"""
EVM (Earned Value Management) calculation engine.
All math lives here — the agent tools call these functions.
Nothing in this module talks to the LLM.
"""
from __future__ import annotations
import statistics
from dataclasses import dataclass

# ── EAC methods ────────────────────────────────────────────────────────────────

def eac_cpi(bac: float, ev: float, ac: float) -> float:
    """EAC = BAC / CPI.  Assumes current cost performance continues."""
    cpi = ev / ac if ac else 1.0
    return bac / cpi if cpi else bac

def eac_remaining_at_budget(bac: float, ev: float, ac: float) -> float:
    """EAC = AC + (BAC - EV).  Assumes future work performed exactly at budget."""
    return ac + (bac - ev)

def eac_composite(bac: float, ev: float, ac: float, spi: float) -> float:
    """EAC = AC + (BAC - EV) / (CPI × SPI).  Composite — accounts for schedule impact on cost."""
    cpi = ev / ac if ac else 1.0
    denominator = cpi * spi if (cpi * spi) > 0 else 1.0
    return ac + (bac - ev) / denominator

def tcpi_bac(bac: float, ev: float, ac: float) -> float:
    """TCPI = (BAC - EV) / (BAC - AC).  Performance needed to finish at original budget."""
    denom = bac - ac
    return (bac - ev) / denom if denom > 0 else 999.0

def tcpi_eac(bac: float, ev: float, ac: float, eac: float) -> float:
    """TCPI = (BAC - EV) / (EAC - AC).  Performance needed to finish at projected EAC."""
    denom = eac - ac
    return (bac - ev) / denom if denom > 0 else 999.0

def vac(bac: float, eac: float) -> float:
    """Variance at Completion = BAC - EAC.  Negative = overrun."""
    return bac - eac


# ── Trend analysis ─────────────────────────────────────────────────────────────

@dataclass
class TrendResult:
    direction: str       # DEGRADING | IMPROVING | STABLE | VOLATILE
    consecutive: int     # consecutive periods in current direction
    magnitude: float     # total change over last 6 periods (or all if <6)
    is_structural: bool  # True if 3+ consecutive same-direction moves
    avg_change_per_period: float
    note: str


def analyse_cpi_trend(cpi_history: list) -> TrendResult:
    """
    Classify the CPI trend from a list of cumulative CPI values.
    Structural = 3+ consecutive periods moving in same direction.
    """
    n = len(cpi_history)
    if n < 2:
        return TrendResult("INSUFFICIENT_DATA", 0, 0.0, False, 0.0,
                           f"Only {n} period(s) — cannot assess trend.")

    deltas = [cpi_history[i] - cpi_history[i-1] for i in range(1, n)]

    # Consecutive streak in most recent direction
    last_sign = 1 if deltas[-1] >= 0 else -1
    streak = 0
    for d in reversed(deltas):
        if (d >= 0 and last_sign == 1) or (d < 0 and last_sign == -1):
            streak += 1
        else:
            break

    # Direction
    window = cpi_history[-6:] if n >= 6 else cpi_history
    total_change = window[-1] - window[0]

    if streak >= 3 and total_change < -0.03:
        direction = "DEGRADING"
        is_structural = True
    elif streak >= 3 and total_change > 0.03:
        direction = "IMPROVING"
        is_structural = True
    elif abs(total_change) <= 0.015:
        direction = "STABLE"
        is_structural = False
    else:
        direction = "VOLATILE"
        is_structural = False

    avg_chg = total_change / (len(window) - 1) if len(window) > 1 else 0

    note = (
        f"CPI moved from {window[0]:.3f} to {window[-1]:.3f} over "
        f"{len(window)} periods ({total_change:+.3f} total). "
        f"Current streak: {streak} consecutive {'drops' if last_sign == -1 else 'increases'}."
    )
    return TrendResult(direction, streak, total_change, is_structural, avg_chg, note)


def detect_step_change(cpi_history: list, threshold: float = 0.05) -> dict | None:
    """
    Detect a sudden step change (event-driven, not gradual).
    Returns info about the largest single-period jump if > threshold.
    """
    if len(cpi_history) < 2:
        return None
    # i is 1-indexed period index; pre = cpi[i-1], post = cpi[i]
    deltas = [(i, cpi_history[i] - cpi_history[i-1])
              for i in range(1, len(cpi_history))]
    worst_period, worst_delta = min(deltas, key=lambda x: x[1])
    if abs(worst_delta) >= threshold:
        pre  = cpi_history[worst_period - 1]
        post = cpi_history[worst_period]
        return {
            "at_period": worst_period + 1,  # 1-indexed
            "delta":     round(worst_delta, 3),
            "pre_cpi":   round(pre, 3),
            "post_cpi":  round(post, 3),
            "note": f"Step change of {worst_delta:+.3f} detected at period {worst_period+1} "
                    f"(CPI {pre:.3f} -> {post:.3f}). Likely a discrete event, not gradual deterioration.",
        }
    return None


# ── Risk scoring ───────────────────────────────────────────────────────────────

def compute_risk_score(
    cpi: float,
    spi: float,
    pct_complete: float,
    contingency_pct_consumed: float,
    cpi_trend: TrendResult,
    has_rebaseline: bool,
) -> tuple[float, str]:
    """
    Composite risk score 0–100 + risk level label.
    Weights:
      CPI performance        : 30
      SPI performance        : 15
      Project maturity adj   : 15  (late-stage overrun is more certain)
      Contingency burn        : 20
      Trend direction         : 15
      Rebaseline flag         :  5
    """
    # CPI score (0–30): perfect CPI=1.0 → 0, CPI=0.70 → 30
    cpi_score = max(0.0, min(30.0, (1.0 - cpi) * 100.0))

    # SPI score (0–15)
    spi_score = max(0.0, min(15.0, (1.0 - spi) * 50.0))

    # Maturity adjustment (0–15): late-stage bad CPI is more certain
    maturity = pct_complete / 100.0
    if maturity >= 0.6 and cpi < 0.95:
        maturity_score = min(15.0, (0.6 - cpi + 0.4) * maturity * 20.0)
    else:
        maturity_score = 0.0

    # Contingency burn (0–20)
    cont_score = min(20.0, (contingency_pct_consumed / 100.0) ** 2 * 30.0)

    # Trend score (0–15)
    if cpi_trend.is_structural and cpi_trend.direction == "DEGRADING":
        trend_score = min(15.0, cpi_trend.consecutive * 2.5)
    elif cpi_trend.direction == "DEGRADING":
        trend_score = 5.0
    elif cpi_trend.direction == "IMPROVING":
        trend_score = -5.0
    else:
        trend_score = 0.0

    # Rebaseline flag (0–5)
    rb_score = 5.0 if has_rebaseline else 0.0

    total = cpi_score + spi_score + maturity_score + cont_score + trend_score + rb_score
    total = max(0.0, min(100.0, total))

    if total >= 55:   level = "CRITICAL"
    elif total >= 38: level = "HIGH"
    elif total >= 22: level = "MEDIUM"
    elif total >= 10: level = "LOW"
    else:             level = "HEALTHY"

    return round(total, 1), level


# ── EAC scenario recommendation ───────────────────────────────────────────────

def recommend_eac_method(pct_complete: float, cpi_trend: TrendResult,
                          has_step_change: bool) -> str:
    """
    Choose the most appropriate EAC method based on project state.
    Returns method name and rationale.
    """
    maturity = pct_complete / 100.0

    if has_step_change:
        return ("composite",
                f"Step-change event detected. CPI-only method overstates the impact of a "
                f"discrete event; composite (CPI×SPI) better accounts for both cost and "
                f"schedule effects.")

    if maturity < 0.25:
        return ("at_budget",
                f"Project is only {pct_complete:.0f}% complete — CPI is unreliable at this stage. "
                f"EAC at budget for remaining work is the most defensible estimate.")

    if maturity >= 0.6 and cpi_trend.is_structural and cpi_trend.direction == "DEGRADING":
        return ("cpi",
                f"Project is {pct_complete:.0f}% complete with a structural degrading CPI trend "
                f"({cpi_trend.consecutive} consecutive periods). Past performance is the best "
                f"predictor of future performance at this stage — CPI method recommended.")

    if cpi_trend.direction == "STABLE":
        return ("cpi",
                f"CPI has been stable ({cpi_trend.note}). CPI-based EAC is appropriate.")

    return ("composite",
            f"Mixed signals ({cpi_trend.direction} trend, {pct_complete:.0f}% complete). "
            f"Composite method (CPI×SPI) provides a balanced estimate.")
