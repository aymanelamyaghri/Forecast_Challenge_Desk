"""
Deterministic tools for the Forecast Challenge Desk.
All numbers come from EVM data + math — the LLM only interprets.
"""
from __future__ import annotations
import json

from data.mock_portfolio import build_portfolio, _MONTH_LABELS
from data.forecast_submissions import SUBMISSIONS, CURRENT_CYCLE, get_submissions_for_period
from data.change_orders import CHANGE_ORDERS, PROJECT_META
from tools.evm_engine import (
    eac_cpi, eac_remaining_at_budget, eac_composite,
    tcpi_bac, analyse_cpi_trend, detect_step_change, recommend_eac_method,
)

_M = lambda v: f"${v/1e6:.1f}M"
_ML = lambda p: _MONTH_LABELS.get(p, f"Period {p}")


def _portfolio(cycle=None):
    return build_portfolio(as_of_period=cycle or CURRENT_CYCLE)


def _subs(cycle=None):
    return get_submissions_for_period(cycle or CURRENT_CYCLE)


def _system_eac(proj):
    bac = proj["bac"]; ev = proj["ev"]; ac = proj["ac"]; spi = proj["spi"]
    cpi_hist = [p["cpi"] for p in proj["periods"]]
    trend = analyse_cpi_trend(cpi_hist)
    step  = detect_step_change(cpi_hist)
    method, _ = recommend_eac_method(proj["pct_complete"], trend, step is not None)
    eac = {"cpi":       eac_cpi(bac, ev, ac),
           "at_budget": eac_remaining_at_budget(bac, ev, ac),
           "composite": eac_composite(bac, ev, ac, spi)}[method]
    return eac, method


def _impl_cpi(pm_eac, ev, ac, bac):
    rem_ev = bac - ev; rem_b = pm_eac - ac
    return round(rem_ev / rem_b, 3) if rem_b > 0 else None


def _signals(proj, sub, pm_eac, sys_eac):
    gap_pct  = (pm_eac - sys_eac) / sys_eac * 100
    cpi_hist = [p["cpi"] for p in proj["periods"]]
    trend = analyse_cpi_trend(cpi_hist)
    step  = detect_step_change(cpi_hist)
    cont_pct = proj["contingency"]["pct_consumed"]
    n_per = len(proj["periods"]); pct = proj["pct_complete"]
    cpi = proj["cpi"]; spi = proj["spi"]

    base = []
    if n_per < 4 or pct < 20:  base.append("EARLY_PHASE")
    if gap_pct < -10:          base.append(f"EAC_GAP_LARGE({gap_pct:.0f}%)")
    elif gap_pct < -5:         base.append(f"EAC_GAP({gap_pct:.0f}%)")
    elif gap_pct < -3:         base.append(f"eac_gap({gap_pct:.0f}%)")
    if cont_pct > 90:          base.append(f"CONTINGENCY_{cont_pct:.0f}%")
    elif cont_pct > 80:        base.append(f"contingency_{cont_pct:.0f}%")
    if trend.is_structural and trend.direction == "DEGRADING":
        base.append(f"STRUCTURAL_DECLINE({trend.consecutive}p)")
    if proj["rebaseline_events"]: base.append("REBASELINED")
    if step:                   base.append(f"STEP_CHANGE(P{step['at_period']})")
    if spi < 0.87:             base.append(f"SPI_LOW({spi:.3f})")

    smart = []
    if cpi > 0.99 and spi < 0.88:
        smart.append(f"SPI_TRAP(CPI:{cpi:.3f}_SPI:{spi:.3f})")
    impl = _impl_cpi(pm_eac, proj["ev"], proj["ac"], proj["bac"])
    if impl and impl > cpi * 1.08:
        rec = (impl / cpi - 1) * 100
        lbl = "NOT_CREDIBLE" if rec > 20 else "UNLIKELY" if rec > 10 else "OPTIMISTIC"
        smart.append(f"IMPLIED_FUTURE_CPI(needs:{impl:.3f}_from:{cpi:.3f}_{lbl})")
    if cont_pct > pct + 20 and pct < 80:
        smart.append(f"CONT_AHEAD({cont_pct:.0f}%_consumed_{pct:.0f}%_done)")
    wbs_c = next((w for w in proj["wbs"] if w["wbs"] == "Civil & Structural"), None)
    if wbs_c and wbs_c["cpi"] < 0.78 and cpi > 0.88:
        smart.append(f"HIDDEN_WBS(Civil:{wbs_c['cpi']:.2f}_masked_by:{cpi:.3f})")
    watch = ["temporary","recovery expected","within approved budget","manageable",
             "no change to eac","challenging but achievable","contingency available","contingency remains"]
    curr = sub["explanation"].lower(); priors = sub.get("prior_explanations", [])
    reps = [f'"{p}"x{sum(1 for e in priors if p in e.lower())+1}'
            for p in watch if p in curr and any(p in e.lower() for e in priors)]
    if reps: smart.append(f"REPEATED_NARRATIVE({', '.join(reps)})")
    return base, smart


# ── Tool 1: Compact portfolio scan ────────────────────────────────────────────

def tool_load_all_summaries(cycle=None):
    """Compact overview of all 20 projects. Call ONCE at start."""
    cycle = cycle or CURRENT_CYCLE
    portfolio = _portfolio(cycle); subs = _subs(cycle)
    month = _ML(cycle)
    lines = [f"PORTFOLIO SCAN -- {month} | 20 projects",
             "!! = suspicious signal -> investigate with get_project_detail | [clean] = quick accept",
             ""]
    for pid, sub in subs.items():
        proj = portfolio.get(pid)
        if not proj: continue
        pm_eac = sub["pm_eac"]; sys_eac, _ = _system_eac(proj)
        base, smart = _signals(proj, sub, pm_eac, sys_eac)
        all_sigs = base + smart
        sig_str = "  !! " + " | ".join(all_sigs) if all_sigs else "  [clean]"
        lines.append(
            f"{pid}  {sub['project_name']:<38} "
            f"CPI:{proj['cpi']:.3f}  SPI:{proj['spi']:.3f}  "
            f"Gap:{(pm_eac-sys_eac)/sys_eac*100:+.0f}%  {proj['pct_complete']:.0f}%done"
        )
        lines.append(sig_str); lines.append("")
    lines += ["PATHS: quick ACCEPT (no !!, gap<3%, CPI>0.97) | quick NEEDS_EVIDENCE (EARLY_PHASE) |",
              "       investigate (any !!) -> get_project_detail -> [get_prior_explanations if REPEATED] -> write_decision",
              "       quick FLAG (EAC_GAP_LARGE + STRUCTURAL_DECLINE both present)",
              "Call write_decision() one project at a time."]
    return "\n".join(lines)


# ── Tool 2: Full project investigation ────────────────────────────────────────

def tool_get_project_detail(project_id, cycle=None):
    """Full investigation for one suspicious project. Call before deciding for any !! project."""
    cycle = cycle or CURRENT_CYCLE
    pid = project_id.upper()
    sub  = _subs(cycle).get(pid)
    proj = _portfolio(cycle).get(pid)
    if not sub or not proj:
        return json.dumps({"error": f"Project {pid} not found."})

    pm_eac = sub["pm_eac"]; sys_eac, method = _system_eac(proj)
    gap = pm_eac - sys_eac; gap_pct = gap / sys_eac * 100
    impl = _impl_cpi(pm_eac, proj["ev"], proj["ac"], proj["bac"])
    cpi = proj["cpi"]; spi = proj["spi"]; pct = proj["pct_complete"]
    bac = proj["bac"]; cont = proj["contingency"]
    cpi_hist = [p["cpi"] for p in proj["periods"]]
    trend = analyse_cpi_trend(cpi_hist); step = detect_step_change(cpi_hist)
    recent_avg = sum(cpi_hist[-3:]) / min(3, len(cpi_hist))
    tcpi_v = tcpi_bac(bac, proj["ev"], proj["ac"])
    rb = proj["rebaseline_events"]

    if impl is None:                                          verdict = "CANNOT_ASSESS"
    elif abs(gap_pct) <= 2 and impl and abs(impl-recent_avg) < 0.05: verdict = "CREDIBLE"
    elif abs(gap_pct) <= 8 and impl and impl < recent_avg*1.10:      verdict = "OPTIMISTIC"
    elif abs(gap_pct) <= 15:                                          verdict = "UNLIKELY"
    else:                                                             verdict = "NOT_CREDIBLE"

    meta = PROJECT_META.get(pid, {})
    cos  = CHANGE_ORDERS.get(pid, [])
    hidden_cos = [c for c in cos if not c["in_eac"] and c["significance"] == "material"]

    lines = [
        f"INVESTIGATION: {pid} -- {sub['project_name']} ({_ML(cycle)})",
        f"  Contract: {meta.get('contract_type','UNKNOWN')} | "
        f"Open risks >$500K: {meta.get('open_risks_above_500k',0)} | "
        f"Contractor: {meta.get('contractor','-')}",
        f"",
        f"EVM SNAPSHOT:",
        f"  BAC {_M(bac)} | AC {_M(proj['ac'])} | EV {_M(proj['ev'])} | {pct:.0f}% complete",
        f"  CPI {cpi:.3f}  SPI {spi:.3f}  Trend: {trend.direction} ({'structural' if trend.is_structural else 'non-structural'})",
        f"  CPI last 3 periods avg: {recent_avg:.3f}",
        f"  Contingency: {cont['pct_consumed']:.0f}% consumed | {_M(cont['remaining'])} remaining",
        f"  Rebaseline: {'YES - ' + rb[0]['reason'] if rb else 'None'}",
        f"",
        f"EAC CREDIBILITY [{verdict}]:",
        f"  PM submitted:         {_M(pm_eac)}",
        f"  System EAC ({method}): {_M(sys_eac)}",
        f"  Gap:                  {gap_pct:+.1f}% ({_M(abs(gap))})",
    ]
    if impl:
        lines.append(f"  Implied future CPI:   {impl:.3f}")
        if impl > cpi:
            rec = (impl / cpi - 1) * 100
            lines.append(f"  Recovery needed:      {rec:.0f}% CPI improvement "
                         f"({'feasible' if rec<8 else 'UNLIKELY' if rec<18 else 'NOT CREDIBLE'})")
    lines += [f"  TCPI to BAC:          {tcpi_v:.3f} ({'feasible' if tcpi_v<1.1 else 'UNREALISTIC'})",
              f"", f"WBS BREAKDOWN:"]
    for w in proj["wbs"]:
        flag = "  <-- CRITICAL" if w["cpi"]<0.75 else ("  <-- concerning" if w["cpi"]<0.90 else "")
        lines.append(f"  {w['wbs']:<32} CPI {w['cpi']:.3f}{flag}")
    # Change order alert
    if hidden_cos:
        lines += [f"", f"CHANGE ORDER ALERT -- {len(hidden_cos)} material CO(s) NOT in PM EAC:"]
        for c in hidden_cos:
            lines.append(f"  [{c['ref']}] {c['desc']} -- ${c['value']/1e6:.1f}M -- {c['status'].upper()}")
        lines.append(f"  -> Call get_change_order_exposure({pid}) to assess full CO exposure")
    elif cos:
        lines.append(f"  Change orders: {len(cos)} on record, all approved/in EAC -- no hidden exposure")

    lines += [f"", f"PM NARRATIVE:", f"  {sub['explanation']}", f"", f"RISK: {sub['risk_note']}"]
    if step: lines += [f"", f"STEP-CHANGE: {step['note']}"]
    priors = sub.get("prior_explanations", [])
    if priors:
        months_back = [f"Period {cycle-2}", f"Period {cycle-1}"]
        lines += [f"", f"PRIOR NARRATIVES:"]
        for i, p in enumerate(priors):
            lbl = months_back[i] if i < len(months_back) else f"Prior {i+1}"
            lines.append(f"  [{lbl}]: {p[:130]}{'...' if len(p)>130 else ''}")
    return "\n".join(lines)


# ── Tool 3: CPI trend history ─────────────────────────────────────────────────

def tool_get_cpi_history(project_id, cycle=None):
    """
    Month-by-month CPI trajectory for one project.
    Use to assess: is this a structural decline or a one-off event?
    """
    cycle = cycle or CURRENT_CYCLE
    pid = project_id.upper()
    proj = _portfolio(cycle).get(pid)
    sub  = _subs(cycle).get(pid)
    if not proj:
        return json.dumps({"error": f"Project {pid} not found."})

    cpi_hist = [p["cpi"] for p in proj["periods"]]
    trend = analyse_cpi_trend(cpi_hist)
    step  = detect_step_change(cpi_hist)

    lines = [f"CPI HISTORY: {pid} -- {sub['project_name'] if sub else pid}", ""]
    lines.append(f"  {'Per':<5} {'Month':<12} {'CPI':<8} {'Change':<10} {'Note'}")
    lines.append(f"  {'---':<5} {'-----':<12} {'---':<8} {'------':<10} {'----'}")

    # Show all periods but cap at 14 rows for readability
    start_i = max(0, len(cpi_hist) - 14)
    if start_i > 0:
        lines.append(f"  ... ({start_i} earlier periods omitted) ...")

    for i in range(start_i, len(cpi_hist)):
        p = proj["periods"][i]
        change = f"{p['cpi'] - cpi_hist[i-1]:+.3f}" if i > 0 else "  ---"
        period_in_prog = i + 1
        abs_period = period_in_prog  # relative period within project
        note = ""
        if step and abs_period == step["at_period"]: note = "<-- STEP CHANGE"
        if proj["periods"][i].get("rebaselined"):    note = "<-- REBASELINE"
        lines.append(f"  P{abs_period:<4} {_ML(cycle-(len(cpi_hist)-1-i)):<12} {p['cpi']:<8.3f} {change:<10} {note}")

    # Summary
    total_change = cpi_hist[-1] - cpi_hist[0]
    lines += [
        f"",
        f"  Total CPI change: {total_change:+.3f} over {len(cpi_hist)} periods",
        f"  Trend: {trend.direction} ({'structural - ' + str(trend.consecutive) + ' consecutive periods' if trend.is_structural else 'non-structural'})",
        f"  {trend.note}",
    ]
    if step:
        lines.append(f"  Step-change: {step['note']}")
    return "\n".join(lines)


# ── Tool 4: PM EAC submission history ─────────────────────────────────────────

def tool_get_pm_eac_history(project_id, cycle=None):
    """
    PM's EAC submissions vs system EAC across the last 6 months.
    Use to detect: has the PM been consistently optimistic month after month?
    A PM who is always $5M below system EAC is showing a pattern of denial.
    """
    cycle = cycle or CURRENT_CYCLE
    pid = project_id.upper()
    sub_current = _subs(cycle).get(pid)
    if not sub_current:
        return json.dumps({"error": f"Project {pid} not found."})

    from data.forecast_submissions import get_submissions_for_period, _pm_optimism_factor

    # Look back up to 5 prior months
    periods_to_check = list(range(max(1, cycle-5), cycle+1))
    lines = [f"PM EAC HISTORY: {pid} -- {sub_current['project_name']}",
             f"  Does this PM consistently submit lower EAC than system data suggests?", ""]
    lines.append(f"  {'Month':<14} {'PM EAC':<12} {'Sys EAC':<12} {'Gap':<10} {'CPI':<8} {'PM bias'}")
    lines.append(f"  {'-----':<14} {'------':<12} {'-------':<12} {'---':<10} {'---':<8} {'-------'}")

    patterns = []
    for period in periods_to_check:
        proj = _portfolio(period).get(pid)
        if not proj: continue
        subs_p = get_submissions_for_period(period)
        sub_p  = subs_p.get(pid)
        if not sub_p: continue
        pm_eac  = sub_p["pm_eac"]
        sys_eac, _ = _system_eac(proj)
        gap_pct = (pm_eac - sys_eac) / sys_eac * 100
        cpi     = proj["cpi"]
        bias    = "optimistic" if gap_pct < -3 else ("conservative" if gap_pct > 3 else "accurate")
        marker  = " <--" if period == cycle else ""
        lines.append(f"  {_ML(period):<14} {_M(pm_eac):<12} {_M(sys_eac):<12} {gap_pct:+.1f}%{'':<5} {cpi:.3f}{'':<4} {bias}{marker}")
        patterns.append(gap_pct)

    if len(patterns) >= 3:
        consistently_low = sum(1 for g in patterns if g < -3)
        lines += ["",
                  f"  Pattern over {len(patterns)} months: {consistently_low}/{len(patterns)} months PM was optimistic (gap < -3%)"]
        if consistently_low >= len(patterns) - 1:
            lines.append("  WARNING: PM has been consistently submitting below system EAC -- persistent optimism bias")
        elif consistently_low == 0:
            lines.append("  PM forecasting track record: accurate")
    return "\n".join(lines)


# ── Tool 5: Prior narratives ──────────────────────────────────────────────────

def tool_get_prior_explanations(project_id, cycle=None):
    """3 months of PM narratives. Call only when REPEATED_NARRATIVE signal detected."""
    cycle = cycle or CURRENT_CYCLE
    pid = project_id.upper()
    sub = _subs(cycle).get(pid)
    if not sub:
        return json.dumps({"error": f"Project {pid} not found."})

    priors = sub.get("prior_explanations", [])
    watch  = ["temporary","recovery expected","within approved budget","manageable",
              "no change to eac","challenging but achievable","contingency available","contingency remains"]
    current = sub["explanation"].lower()
    reps = []
    for phrase in watch:
        count = sum(1 for p in priors if phrase in p.lower()) + (1 if phrase in current else 0)
        if count >= 2:
            reps.append(f"  '{phrase}' used in {count} consecutive months")

    lines = [f"PRIOR NARRATIVES: {pid} -- {sub['project_name']} ({_ML(cycle)})", "_"*60]
    months_back = [_ML(cycle-2), _ML(cycle-1)]
    for i, p in enumerate(priors):
        lines += [f"", f"  [{months_back[i] if i < len(months_back) else 'Prior'}]:", f"  {p}"]
    lines += [f"", f"  [{_ML(cycle)} CURRENT]:", f"  {sub['explanation'][:200]}...",
              f"", f"PATTERN CHECK:"]
    if reps:
        lines.append("  WARNING -- repeated reassurance with no data improvement:")
        lines.extend(reps)
    else:
        lines.append("  No concerning repeated phrases.")
    return "\n".join(lines)


# ── Tool 6: Change order exposure ────────────────────────────────────────────

def tool_get_change_order_exposure(project_id, cycle=None):
    """
    Full change order register for one project.
    Reveals pending/disputed costs the PM has NOT included in their EAC.
    Call when get_project_detail shows a CO alert, or when the PM narrative
    mentions acceleration, rework, contamination, FX exposure, or regulatory changes.
    """
    cycle = cycle or CURRENT_CYCLE
    pid   = project_id.upper()
    sub   = _subs(cycle).get(pid)
    proj  = _portfolio(cycle).get(pid)
    if not sub or not proj:
        return json.dumps({"error": f"Project {pid} not found."})

    cos      = CHANGE_ORDERS.get(pid, [])
    pm_eac   = sub["pm_eac"]
    sys_eac, _ = _system_eac(proj)
    meta     = PROJECT_META.get(pid, {})

    lines = [
        f"CHANGE ORDER EXPOSURE: {pid} -- {sub['project_name']}",
        f"  Contract type: {meta.get('contract_type','UNKNOWN')} "
        f"({'client bears overrun' if meta.get('contract_type')=='REIMBURSABLE' else 'contractor risk' if meta.get('contract_type')=='LUMP_SUM' else 'pain/gain share'})",
        f"",
    ]

    if not cos:
        lines.append("  No change orders on record for this project.")
        return "\n".join(lines)

    lines.append(f"  {'Ref':<14} {'Description':<48} {'Value':>8}  {'Status':<10} {'In EAC?'}")
    lines.append(f"  {'---':<14} {'-'*48} {'------':>8}  {'------':<10} {'-------'}")

    total_hidden   = 0.0
    total_approved = 0.0
    total_disputed = 0.0

    for c in cos:
        v = c["value"]
        in_eac_str = "YES" if c["in_eac"] else "NO  <-- HIDDEN"
        status_str = c["status"].upper()
        desc_trunc = c["desc"][:47]
        lines.append(
            f"  {c['ref']:<14} {desc_trunc:<48} ${abs(v)/1e6:>6.2f}M  {status_str:<10} {in_eac_str}"
        )
        if c["status"] == "approved":
            if not c["in_eac"]: total_hidden += v
            else:               total_approved += v
        elif c["status"] == "pending":
            if not c["in_eac"]: total_hidden += v
        elif c["status"] == "disputed":
            if not c["in_eac"]: total_disputed += v

    hidden_material = [c for c in cos if not c["in_eac"] and c["significance"] == "material"]

    lines += [
        f"",
        f"  SUMMARY:",
        f"    Total hidden (pending, not in EAC):    ${total_hidden/1e6:.2f}M",
        f"    Total disputed (not in EAC):           ${total_disputed/1e6:.2f}M",
        f"    PM submitted EAC:                      {_M(pm_eac)}",
        f"    System EAC:                            {_M(sys_eac)}",
    ]
    if total_hidden > 0:
        adj_eac = pm_eac + total_hidden
        adj_pct = (adj_eac - sys_eac) / sys_eac * 100
        lines += [
            f"    Adjusted EAC (if hidden COs land):     {_M(adj_eac)} ({adj_pct:+.1f}% vs system)",
            f"",
            f"  RISK: PM's EAC of {_M(pm_eac)} does not include ${total_hidden/1e6:.1f}M "
            f"in {len(hidden_material)} material pending change order(s).",
        ]
        for c in hidden_material:
            lines.append(f"    - {c['note']}")
    else:
        lines.append(f"    All material change orders are in PM EAC. No hidden exposure.")

    return "\n".join(lines)


# ── Tool 7: WBS dollar breakdown ──────────────────────────────────────────────

def tool_get_wbs_cost_breakdown(project_id, cycle=None):
    """
    Dollar-level breakdown of cost overrun by WBS package.
    Use when HIDDEN_WBS signal is present, or when you want to quantify which
    package is driving the overrun and how much it will cost at completion.
    """
    cycle = cycle or CURRENT_CYCLE
    pid   = project_id.upper()
    sub   = _subs(cycle).get(pid)
    proj  = _portfolio(cycle).get(pid)
    if not sub or not proj:
        return json.dumps({"error": f"Project {pid} not found."})

    pm_eac = sub["pm_eac"]
    wbs    = proj["wbs"]
    total_overrun_to_date   = 0.0
    total_projected_overrun = 0.0

    lines = [
        f"WBS COST BREAKDOWN: {pid} -- {sub['project_name']} ({_ML(cycle)})",
        f"  What is each WBS package costing at completion?",
        f"",
        f"  {'Package':<32} {'BAC':>8}  {'CPI':>6}  {'Overrun$':>10}  {'Proj Final':>10}  {'Proj Over':>10}",
        f"  {'-'*32} {'---':>8}  {'---':>6}  {'--------':>10}  {'----------':>10}  {'---------':>10}",
    ]

    package_rows = []
    for w in wbs:
        bac_w = w["bac"]; ev_w = w["ev"]; ac_w = w["ac"]; cpi_w = w["cpi"]
        if bac_w == 0: continue

        # Cost overrun to date on this package
        overrun_to_date = ac_w - ev_w

        # Projected final cost for this package at current CPI
        if cpi_w > 0:
            proj_final = ac_w + (bac_w - ev_w) / cpi_w
        else:
            proj_final = ac_w + (bac_w - ev_w)

        proj_overrun = proj_final - bac_w
        total_overrun_to_date   += overrun_to_date
        total_projected_overrun += proj_overrun

        flag = ""
        if cpi_w < 0.75:  flag = "  <<CRITICAL"
        elif cpi_w < 0.88: flag = "  <warning"

        lines.append(
            f"  {w['wbs']:<32} {_M(bac_w):>8}  {cpi_w:>6.3f}  "
            f"{_M(overrun_to_date):>10}  {_M(proj_final):>10}  {_M(proj_overrun):>10}{flag}"
        )
        package_rows.append((w["wbs"], proj_overrun, bac_w, cpi_w))

    # Find primary driver
    worst = max(package_rows, key=lambda x: x[1]) if package_rows else None
    driver_pct = worst[1] / total_projected_overrun * 100 if (worst and total_projected_overrun > 0) else 0

    lines += [
        f"  {'':32} {'':>8}  {'':>6}  {'':>10}  {'':>10}  {'----------':>10}",
        f"  {'TOTAL':32} {'':>8}  {'':>6}  {_M(total_overrun_to_date):>10}  {'':>10}  {_M(total_projected_overrun):>10}",
        f"",
        f"  SYSTEM EAC: {_M(_system_eac(proj)[0])} | PM EAC: {_M(pm_eac)} | BAC: {_M(proj['bac'])}",
    ]
    if worst:
        lines.append(
            f"  PRIMARY DRIVER: {worst[0]} (CPI {worst[2]:.3f}) — "
            f"{_M(worst[1])} projected overrun ({driver_pct:.0f}% of total)"
        )
    return "\n".join(lines)


# ── Tool 8: Spend rate acceleration ──────────────────────────────────────────

def tool_get_spend_acceleration(project_id, cycle=None):
    """
    Monthly actual-cost rate trend for last 6 periods.
    Detects whether spending is accelerating — an early warning that future
    CPI will worsen even if the current period CPI looks stable.
    Call for SPI_TRAP cases (acceleration costs about to flow through) or
    when the PM claims 'costs are under control' but SPI has been declining.
    """
    cycle = cycle or CURRENT_CYCLE
    pid   = project_id.upper()
    sub   = _subs(cycle).get(pid)
    proj  = _portfolio(cycle).get(pid)
    if not sub or not proj:
        return json.dumps({"error": f"Project {pid} not found."})

    periods = proj["periods"]
    if len(periods) < 3:
        return f"SPEND ACCELERATION: {pid} -- insufficient data (< 3 periods)"

    # Compute monthly AC increments (cumulative AC → monthly spend)
    increments = []
    for i in range(1, len(periods)):
        inc = periods[i]["ac"] - periods[i-1]["ac"]
        abs_period = i + 1
        month_label = _ML(cycle - (len(periods) - 1 - i))
        increments.append({"period": abs_period, "month": month_label,
                            "ac_inc": max(0, inc), "cpi": periods[i]["cpi"]})

    # Only show last 6 increments
    recent = increments[-6:] if len(increments) >= 6 else increments
    prior_window = increments[:-2] if len(increments) >= 4 else increments[:-1]
    prior_avg = sum(r["ac_inc"] for r in prior_window) / len(prior_window) if prior_window else 0
    last2_avg  = sum(r["ac_inc"] for r in recent[-2:]) / 2 if len(recent) >= 2 else recent[-1]["ac_inc"]
    acceleration_pct = (last2_avg - prior_avg) / prior_avg * 100 if prior_avg > 0 else 0

    lines = [
        f"SPEND ACCELERATION: {pid} -- {sub['project_name']}",
        f"  Monthly actual cost increments — is spending ramping up?",
        f"",
        f"  {'Month':<13} {'AC/Month':>10}  {'vs Prior Avg':>13}  CPI",
        f"  {'-----':<13} {'--------':>10}  {'------------':>13}  ---",
    ]
    for r in recent:
        vs = f"{(r['ac_inc']-prior_avg)/prior_avg*100:+.0f}%" if prior_avg > 0 else "--"
        alert = "  ** SPIKE" if r["ac_inc"] > prior_avg * 1.35 else ""
        lines.append(
            f"  {r['month']:<13} {_M(r['ac_inc']):>10}  {vs:>13}  {r['cpi']:.3f}{alert}"
        )

    lines += [
        f"",
        f"  Prior {len(prior_window)}-month avg spend: {_M(prior_avg)}/month",
        f"  Last 2 months avg:            {_M(last2_avg)}/month",
        f"  Acceleration vs prior avg:    {acceleration_pct:+.0f}%",
    ]
    if acceleration_pct > 35:
        lines.append(f"  WARNING: Spending accelerating significantly. "
                     f"If this rate continues, remaining budget depletes faster than planned.")
    elif acceleration_pct > 15:
        lines.append(f"  NOTE: Spend rate trending upward. Monitor closely.")
    else:
        lines.append(f"  Spend rate stable — no acceleration detected.")

    return "\n".join(lines)


# ── Tool 9: Portfolio $ exposure ranking ──────────────────────────────────────

def tool_get_portfolio_exposure_ranking(cycle=None):
    """
    All 20 projects ranked by estimated $ at risk (system EAC minus BAC).
    Call at the START alongside load_all_summaries when you want to prioritise
    where to spend your investigation effort — largest $ exposure first.
    """
    cycle     = cycle or CURRENT_CYCLE
    portfolio = _portfolio(cycle)
    subs      = _subs(cycle)
    month     = _ML(cycle)

    rows = []
    for pid, proj in portfolio.items():
        sub = subs.get(pid)
        if not sub: continue
        sys_eac, _ = _system_eac(proj)
        at_risk = max(0.0, sys_eac - proj["bac"])
        over_pct = (sys_eac - proj["bac"]) / proj["bac"] * 100
        rows.append((pid, proj["meta"]["name"], proj["bac"], sys_eac, at_risk, over_pct, proj["cpi"]))

    rows.sort(key=lambda x: x[4], reverse=True)

    total_risk = sum(r[4] for r in rows)
    n_over_10  = sum(1 for r in rows if r[5] > 10)

    lines = [
        f"PORTFOLIO EXPOSURE RANKING -- {month}",
        f"  Projects sorted by estimated $ at risk (System EAC - BAC)",
        f"",
        f"  {'#':<3} {'Project':<38} {'BAC':>8}  {'Sys EAC':>8}  {'$AtRisk':>8}  {'%Over':>6}  {'CPI':>6}",
        f"  {'--':<3} {'-'*38} {'---':>8}  {'-------':>8}  {'-------':>8}  {'-----':>6}  {'---':>6}",
    ]
    for i, (pid, name, bac, seac, risk, over_pct, cpi) in enumerate(rows, 1):
        flag = "  **" if risk > 10e6 else ("  *" if risk > 4e6 else "")
        lines.append(
            f"  {i:<3} {pid+' '+name:<38} {_M(bac):>8}  {_M(seac):>8}  "
            f"{_M(risk):>8}  {over_pct:>+5.0f}%  {cpi:>6.3f}{flag}"
        )
    lines += [
        f"",
        f"  Total portfolio at risk:  {_M(total_risk)}",
        f"  Projects >10% over BAC:   {n_over_10} of {len(rows)}",
        f"  ** = >$10M exposure | * = >$4M exposure",
    ]
    return "\n".join(lines)


# ── Tool 10: Write one decision ────────────────────────────────────────────────

def tool_write_decision(project_id, decision, comment, _already_decided=None):
    """Write decision for ONE project. Returns remaining list so agent knows what's left."""
    from data.forecast_submissions import SUBMISSIONS
    pid = project_id.upper()
    decided = set(_already_decided or [])
    decided.add(pid)
    all_pids  = list(SUBMISSIONS.keys())
    remaining = [p for p in all_pids if p not in decided]
    return json.dumps({
        "status":          "ok",
        "written":         pid,
        "decision":        decision.upper(),
        "remaining":       remaining,
        "remaining_count": len(remaining),
        "done":            len(remaining) == 0,
    })
