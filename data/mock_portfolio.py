"""
NIG Project Portfolio — Mock Data
20 infrastructure/construction projects with realistic EVM scenarios.
Scenarios are designed to expose the hard parts of EAC forecasting:
  1. Structural CPI degradation vs early-phase instability
  2. Rebaseline masking (project looks green after BAC increase)
  3. WBS-level disaster hidden behind project-level CPI
  4. Schedule-cost correlation (SPI decline → future cost spike)
  5. Contingency exhaustion (no buffer left mid-project)
  6. Step-change event (site discovery, sudden cost jump)
  7. Near-completion lock-in (overrun is baked in, no recovery)

Ground truth final costs are embedded — used by the evaluator to score
the agent's risk ranking and EAC estimates.
"""
from __future__ import annotations
import math

# ── S-curve: logistic planned progress ────────────────────────────────────────

def _s(t: int, n: int, k: float = 5.5) -> float:
    if t <= 0: return 0.0
    if t >= n: return 1.0
    return 1.0 / (1.0 + math.exp(-k * (t / n - 0.5)))


# ── Period builder ─────────────────────────────────────────────────────────────

def _build_periods(
    bac_original: float,
    duration: int,
    cpi_series: list,
    spi_series: list,
    rebaseline: dict | None = None,
) -> list:
    """
    Build period-by-period EVM records from CPI/SPI trajectories.
    Rebaseline: {'at': period_int, 'new_bac': float, 'reason': str}
    """
    periods = []
    bac = bac_original
    for t in range(1, len(cpi_series) + 1):
        is_rebaseline = rebaseline is not None and t == rebaseline["at"]
        if is_rebaseline:
            bac = rebaseline["new_bac"]

        planned_pct = _s(t, duration)
        cpi = cpi_series[t - 1]
        spi = spi_series[t - 1]
        actual_pct  = planned_pct * spi
        pv  = round(planned_pct * bac)
        ev  = round(actual_pct  * bac)
        ac  = round(ev / cpi) if cpi > 0 else 0

        periods.append({
            "period":       t,
            "bac":          bac,
            "pv":           pv,
            "ev":           ev,
            "ac":           ac,
            "cpi":          round(cpi, 3),
            "spi":          round(spi, 3),
            "pct_complete": round(actual_pct * 100, 1),
            "rebaselined":  is_rebaseline,
        })
    return periods


# ── WBS allocations (% of BAC) ─────────────────────────────────────────────────

WBS_NAMES = [
    "Project Management",
    "Engineering & Design",
    "Procurement",
    "Civil & Structural",
    "Mechanical & Electrical",
    "Testing & Commissioning",
    "HSE & Compliance",
    "Contingency",
]
WBS_ALLOC = {
    "Project Management":       0.050,
    "Engineering & Design":     0.120,
    "Procurement":              0.280,
    "Civil & Structural":       0.220,
    "Mechanical & Electrical":  0.175,
    "Testing & Commissioning":  0.080,
    "HSE & Compliance":         0.040,
    "Contingency":              0.035,
}


def _build_wbs(bac: float, ev_total: float, ac_total: float,
               wbs_cpi_overrides: dict | None = None) -> list:
    """
    Build WBS snapshot.  Override elements get their explicit CPI.
    Remaining elements share a residual CPI so sum(AC) == ac_total.
    """
    overrides = wbs_cpi_overrides or {}
    override_ev, override_ac = 0.0, 0.0
    rows = []

    for name in WBS_NAMES:
        alloc = WBS_ALLOC[name]
        wbs_bac = alloc * bac
        wbs_ev  = alloc * ev_total

        if name in overrides and name != "Contingency":
            cpi    = overrides[name]
            wbs_ac = wbs_ev / cpi
            override_ev += wbs_ev
            override_ac += wbs_ac
            rows.append({"name": name, "bac": wbs_bac, "ev": wbs_ev, "ac": wbs_ac,
                         "cpi": cpi, "_override": True})
        else:
            rows.append({"name": name, "bac": wbs_bac, "ev": wbs_ev,
                         "_override": False})

    residual_ev  = ev_total  - override_ev
    residual_ac  = ac_total  - override_ac
    residual_cpi = residual_ev / residual_ac if residual_ac > 0 else 1.0

    final = []
    for r in rows:
        if r["_override"]:
            final.append({
                "wbs": r["name"],
                "bac": round(r["bac"]),
                "ev":  round(r["ev"]),
                "ac":  round(r["ac"]),
                "cpi": round(r["cpi"], 3),
                "pct_complete": round(r["ev"] / r["bac"] * 100, 1) if r["bac"] else 0,
            })
        else:
            wbs_ev = r["ev"]
            wbs_ac = wbs_ev / residual_cpi if residual_cpi > 0 else wbs_ev
            final.append({
                "wbs": r["name"],
                "bac": round(r["bac"]),
                "ev":  round(wbs_ev),
                "ac":  round(wbs_ac),
                "cpi": round(residual_cpi, 3),
                "pct_complete": round(wbs_ev / r["bac"] * 100, 1) if r["bac"] else 0,
            })
    return final


# ── Raw project configs ────────────────────────────────────────────────────────
# Notation: bac in USD, duration in months, current_period = last completed period.
# Ground truth final_cost drives the evaluation — it's what the project "actually" cost.

_CONFIGS = [
    # ── CRITICAL PROJECTS ─────────────────────────────────────────────────────

    {   # P01 — Structural CPI degradation
        # Hard part: decline is gradual; any single period looks "just slightly worse".
        # Agent must detect the 8-period consecutive drop pattern, not just current value.
        "id": "P01", "name": "North Sea Platform Upgrade",
        "type": "Offshore", "region": "Europe",
        "bac": 45_200_000, "duration": 24, "current_period": 14,
        "scenario": "Structural CPI degradation over 8 consecutive periods driven by "
                    "North Sea weather delays and rework on Civil & Structural scope.",
        "cpi_series": [0.970,0.963,0.955,0.946,0.934,0.919,0.902,0.884,0.867,0.851,0.838,0.829,0.822,0.820],
        "spi_series": [0.990,0.985,0.979,0.973,0.966,0.958,0.950,0.942,0.934,0.926,0.919,0.913,0.907,0.903],
        "rebaseline": None,
        "wbs_cpi_overrides": {"Civil & Structural": 0.71},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.72},
        "ground_truth": {"final_cost": 56_800_000},  # +25.7% vs BAC
    },
    {   # P02 — Rebaseline masking
        # Hard part: post-rebaseline CPI looks healthy (0.94) but the project is
        # reproducing the same deterioration pattern on the new baseline.
        # Agent must look at pre-rebaseline history and AC growth rate, not just current CPI.
        "id": "P02", "name": "Dubai Metro Extension",
        "type": "Rail", "region": "Middle East",
        "bac": 105_000_000, "duration": 36, "current_period": 18,
        "scenario": "BAC rebaselined P12→P13: $105M→$120M absorbing prior overrun. "
                    "Post-rebaseline metrics appear healthy; same deterioration pattern resuming.",
        "cpi_series": [
            # P1–P12 pre-rebaseline: steady deterioration to 0.79
            0.976,0.958,0.938,0.917,0.896,0.875,0.854,0.833,0.815,0.800,0.789,0.790,
            # P13–P18 post-rebaseline: apparent reset then gradual decline starting again
            0.960,0.955,0.949,0.943,0.937,0.931,
        ],
        "spi_series": [
            0.986,0.974,0.963,0.951,0.939,0.926,0.913,0.900,0.888,0.877,0.867,0.860,
            0.982,0.978,0.974,0.969,0.964,0.959,
        ],
        "rebaseline": {"at": 13, "new_bac": 120_000_000,
                       "reason": "Scope increase: additional 3 stations added; preliminary cost absorbed"},
        "wbs_cpi_overrides": {"Civil & Structural": 0.85, "Procurement": 0.91},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.88},
        "ground_truth": {"final_cost": 140_200_000},  # +33.5% vs original $105M; +16.8% vs new $120M
    },
    {   # P06 — WBS-level disaster hidden at project level
        # Hard part: project CPI 0.93 looks "concerning but manageable".
        # Civil & Structural WBS at 0.61 is catastrophic (foundation issues, soil conditions).
        # M&E WBS at 1.08 compensates at project level.
        # Only WBS drill-down reveals the true picture.
        "id": "P06", "name": "Cairo Power Station",
        "type": "Energy", "region": "Middle East",
        "bac": 95_000_000, "duration": 30, "current_period": 15,
        "scenario": "Project-level CPI 0.93 masks a catastrophic Civil & Structural WBS "
                    "(CPI 0.61) due to unexpected soil conditions. M&E is ahead of budget "
                    "and partially offsets. Without WBS drill-down this project appears moderate risk.",
        "cpi_series": [0.995,0.990,0.983,0.974,0.963,0.950,0.935,0.920,0.908,0.897,0.929,0.938,0.940,0.936,0.930],
        "spi_series": [0.998,0.996,0.994,0.991,0.988,0.985,0.981,0.977,0.973,0.970,0.968,0.966,0.964,0.963,0.961],
        "rebaseline": None,
        "wbs_cpi_overrides": {"Civil & Structural": 0.61, "Mechanical & Electrical": 1.08},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.68},
        "ground_truth": {"final_cost": 112_100_000},  # +18.0%
    },
    {   # P07 — Schedule-cost correlation (cost impact not yet visible in actuals)
        # Hard part: CPI is 1.01 (on budget). But SPI is 0.82 (significantly behind schedule).
        # The contractor is now on an acceleration programme. Premium rates not yet invoiced.
        # Contingency burn at 75% confirms the hidden pressure.
        "id": "P07", "name": "Manchester Roads Programme",
        "type": "Civil", "region": "Europe",
        "bac": 22_000_000, "duration": 20, "current_period": 12,
        "scenario": "SPI degradation to 0.82 with CPI still 1.01 — classic leading indicator "
                    "of imminent cost overrun. Contractor on acceleration (premium rates unpaid). "
                    "Contingency 75% consumed at 60% complete. Cost impact 2-3 periods out.",
        "cpi_series": [1.010,1.008,1.006,1.004,1.005,1.003,1.002,1.004,1.006,1.008,1.009,1.010],
        "spi_series": [0.992,0.985,0.977,0.968,0.958,0.946,0.934,0.921,0.908,0.895,0.882,0.820],
        "rebaseline": None,
        "wbs_cpi_overrides": {"Civil & Structural": 1.02, "Testing & Commissioning": 0.94},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.75},
        "ground_truth": {"final_cost": 26_100_000},  # +18.6%
    },
    {   # P08 — Contingency exhausted from scope growth (regulatory change)
        # Hard part: CPI is 0.97 (looks fine). But contingency is 91% consumed at 58% complete.
        # A new safety regulation required 2 extra systems mid-project.
        # Any further cost variance has no buffer.
        "id": "P08", "name": "Singapore LNG Terminal",
        "type": "Industrial", "region": "Asia-Pacific",
        "bac": 67_000_000, "duration": 24, "current_period": 14,
        "scenario": "Scope growth from mid-project regulatory change (2 new safety systems). "
                    "CPI 0.97 appears healthy but contingency is 91% consumed at 58% complete. "
                    "No buffer for any remaining risk events.",
        "cpi_series": [0.993,0.987,0.982,0.976,0.971,0.966,0.962,0.959,0.957,0.956,0.958,0.962,0.967,0.970],
        "spi_series": [0.999,0.998,0.997,0.996,0.995,0.994,0.993,0.991,0.989,0.987,0.985,0.983,0.981,0.979],
        "rebaseline": None,
        "wbs_cpi_overrides": {"Procurement": 0.94},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.91},
        "ground_truth": {"final_cost": 76_200_000},  # +13.7%
    },
    {   # P10 — Multiple compounding signals (most critical in portfolio)
        # Hard part: every metric is bad but in different ways.
        # CPI 0.79 AND SPI 0.86 AND contingency 88% consumed.
        # Structural: CPI has dropped each of last 6 periods.
        # Two WBS elements failing simultaneously.
        "id": "P10", "name": "Mumbai Port Expansion",
        "type": "Marine", "region": "Asia-Pacific",
        "bac": 55_000_000, "duration": 28, "current_period": 16,
        "scenario": "Portfolio's most critical project. Structural CPI decline for 8 periods "
                    "(now 0.79). SPI 0.86. Procurement (0.72) and Civil (0.81) both failing. "
                    "Contingency 88% consumed. Compounding supply chain and labour issues.",
        "cpi_series": [0.984,0.972,0.958,0.942,0.925,0.906,0.885,0.863,0.842,0.820,0.800,0.786,0.793,0.791,0.789,0.793],
        "spi_series": [0.978,0.968,0.956,0.943,0.929,0.915,0.901,0.887,0.873,0.861,0.850,0.860,0.858,0.856,0.860,0.862],
        "rebaseline": None,
        "wbs_cpi_overrides": {"Procurement": 0.72, "Civil & Structural": 0.81},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.88},
        "ground_truth": {"final_cost": 71_900_000},  # +30.7%
    },
    {   # P13 — Contingency nearly exhausted, CPI looks OK
        # Hard part: CPI 0.94 is concerning but not alarming. The real flag is
        # contingency at 97% consumed with 40% of project remaining.
        # Any single cost event will cause an immediate overrun with no buffer.
        "id": "P13", "name": "Riyadh Hospital Complex",
        "type": "Healthcare", "region": "Middle East",
        "bac": 72_000_000, "duration": 32, "current_period": 20,
        "scenario": "CPI 0.94 — concerning but not critical in isolation. The real risk: "
                    "contingency is 97% consumed at 60% complete. M&E complexity was "
                    "significantly underestimated. Zero buffer for remaining 40% of scope.",
        "cpi_series": [0.994,0.990,0.985,0.979,0.972,0.964,0.956,0.947,0.940,0.934,
                       0.942,0.944,0.946,0.945,0.943,0.941,0.940,0.939,0.940,0.940],
        "spi_series": [0.997,0.995,0.992,0.989,0.986,0.982,0.978,0.974,0.970,0.967,
                       0.965,0.963,0.962,0.961,0.960,0.959,0.958,0.957,0.956,0.955],
        "rebaseline": None,
        "wbs_cpi_overrides": {"Mechanical & Electrical": 0.79},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.97},
        "ground_truth": {"final_cost": 80_400_000},  # +11.7%
    },
    {   # P17 — Largest absolute dollar exposure
        # Hard part: CPI 0.76 is obviously bad. But the agent must also note:
        # $26M exposure on an $83M project is the largest $ risk in the entire portfolio,
        # even though % variance is similar to P01.
        "id": "P17", "name": "Lagos Pipeline",
        "type": "Energy", "region": "Africa",
        "bac": 83_000_000, "duration": 36, "current_period": 20,
        "scenario": "Largest dollar exposure in portfolio: ~$27M overrun projected. "
                    "Structural CPI decline for 12 periods to 0.76. Terrain challenges "
                    "and FX impact on procurement. Contingency fully exhausted.",
        "cpi_series": [0.979,0.963,0.944,0.922,0.898,0.873,0.846,0.819,0.792,0.768,
                       0.752,0.743,0.755,0.762,0.766,0.763,0.758,0.756,0.760,0.762],
        "spi_series": [0.975,0.963,0.950,0.936,0.921,0.906,0.890,0.875,0.861,0.849,
                       0.838,0.839,0.842,0.845,0.848,0.846,0.843,0.841,0.840,0.841],
        "rebaseline": None,
        "wbs_cpi_overrides": {"Civil & Structural": 0.65, "Procurement": 0.72},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 1.00},
        "ground_truth": {"final_cost": 110_500_000},  # +33.1%
    },
    {   # P18 — Step-change event (site discovery at P8)
        # Hard part: pattern is NOT a gradual decline (not structural in the classic sense).
        # CPI was 0.98 for 7 periods, then dropped sharply to 0.85 at P8.
        # The agent must distinguish this from structural degradation and identify P8 as an event.
        "id": "P18", "name": "Vancouver Transit Hub",
        "type": "Civil", "region": "North America",
        "bac": 48_000_000, "duration": 24, "current_period": 10,
        "scenario": "Step-change event at P8: unexpected contaminated soil discovered. "
                    "CPI was stable at 0.98 for 7 periods then dropped sharply to 0.85. "
                    "Remediation costs ongoing. Not a gradual deterioration — a discrete event.",
        "cpi_series": [0.983,0.980,0.978,0.976,0.975,0.977,0.979,0.851,0.845,0.848],
        "spi_series": [0.997,0.996,0.994,0.992,0.991,0.990,0.989,0.970,0.965,0.963],
        "rebaseline": None,
        "wbs_cpi_overrides": {"Civil & Structural": 0.72},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.58},
        "ground_truth": {"final_cost": 56_300_000},  # +17.3%
    },

    # ── WATCH / LOW RISK ──────────────────────────────────────────────────────

    {   # P03 — Genuinely healthy; should NOT be flagged
        "id": "P03", "name": "Sydney Water Treatment Plant",
        "type": "Civil", "region": "Asia-Pacific",
        "bac": 28_400_000, "duration": 18, "current_period": 11,
        "scenario": "Healthy project. No anomalies.",
        "cpi_series": [0.995,1.002,0.998,0.996,1.001,0.997,0.994,0.999,1.002,0.998,0.995],
        "spi_series": [1.000,1.001,0.999,1.000,1.001,1.002,0.999,1.001,1.000,0.998,0.997],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.31},
        "ground_truth": {"final_cost": 28_700_000},  # +1.1%
    },
    {   # P04 — Near completion with baked-in minor overrun
        "id": "P04", "name": "Houston Refinery Turnaround",
        "type": "Industrial", "region": "North America",
        "bac": 18_500_000, "duration": 12, "current_period": 10,
        "scenario": "85% complete with CPI 0.91 — overrun is baked in but project is nearly done. "
                    "No recovery path at this stage.",
        "cpi_series": [0.972,0.958,0.945,0.933,0.922,0.913,0.908,0.906,0.908,0.910],
        "spi_series": [0.998,0.997,0.996,0.995,0.994,0.993,0.992,0.991,0.991,0.992],
        "rebaseline": None, "wbs_cpi_overrides": {"Procurement": 0.88},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.82},
        "ground_truth": {"final_cost": 20_300_000},  # +9.7% — just under 10%
    },
    {   # P05 — Early phase instability; NOT structural
        "id": "P05", "name": "Kuala Lumpur Tower Fitout",
        "type": "Commercial", "region": "Asia-Pacific",
        "bac": 8_200_000, "duration": 10, "current_period": 2,
        "scenario": "Early phase (18% complete). CPI 0.88 this period but only 2 data points. "
                    "Early-phase CPI instability is normal — insufficient data for structural call.",
        "cpi_series": [0.920, 0.881],
        "spi_series": [0.972, 0.965],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.08},
        "ground_truth": {"final_cost": 8_500_000},  # +3.7%
    },
    {   # P09 — Healthy with minor schedule slip
        "id": "P09", "name": "Berlin Office Development",
        "type": "Commercial", "region": "Europe",
        "bac": 14_000_000, "duration": 16, "current_period": 9,
        "scenario": "Minor schedule slip (SPI 0.94) but cost performance solid. Not material.",
        "cpi_series": [0.996,0.995,0.993,0.990,0.989,0.988,0.987,0.986,0.984],
        "spi_series": [0.997,0.993,0.988,0.982,0.975,0.968,0.961,0.955,0.943],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.29},
        "ground_truth": {"final_cost": 14_200_000},  # +1.4%
    },
    {   # P11 — Early phase, CPI volatile but not alarming
        "id": "P11", "name": "Oslo Wind Farm",
        "type": "Energy", "region": "Europe",
        "bac": 38_000_000, "duration": 22, "current_period": 5,
        "scenario": "Early phase (20% complete). CPI fluctuating 0.91–1.03. "
                    "Normal early-phase variance. Watch category only.",
        "cpi_series": [1.025, 0.955, 1.012, 0.940, 1.018],
        "spi_series": [1.002, 0.997, 1.001, 0.998, 0.994],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.12},
        "ground_truth": {"final_cost": 38_600_000},  # +1.6%
    },
    {   # P12 — Was struggling early, now recovering
        "id": "P12", "name": "Toronto Highway Widening",
        "type": "Civil", "region": "North America",
        "bac": 31_000_000, "duration": 18, "current_period": 14,
        "scenario": "Early problems (CPI dipped to 0.88 at P5) now recovered to 0.96. "
                    "Positive trend — agent should note the recovery pattern.",
        "cpi_series": [0.968,0.940,0.910,0.890,0.882,0.889,0.901,0.912,0.921,0.930,0.940,0.950,0.956,0.960],
        "spi_series": [0.991,0.984,0.976,0.968,0.960,0.955,0.952,0.950,0.949,0.950,0.951,0.953,0.954,0.955],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.61},
        "ground_truth": {"final_cost": 32_100_000},  # +3.5%
    },
    {   # P14 — Ahead of schedule and budget
        "id": "P14", "name": "Perth Mining Facility",
        "type": "Mining", "region": "Asia-Pacific",
        "bac": 44_000_000, "duration": 20, "current_period": 12,
        "scenario": "Performing well. CPI 1.03, SPI 1.05. Should NOT be flagged.",
        "cpi_series": [1.018,1.022,1.025,1.028,1.031,1.034,1.033,1.031,1.029,1.028,1.027,1.028],
        "spi_series": [1.012,1.018,1.023,1.028,1.032,1.035,1.038,1.040,1.042,1.043,1.044,1.045],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.18},
        "ground_truth": {"final_cost": 42_700_000},  # -3.0% (under budget)
    },
    {   # P15 — Rebaseline at P6: BAC $16M → $19M; new metrics look clean
        "id": "P15", "name": "Cape Town Desalination Plant",
        "type": "Civil", "region": "Africa",
        "bac": 16_000_000, "duration": 15, "current_period": 8,
        "scenario": "Rebaselined at P6 ($16M→$19M). Pre-rebaseline CPI was 0.78. "
                    "Post-rebaseline CPI appears clean (0.97) but should be questioned.",
        "cpi_series": [
            # P1–P5 pre-rebaseline: deteriorating
            0.952, 0.920, 0.890, 0.853, 0.813,
            # P6 rebaseline applied (period 6 marks the change), P7–P8 post
            0.812, 0.975, 0.971,
        ],
        "spi_series": [
            0.980, 0.965, 0.950, 0.935, 0.920,
            0.920, 0.980, 0.976,
        ],
        "rebaseline": {"at": 7, "new_bac": 19_000_000,
                       "reason": "Scope increase: additional membrane filtration units added"},
        "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.70},
        "ground_truth": {"final_cost": 19_800_000},  # +4.2% vs new $19M
    },
    {   # P16 — Small, healthy project
        "id": "P16", "name": "Amsterdam Data Centre Fit-Out",
        "type": "IT Infrastructure", "region": "Europe",
        "bac": 11_000_000, "duration": 12, "current_period": 7,
        "scenario": "Minor cost variance. On schedule. Not material.",
        "cpi_series": [0.988,0.982,0.977,0.974,0.971,0.970,0.968],
        "spi_series": [0.999,0.998,0.997,0.996,0.995,0.994,0.993],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.33},
        "ground_truth": {"final_cost": 11_400_000},  # +3.6%
    },
    {   # P19 — Large, healthy flagship project
        "id": "P19", "name": "Doha Airport Terminal Expansion",
        "type": "Aviation", "region": "Middle East",
        "bac": 135_000_000, "duration": 40, "current_period": 22,
        "scenario": "Large flagship project tracking well. CPI 1.01, SPI 0.98. "
                    "Should NOT dominate agent attention despite large BAC.",
        "cpi_series": [1.008,1.010,1.010,1.009,1.008,1.006,1.006,1.007,1.008,1.009,
                       1.010,1.010,1.009,1.008,1.007,1.006,1.007,1.008,1.010,1.011,
                       1.010,1.009],
        "spi_series": [0.999,0.998,0.997,0.996,0.995,0.994,0.993,0.992,0.991,0.990,
                       0.989,0.988,0.987,0.986,0.985,0.984,0.983,0.982,0.981,0.980,
                       0.980,0.980],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.22},
        "ground_truth": {"final_cost": 133_700_000},  # -1.0% (under budget)
    },
    {   # P20 — Nearly complete, minor overrun locked in
        "id": "P20", "name": "Bucharest Water Network Upgrade",
        "type": "Civil", "region": "Europe",
        "bac": 16_000_000, "duration": 14, "current_period": 13,
        "scenario": "90% complete. CPI 0.95 — small overrun locked in but project nearly done. "
                    "Not material in portfolio context.",
        "cpi_series": [0.980,0.970,0.962,0.957,0.955,0.954,0.953,0.952,0.952,0.953,0.953,0.952,0.950],
        "spi_series": [0.999,0.998,0.997,0.996,0.995,0.994,0.994,0.994,0.993,0.993,0.993,0.993,0.992],
        "rebaseline": None, "wbs_cpi_overrides": {},
        "contingency": {"budget_pct": 0.035, "consumed_pct": 0.74},
        "ground_truth": {"final_cost": 16_800_000},  # +5.0%
    },
]

# Projects that end up >10% over their original BAC (evaluation ground truth)
OVERRUN_PROJECT_IDS = {"P01", "P02", "P06", "P07", "P08", "P10", "P13", "P17", "P18"}


# ── Portfolio builder ──────────────────────────────────────────────────────────

def build_portfolio(as_of_period: int | None = None) -> dict:
    """
    Build the full portfolio snapshot.
    as_of_period: simulate having data only through this period (for back-testing).
                  None = use each project's current_period.
    Returns dict keyed by project_id.
    """
    portfolio = {}
    for cfg in _CONFIGS:
        pid  = cfg["id"]
        bac  = cfg["bac"]
        dur  = cfg["duration"]
        cpi_full = cfg["cpi_series"]
        spi_full = cfg["spi_series"]
        cp   = cfg["current_period"]

        # For back-testing, cap at as_of_period
        if as_of_period is not None:
            n = min(cp, as_of_period)
        else:
            n = cp

        if n <= 0:
            continue  # project hasn't started yet at this as-of period

        cpi_trimmed = cpi_full[:n]
        spi_trimmed = spi_full[:n]

        # Adjust rebaseline — only apply if it happened within the trimmed window
        rb = cfg["rebaseline"]
        if rb and rb["at"] > n:
            rb = None  # rebaseline hasn't happened yet

        periods = _build_periods(bac, dur, cpi_trimmed, spi_trimmed, rb)
        current = periods[-1]
        current_bac = current["bac"]

        # WBS snapshot (current period)
        wbs = _build_wbs(current_bac, current["ev"], current["ac"],
                         cfg["wbs_cpi_overrides"])

        # Contingency snapshot
        cont_budget  = cfg["contingency"]["budget_pct"] * current_bac
        cont_consumed_pct = cfg["contingency"]["consumed_pct"]
        # Scale consumed_pct by how far through the project we are
        progress_ratio = n / cp if cp > 0 else 1.0
        scaled_consumed = min(1.0, cont_consumed_pct * progress_ratio)
        cont_consumed = cont_budget * scaled_consumed
        cont_remaining = max(0.0, cont_budget - cont_consumed)

        portfolio[pid] = {
            "meta": {
                "id":       pid,
                "name":     cfg["name"],
                "type":     cfg["type"],
                "region":   cfg["region"],
                "scenario": cfg["scenario"],
                "bac_original": bac,
                "duration": dur,
            },
            "current_period":  n,
            "total_periods":   dur,
            "bac":             current_bac,
            "pv":              current["pv"],
            "ev":              current["ev"],
            "ac":              current["ac"],
            "cpi":             current["cpi"],
            "spi":             current["spi"],
            "pct_complete":    current["pct_complete"],
            "periods":         periods,
            "wbs":             wbs,
            "contingency": {
                "budget":          round(cont_budget),
                "consumed":        round(cont_consumed),
                "remaining":       round(cont_remaining),
                "pct_consumed":    round(scaled_consumed * 100, 1),
                "expected_pct_at_this_stage": round(current["pct_complete"] / 100 * 100, 1),
            },
            "rebaseline_events": [
                {**cfg["rebaseline"], "original_bac": bac}
            ] if (rb and cfg["rebaseline"]) else [],
            "ground_truth": cfg["ground_truth"],
        }
    return portfolio


# ── Monthly run cadence ───────────────────────────────────────────────────────
# We treat each EVM period as one calendar month.
# The portfolio programme started October 2023.
# "Current" run is Period 14 = November 2024.
# Back-test runs cover the prior 5 months.

PROGRAMME_START = "Oct 2023"
CURRENT_PERIOD  = 14   # the "live" period used for the main monthly run

# Maps period number → human-readable month label
_MONTH_LABELS = {
    1:  "Oct 2023",
    2:  "Nov 2023",
    3:  "Dec 2023",
    4:  "Jan 2024",
    5:  "Feb 2024",
    6:  "Mar 2024",
    7:  "Apr 2024",
    8:  "May 2024",
    9:  "Jun 2024",
    10: "Jul 2024",
    11: "Aug 2024",
    12: "Sep 2024",
    13: "Oct 2024",
    14: "Nov 2024",   # ← current
    15: "Dec 2024",
    16: "Jan 2025",
    17: "Feb 2025",
    18: "Mar 2025",
    19: "Apr 2025",
    20: "May 2025",
    21: "Jun 2025",
    22: "Jul 2025",
}

# Monthly runs to show in Track Record (most recent first)
MONTHLY_RUNS = [14, 13, 12, 11, 10, 9]



def period_label(period: int) -> str:
    return _MONTH_LABELS.get(period, f"Period {period}")


# Convenience: default full portfolio
PORTFOLIO = build_portfolio()
