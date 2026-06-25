"""Forecast Challenge Desk"""
import time
import streamlit as st
from data.forecast_submissions import SUBMISSIONS, CURRENT_CYCLE, PERIOD_LABELS, CYCLE_GROUND_TRUTH, REVIEW_CYCLES
from data.mock_portfolio import build_portfolio
from data.change_orders import CHANGE_ORDERS, PROJECT_META
from agent.challenge_agent import run_challenge_analysis

st.set_page_config(page_title="Forecast Challenge Desk", page_icon="📋", layout="centered")

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.block-container { padding-top: 1.6rem !important; }

/* Badges */
.badge {
  display: inline-block;
  font-size: 0.62rem; font-weight: 700;
  letter-spacing: 0.05em; text-transform: uppercase;
  padding: 2px 7px; border-radius: 3px;
  vertical-align: middle;
}
.b-F { background:#fef2f2; color:#dc2626; }
.b-A { background:#f0fdf4; color:#16a34a; }
.b-N { background:#eff6ff; color:#2563eb; }

/* Decision cards */
.dc {
  padding: 10px 14px; margin: 3px 0;
  border: 1px solid #e5e7eb; border-radius: 6px;
  border-left-width: 3px; background: #fff;
  display: flex; gap: 14px; align-items: flex-start;
}
.dc-F { border-left-color: #dc2626; }
.dc-A { border-left-color: #16a34a; }
.dc-N { border-left-color: #2563eb; }
.dc-pid  { font-size: 0.68rem; font-weight: 600; color: #9ca3af; margin-top: 3px; }
.dc-name { font-size: 0.875rem; font-weight: 600; color: #111827; line-height: 1.3; }
.dc-stat { font-size: 0.7rem; color: #6b7280; margin-top: 3px; }
.dc-cmt  {
  font-size: 0.78rem; color: #374151; margin-top: 7px;
  line-height: 1.55; border-top: 1px solid #f3f4f6; padding-top: 6px;
}

/* KPI strip */
.kpi-strip {
  display: flex; gap: 28px;
  padding: 12px 0 14px; border-bottom: 1px solid #e5e7eb;
  margin-bottom: 16px;
}
.kpi-val { font-size: 1.4rem; font-weight: 700; line-height: 1; }
.kpi-lbl { font-size: 0.6rem; color: #9ca3af; text-transform: uppercase;
           letter-spacing: 0.07em; margin-top: 3px; }

/* Section label */
.sec { font-size: 0.62rem; font-weight: 600; text-transform: uppercase;
       letter-spacing: 0.09em; color: #9ca3af; margin: 20px 0 10px; }

/* Hard case chips */
.hc-row { display: flex; gap: 8px; flex-wrap: wrap; }
.hc-chip {
  padding: 5px 11px; border-radius: 4px; font-size: 0.72rem;
  line-height: 1.45; border: 1px solid;
}
.hc-ok   { background:#f0fdf4; border-color:#bbf7d0; color:#15803d; }
.hc-miss { background:#fef2f2; border-color:#fecaca; color:#dc2626; }

/* Ground truth */
.gt-ok  { font-size: 0.68rem; color: #16a34a; margin-left: 6px; }
.gt-err { font-size: 0.68rem; color: #dc2626; margin-left: 6px; }

/* Tables */
.tbl { width: 100%; border-collapse: collapse; font-size: 0.78rem; }
.tbl th {
  font-size: 0.6rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.07em; color: #6b7280;
  border-bottom: 1px solid #e5e7eb; padding: 7px 10px; text-align: left;
}
.tbl td { padding: 6px 10px; border-bottom: 1px solid #f3f4f6; color: #111827; }
.tbl tr:last-child td { border-bottom: none; }
.tbl tr:hover td { background: #fafafa; }

/* Misc */
.divider { height: 1px; background: #e5e7eb; margin: 16px 0; }
.red   { color: #dc2626; }
.green { color: #16a34a; }
.blue  { color: #2563eb; }
.muted { color: #9ca3af; }
.pill  {
  display:inline-block; padding:1px 6px; border-radius:3px;
  font-size:0.68rem; font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px">
  <span style="font-size:1.05rem;font-weight:700;color:#111827">Forecast Challenge Desk</span>
  <span style="font-size:0.72rem;color:#9ca3af">NorthStar Infrastructure Group · Finance</span>
</div>
<div style="height:1px;background:#e5e7eb;margin-bottom:16px"></div>
""", unsafe_allow_html=True)

# ── Month selector ─────────────────────────────────────────────────────────────
st.markdown('<div style="font-size:0.72rem;color:#6b7280;margin-bottom:6px;font-weight:500">REVIEW PERIOD</div>', unsafe_allow_html=True)
cycle_options = {PERIOD_LABELS[c]: c for c in REVIEW_CYCLES}
cols_month = st.columns(len(REVIEW_CYCLES))
for i, (label, cyc) in enumerate(cycle_options.items()):
    with cols_month[i]:
        if st.button(label, key=f"m_{cyc}",
                     type="primary" if cyc == st.session_state.get("sel_cycle", CURRENT_CYCLE) else "secondary",
                     use_container_width=True):
            st.session_state.sel_cycle = cyc
            st.session_state.update(result=None, trace=[], elapsed=None, live_dec=[])
            st.rerun()

sel_cycle = st.session_state.get("sel_cycle", CURRENT_CYCLE)
sel_label = PERIOD_LABELS.get(sel_cycle, f"Period {sel_cycle}")
gt        = CYCLE_GROUND_TRUTH.get(sel_cycle, {})

for k, v in [("result", None), ("trace", []), ("elapsed", None), ("live_dec", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Portfolio helper ───────────────────────────────────────────────────────────
@st.cache_data
def _port(cycle):
    return build_portfolio(as_of_period=cycle)

def _sys_eac(proj):
    from tools.evm_engine import (eac_cpi, eac_remaining_at_budget, eac_composite,
                                   analyse_cpi_trend, detect_step_change, recommend_eac_method)
    bac = proj["bac"]; ev = proj["ev"]; ac = proj["ac"]; spi = proj["spi"]
    cpi_h = [p["cpi"] for p in proj["periods"]]
    tr = analyse_cpi_trend(cpi_h)
    st2 = detect_step_change(cpi_h)
    meth, _ = recommend_eac_method(proj["pct_complete"], tr, st2 is not None)
    return {"cpi": eac_cpi(bac, ev, ac),
            "at_budget": eac_remaining_at_budget(bac, ev, ac),
            "composite": eac_composite(bac, ev, ac, spi)}[meth]

def _key_findings(tool: str, text: str) -> list:
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    WARN = ["NOT_CREDIBLE", "CRITICAL", "WARNING", "NOT CREDIBLE",
            "persistent optimism", "accelerating", "HIDDEN", "structural", "Repeated reassurance"]
    KEYS = {
        "get_project_detail":        ["BAC", "CPI ", "SPI ", "Trend:", "EAC CREDIBILITY",
                                      "Gap:", "Implied future CPI", "Recovery needed",
                                      "CHANGE ORDER ALERT", "Contingency:"],
        "get_change_order_exposure": ["Total hidden", "Adjusted EAC", "RISK:", "Contract type:"],
        "get_wbs_cost_breakdown":    ["<<CRITICAL", "PRIMARY DRIVER", "TOTAL"],
        "get_cpi_history":           ["Total CPI change", "Trend:", "Step-change"],
        "get_pm_eac_history":        ["Pattern over", "WARNING", "PM forecasting"],
        "get_spend_acceleration":    ["Acceleration vs", "Last 2 months avg", "WARNING"],
        "get_prior_explanations":    ["WARNING", "used in", "No concerning"],
    }
    seen, out = set(), []
    for line in lines:
        if len(out) >= 5: break
        for key in KEYS.get(tool, []):
            if key in line and line not in seen:
                out.append((line, any(w in line for w in WARN)))
                seen.add(line)
                break
    return out

HARD_CASES = {
    "P07": ("SPI Trap",           "CPI 1.01 · SPI 0.82"),
    "P13": ("Contingency Lie",    "97% contingency consumed"),
    "P06": ("Hidden WBS",         "Civil CPI 0.61 masked"),
    "P17": ("Impossible CPI",     "Needs 0.936 from 0.762"),
    "P01": ("Repeated Narrative", "Same phrase ×3 months"),
}

def _card_html(d, portfolio):
    dec  = d.get("decision", "ACCEPT").upper()
    pid  = d.get("project_id", "")
    name = SUBMISSIONS.get(pid, {}).get("project_name", pid)
    cmt  = d.get("comment", "")
    proj = portfolio.get(pid, {})

    dc_cls = {"FLAG": "dc-F", "ACCEPT": "dc-A", "NEEDS_EVIDENCE": "dc-N"}.get(dec, "dc-A")
    b_cls  = {"FLAG": "b-F",  "ACCEPT": "b-A",  "NEEDS_EVIDENCE": "b-N"}.get(dec, "b-A")
    lbl    = {"FLAG": "FLAG", "ACCEPT": "ACCEPT", "NEEDS_EVIDENCE": "NEEDS EV."}.get(dec, dec)

    cpi_str = f"CPI {proj['cpi']:.3f}" if proj.get("cpi") else ""
    pct_str = f"{proj.get('pct_complete', 0):.0f}% complete" if proj else ""
    bac_str = f"BAC ${proj['bac']/1e6:.0f}M" if proj.get("bac") else ""
    risk_str = ""
    if proj.get("bac"):
        seac = _sys_eac(proj)
        gap  = (seac - proj["bac"]) / proj["bac"] * 100
        col  = "#dc2626" if gap > 5 else "#6b7280"
        risk_str = f'<span style="color:{col}">{gap:+.0f}% vs BAC</span>'

    gt_lbl = gt.get(pid, "")
    ok = (dec == gt_lbl) or (dec == "FLAG" and gt_lbl in ("ESCALATE", "CHALLENGE"))
    gt_html = (f'<span class="gt-ok">✓</span>'
               if ok else f'<span class="gt-err">✗ {gt_lbl}</span>') if gt_lbl else ""

    stats = " · ".join(p for p in [cpi_str, pct_str, bac_str] if p)
    if risk_str:
        stats += f" · {risk_str}"

    return (
        f'<div class="dc {dc_cls}">'
        f'<div style="min-width:62px;padding-top:1px">'
        f'<span class="badge {b_cls}">{lbl}</span>'
        f'<div class="dc-pid">{pid}</div></div>'
        f'<div style="flex:1;min-width:0">'
        f'<div class="dc-name">{name}{gt_html}</div>'
        f'<div class="dc-stat">{stats}</div>'
        f'<div class="dc-cmt">{cmt}</div>'
        f'</div></div>'
    )

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_review, tab_data, tab_tools = st.tabs(["Review", "Data", "Tools"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_review:
    portfolio = _port(sel_cycle)

    col_btn, col_status = st.columns([1, 3])
    run_clicked = col_btn.button(f"Run {sel_label}", type="primary", use_container_width=True)
    status_ph   = col_status.empty()

    if run_clicked:
        st.session_state.update(result=None, trace=[], elapsed=None, live_dec=[])
        live_hdr  = st.empty()
        live_area = st.empty()

        def _on_decision(d):
            st.session_state.live_dec.append(d)
            n   = len(st.session_state.live_dec)
            pid = d.get("pid") or d.get("project_id", "")
            status_ph.caption(f"{pid} · {d.get('decision','')} — {n}/20")
            live_hdr.markdown(
                f'<div style="font-size:0.8rem;color:#6b7280;margin-bottom:8px">'
                f'{n} / 20 complete</div>', unsafe_allow_html=True)
            order = {"FLAG": 0, "NEEDS_EVIDENCE": 1, "ACCEPT": 2}
            sorted_d = sorted(st.session_state.live_dec,
                              key=lambda x: order.get(x.get("decision", ""), 9))
            live_area.markdown(
                "".join(_card_html(d, portfolio) for d in sorted_d),
                unsafe_allow_html=True)

        t0 = time.time()
        with st.spinner(f"Running {sel_label}..."):
            result, trace = run_challenge_analysis(cycle=sel_cycle, on_decision=_on_decision)
        elapsed = round(time.time() - t0, 1)
        st.session_state.update(result=result, trace=trace, elapsed=elapsed)
        status_ph.empty(); live_hdr.empty(); live_area.empty()
        st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    result  = st.session_state.result
    elapsed = st.session_state.elapsed

    if result is None:
        st.markdown(
            '<div style="font-size:0.82rem;color:#9ca3af;padding:18px 0">'
            'Select a month above and click <strong>Run</strong> to start. '
            'Runs 20 agents in parallel — typically 25–40 s.</div>',
            unsafe_allow_html=True)
    else:
        decisions = result.get("decisions", [])
        summary   = result.get("summary", {})
        n_flag    = summary.get("FLAG", 0)
        n_acc     = summary.get("ACCEPT", 0)
        n_needs   = summary.get("NEEDS_EVIDENCE", 0)
        n_tools   = len([s for s in st.session_state.trace if "tool" in s])

        # KPI strip
        st.markdown(
            f'<div class="kpi-strip">'
            f'<div><div class="kpi-val red">{n_flag}</div><div class="kpi-lbl">Flagged</div></div>'
            f'<div><div class="kpi-val green">{n_acc}</div><div class="kpi-lbl">Accepted</div></div>'
            f'<div><div class="kpi-val blue">{n_needs}</div><div class="kpi-lbl">Needs Ev.</div></div>'
            f'<div><div class="kpi-val" style="color:#6b7280">{elapsed}s</div><div class="kpi-lbl">Run time</div></div>'
            f'<div><div class="kpi-val" style="color:#6b7280">{n_tools}</div><div class="kpi-lbl">Tool calls</div></div>'
            f'</div>',
            unsafe_allow_html=True)

        # Decision cards
        order = {"FLAG": 0, "NEEDS_EVIDENCE": 1, "ACCEPT": 2}
        for d in sorted(decisions, key=lambda x: order.get(x.get("decision", ""), 9)):
            st.markdown(_card_html(d, portfolio), unsafe_allow_html=True)

        # Hard cases
        if sel_cycle == CURRENT_CYCLE:
            st.markdown('<div class="divider"></div><div class="sec">Hard Case Detection</div>', unsafe_allow_html=True)
            dec_map = {d["project_id"]: d["decision"].upper() for d in decisions}
            caught_n = 0
            hc_html = '<div class="hc-row">'
            for pid, (label, desc) in HARD_CASES.items():
                caught = dec_map.get(pid) == "FLAG"
                if caught: caught_n += 1
                cls = "hc-ok" if caught else "hc-miss"
                status = "Caught" if caught else "Missed"
                hc_html += (
                    f'<div class="hc-chip {cls}">'
                    f'<strong>{status}</strong> · {label}'
                    f'<br><span style="font-size:0.63rem;opacity:0.75">{pid} · {desc}</span>'
                    f'</div>')
            hc_html += '</div>'
            st.markdown(hc_html, unsafe_allow_html=True)
        else:
            caught_n = 0
            dec_map  = {d["project_id"]: d["decision"].upper() for d in decisions}

        # Accuracy metrics
        st.markdown('<div class="divider"></div><div class="sec">Accuracy — ' + sel_label + '</div>', unsafe_allow_html=True)
        correct = sum(
            1 for d in decisions
            if d.get("decision", "").upper() == gt.get(d.get("project_id", ""), "")
            or (d.get("decision", "").upper() == "FLAG"
                and gt.get(d.get("project_id", ""), "") in ("ESCALATE", "CHALLENGE")))
        total = len(decisions)
        false_acc = [d["project_id"] for d in decisions
                     if d.get("decision", "").upper() == "ACCEPT"
                     and gt.get(d.get("project_id", ""), "") in ("ESCALATE", "CHALLENGE")]
        n_should = sum(1 for v in gt.values() if v in ("ESCALATE", "CHALLENGE"))
        far = len(false_acc) / max(1, n_should)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy", f"{correct/total*100:.0f}%" if total else "--")
        c2.metric("False Accept Rate", f"{far*100:.0f}%",
                  delta="OK" if far < .10 else "Above threshold",
                  delta_color="normal" if far < .10 else "inverse")
        c3.metric("Hard Cases", f"{caught_n}/5" if sel_cycle == CURRENT_CYCLE else "N/A")
        c4.metric("Tool Calls", str(n_tools))
        if false_acc:
            st.warning(f"False accepts: {', '.join(false_acc)}")

        # ── Investigation Trace ──────────────────────────────────────────────
        st.markdown('<div class="divider"></div><div class="sec">Investigation Trace</div>', unsafe_allow_html=True)

        trace    = st.session_state.trace
        dec_map2 = {d["project_id"]: d for d in decisions}
        pids_decided = sorted(
            dec_map2.keys(),
            key=lambda p: (order.get(dec_map2[p].get("decision", ""), 9), p))

        def _sel_label(p):
            d2   = dec_map2.get(p, {})
            dec2 = d2.get("decision", "?")
            name2 = SUBMISSIONS.get(p, {}).get("project_name", p)
            n_calls = len([t for t in trace
                           if t.get("pid") == p and t.get("tool", "") not in ("write_decision", "")])
            return f"{p} · {name2} — {dec2} · {n_calls} call{'s' if n_calls != 1 else ''}"

        sel_pid = st.selectbox(
            "Project",
            options=pids_decided,
            format_func=_sel_label,
            label_visibility="collapsed")

        if sel_pid:
            d_sel    = dec_map2[sel_pid]
            dec_sel  = d_sel.get("decision", "?").upper()
            cmt_sel  = d_sel.get("comment", "")
            name_sel = SUBMISSIONS.get(sel_pid, {}).get("project_name", sel_pid)

            badge_col = {"FLAG": "#dc2626", "ACCEPT": "#16a34a", "NEEDS_EVIDENCE": "#2563eb"}.get(dec_sel, "#6b7280")
            b_cls_sel = {"FLAG": "b-F", "ACCEPT": "b-A", "NEEDS_EVIDENCE": "b-N"}.get(dec_sel, "b-A")
            badge_lbl = {"FLAG": "FLAG", "ACCEPT": "ACCEPT", "NEEDS_EVIDENCE": "NEEDS EV."}.get(dec_sel, dec_sel)

            steps = [t for t in trace
                     if t.get("pid") == sel_pid and t.get("tool", "") not in ("write_decision", "")]

            if not steps:
                st.markdown(
                    '<div style="font-size:0.8rem;color:#9ca3af;padding:10px 0">'
                    'No investigation steps — agent decided without tool calls.</div>',
                    unsafe_allow_html=True)
            else:
                # Timeline
                for i, step in enumerate(steps, 1):
                    tname    = step["tool"]
                    findings = _key_findings(tname, step.get("result", ""))

                    # Step row
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:10px;margin:14px 0 4px">'
                        f'<span style="background:#e5e7eb;color:#6b7280;border-radius:50%;'
                        f'width:18px;height:18px;display:inline-flex;align-items:center;'
                        f'justify-content:center;font-size:0.58rem;font-weight:700;flex-shrink:0">{i}</span>'
                        f'<code style="font-size:0.8rem;color:#111827;background:transparent;'
                        f'font-weight:600">{tname}</code>'
                        f'</div>',
                        unsafe_allow_html=True)

                    # Findings
                    if findings:
                        fhtml = '<div style="padding-left:28px;margin-bottom:2px">'
                        for txt, is_warn in findings:
                            color  = "#b45309" if is_warn else "#6b7280"
                            prefix = "⚠" if is_warn else "·"
                            fhtml += (
                                f'<div style="font-size:0.74rem;color:{color};'
                                f'line-height:1.85;font-family:monospace">'
                                f'{prefix}&nbsp;{txt}</div>')
                        fhtml += '</div>'
                        st.markdown(fhtml, unsafe_allow_html=True)

                    with st.expander("Full output"):
                        st.code(step.get("result", "") or "(no output)", language=None)

            # Decision card
            gt_lbl2 = gt.get(sel_pid, "")
            ok2 = (dec_sel == gt_lbl2) or (dec_sel == "FLAG" and gt_lbl2 in ("ESCALATE", "CHALLENGE"))
            gt_line = ""
            if gt_lbl2:
                gt_line = (
                    f'<span class="{"gt-ok" if ok2 else "gt-err"}">'
                    f'{"✓ Correct" if ok2 else "✗ Expected " + gt_lbl2}</span>')

            st.markdown(
                f'<div style="border:1px solid #e5e7eb;border-left:3px solid {badge_col};'
                f'border-radius:6px;padding:12px 14px;margin-top:14px;background:#fafafa">'
                f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">'
                f'<span class="badge {b_cls_sel}">{badge_lbl}</span>'
                f'<span style="font-size:0.82rem;font-weight:600;color:#111827">'
                f'{sel_pid} · {name_sel}</span>{gt_line}'
                f'</div>'
                f'<div style="font-size:0.8rem;color:#374151;line-height:1.6;'
                f'border-top:1px solid #e5e7eb;padding-top:8px">{cmt_sel}</div>'
                f'</div>',
                unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DATA
# ══════════════════════════════════════════════════════════════════════════════
with tab_data:
    st.markdown(
        '<div style="font-size:0.8rem;color:#6b7280;margin-bottom:16px;line-height:1.6">'
        '20 simulated infrastructure projects across 5 regions, each with 14 months of EVM history, '
        'per-package WBS breakdown, contingency register, and change order log. '
        'Seven distinct failure scenarios are embedded in the data.'
        '</div>',
        unsafe_allow_html=True)

    # ── Portfolio overview ────────────────────────────────────────────────────
    st.markdown('<div class="sec">Portfolio — ' + sel_label + '</div>', unsafe_allow_html=True)
    p14 = _port(CURRENT_CYCLE)

    def _cpi_c(v):
        return "#16a34a" if v >= .97 else ("#d97706" if v >= .90 else "#dc2626")

    tbl = '<table class="tbl"><thead><tr>'
    for h in ["", "Project", "Type", "Region", "BAC", "CPI", "SPI", "% Done", "Contract", "Hidden COs"]:
        align = "right" if h in ("BAC",) else ("center" if h in ("CPI","SPI","% Done","Hidden COs") else "left")
        tbl  += f'<th style="text-align:{align}">{h}</th>'
    tbl += '</tr></thead><tbody>'

    for i, (pid, proj) in enumerate(p14.items()):
        sub  = SUBMISSIONS.get(pid, {})
        meta = PROJECT_META.get(pid, {})
        cpi  = proj["cpi"]; spi = proj["spi"]
        hcos = len([c for c in CHANGE_ORDERS.get(pid, []) if not c["in_eac"] and c["significance"] == "material"])
        hco_h = (f'<span class="pill" style="background:#fef2f2;color:#dc2626">{hcos}</span>'
                 if hcos else '<span class="muted">—</span>')
        bg = "#fff" if i % 2 == 0 else "#fafafa"
        tbl += (
            f'<tr style="background:{bg}">'
            f'<td style="font-weight:600;color:#2563eb">{pid}</td>'
            f'<td>{sub.get("project_name","")[:28]}</td>'
            f'<td style="color:#6b7280">{proj["meta"]["type"]}</td>'
            f'<td style="color:#6b7280">{proj["meta"]["region"]}</td>'
            f'<td style="text-align:right">${proj["bac"]/1e6:.0f}M</td>'
            f'<td style="text-align:center;font-weight:600;color:{_cpi_c(cpi)}">{cpi:.3f}</td>'
            f'<td style="text-align:center;color:#374151">{spi:.3f}</td>'
            f'<td style="text-align:center;color:#374151">{proj["pct_complete"]:.0f}%</td>'
            f'<td style="color:#6b7280;font-size:0.7rem">{meta.get("contract_type","")}</td>'
            f'<td style="text-align:center">{hco_h}</td>'
            f'</tr>')
    tbl += '</tbody></table>'
    st.markdown(tbl, unsafe_allow_html=True)

    # ── Project deep-dive ─────────────────────────────────────────────────────
    st.markdown('<div class="divider"></div><div class="sec">Project Deep-Dive — P06 Cairo Power Station</div>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:0.78rem;color:#6b7280;margin-bottom:14px">'
        'Scenario: <em>Hidden WBS Disaster</em> — project-level CPI 0.936 is concerning but manageable; '
        'Civil &amp; Structural at CPI 0.61 is catastrophic. $6.3M in pending change orders excluded from PM EAC.'
        '</div>',
        unsafe_allow_html=True)

    p06 = p14["P06"]; s06 = SUBMISSIONS["P06"]; m06 = PROJECT_META["P06"]
    cos06_h = [c for c in CHANGE_ORDERS["P06"] if not c["in_eac"]]

    st.markdown(
        f'<div style="background:#fafafa;border:1px solid #e5e7eb;border-radius:6px;'
        f'padding:10px 14px;font-size:0.78rem;color:#374151;margin-bottom:12px">'
        f'<strong>{m06["contract_type"]}</strong> &nbsp;·&nbsp; {m06["contractor"]} '
        f'&nbsp;·&nbsp; BAC ${p06["bac"]/1e6:.0f}M '
        f'&nbsp;·&nbsp; <span style="color:#dc2626;font-weight:600">'
        f'{m06["open_risks_above_500k"]} open risks &gt;$500K</span></div>',
        unsafe_allow_html=True)

    cc1, cc2, cc3, cc4 = st.columns(4)
    cc1.metric("CPI", f"{p06['cpi']:.3f}", delta="structural decline", delta_color="inverse")
    cc2.metric("SPI", f"{p06['spi']:.3f}")
    cc3.metric("% Complete", f"{p06['pct_complete']:.0f}%")
    cc4.metric("Contingency left",
               f"${p06['contingency']['remaining']/1e6:.1f}M",
               delta=f"{100 - p06['contingency']['pct_consumed']:.0f}% remaining")

    st.markdown('<div style="margin-top:14px;margin-bottom:6px;font-size:0.72rem;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.07em">WBS Breakdown</div>', unsafe_allow_html=True)
    wt = '<table class="tbl"><thead><tr>'
    for j, h in enumerate(["Package", "BAC", "EV", "AC", "CPI", "Proj. Overrun"]):
        align = "right" if j > 0 else "left"
        wt += f'<th style="text-align:{align}">{h}</th>'
    wt += '</tr></thead><tbody>'
    for i, w in enumerate(p06["wbs"]):
        bg2 = "#fef2f2" if w["cpi"] < .75 else ("#fffbeb" if w["cpi"] < .90 else ("#fff" if i % 2 == 0 else "#fafafa"))
        cpic = "#dc2626" if w["cpi"] < .75 else ("#d97706" if w["cpi"] < .90 else "#16a34a")
        po   = w["ac"] + (w["bac"] - w["ev"]) / w["cpi"] - w["bac"] if w["cpi"] > 0 else 0
        flag = " · CRITICAL" if w["cpi"] < .75 else ""
        wt  += (
            f'<tr style="background:{bg2}">'
            f'<td style="font-weight:{"600" if w["cpi"]<.75 else "400"}">{w["wbs"]}{flag}</td>'
            f'<td style="text-align:right">${w["bac"]/1e6:.1f}M</td>'
            f'<td style="text-align:right">${w["ev"]/1e6:.1f}M</td>'
            f'<td style="text-align:right">${w["ac"]/1e6:.1f}M</td>'
            f'<td style="text-align:center;font-weight:600;color:{cpic}">{w["cpi"]:.3f}</td>'
            f'<td style="text-align:right;color:{"#dc2626" if po>0 else "#16a34a"}">'
            f'{"+" if po > 0 else ""}${po/1e6:.1f}M</td></tr>')
    wt += '</tbody></table>'
    st.markdown(wt, unsafe_allow_html=True)

    if cos06_h:
        st.markdown('<div style="margin-top:14px;margin-bottom:6px;font-size:0.72rem;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:0.07em">Hidden Change Orders</div>', unsafe_allow_html=True)
        co_tbl = '<table class="tbl"><thead><tr>'
        for h in ["Ref", "Description", "Value", "Status"]:
            co_tbl += f'<th>{h}</th>'
        co_tbl += '</tr></thead><tbody>'
        for c in cos06_h:
            co_tbl += (
                f'<tr>'
                f'<td style="font-weight:600;color:#dc2626;white-space:nowrap">{c["ref"]}</td>'
                f'<td>{c["desc"]}</td>'
                f'<td style="white-space:nowrap;font-weight:600">${c["value"]/1e6:.1f}M</td>'
                f'<td style="color:#6b7280;font-size:0.7rem;text-transform:uppercase">{c["status"]}</td>'
                f'</tr>')
        co_tbl += '</tbody></table>'
        st.markdown(co_tbl, unsafe_allow_html=True)

    st.markdown(
        f'<div style="background:#fafafa;border:1px solid #e5e7eb;border-radius:6px;'
        f'padding:10px 14px;margin-top:12px;font-size:0.78rem;color:#374151;line-height:1.6">'
        f'<strong style="color:#6b7280;font-size:0.62rem;text-transform:uppercase;letter-spacing:0.07em">'
        f'PM Narrative</strong><br>{s06["explanation"][:280]}…'
        f'</div>',
        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TOOLS
# ══════════════════════════════════════════════════════════════════════════════
with tab_tools:
    st.markdown(
        '<div style="font-size:0.8rem;color:#6b7280;margin-bottom:16px;line-height:1.6">'
        'Each agent runs a ReAct loop and calls tools adaptively based on what each tool reveals. '
        'Clean projects use 1 call. Deeply suspicious ones use up to 7. '
        'Tools return deterministic data — the LLM never generates numbers, only interprets them.'
        '</div>',
        unsafe_allow_html=True)

    TOOLS_DEF = [
        ("Portfolio",    "load_all_summaries",            "Once per run — shared across all agents",
         "Compact scan of all 20 projects: CPI, SPI, EAC gap, and signal flags. Passed as context to every agent before investigation begins."),
        ("Portfolio",    "get_portfolio_exposure_ranking","Once per run — shared across all agents",
         "All 20 projects ranked by $ at risk (System EAC − BAC). Agents use this to calibrate investigation depth relative to portfolio exposure."),
        ("Investigation","get_project_detail",            "Any project with !! signals",
         "Full EVM snapshot: CPI/SPI trend, credibility verdict, implied future CPI, WBS per-package CPI, contingency status, PM narrative. CO alert shown if hidden change orders exist."),
        ("Deep-dive",    "get_change_order_exposure",     "CO alert in project detail",
         "Full change order register. Reveals pending/disputed costs excluded from PM EAC. Highest impact on REIMBURSABLE contracts — undisclosed COs flow directly to client budget."),
        ("Deep-dive",    "get_wbs_cost_breakdown",        "HIDDEN_WBS signal (Civil CPI < 0.78)",
         "Dollar overrun per WBS package at completion. Converts a CPI signal to a concrete figure: Civil CPI 0.61 → $13.4M projected overrun, 90% of total project exposure."),
        ("Deep-dive",    "get_spend_acceleration",        "SPI_TRAP signal (SPI < 0.88, CPI clean)",
         "Monthly actual-cost increment trend over 6 periods. Acceleration invoices appear as future AC spikes — CPI drops before the monthly snapshot catches it."),
        ("Deep-dive",    "get_cpi_history",               "STRUCTURAL_DECLINE or STEP_CHANGE",
         "Month-by-month CPI trajectory. Distinguishes structural decline (same direction 6+ periods) from a step-change event — different failure modes, different FLAG rationale."),
        ("Deep-dive",    "get_pm_eac_history",            "PM credibility UNLIKELY or NOT_CREDIBLE",
         "PM's submitted EAC vs system EAC over 6 months. Persistent gap of 10–15% indicates systematic optimism bias independent of current period performance."),
        ("Deep-dive",    "get_prior_explanations",        "REPEATED_NARRATIVE signal only",
         "3 months of PM narrative text. Detects whether the same reassurance phrases appear across months while CPI continues to worsen."),
        ("Decision",     "write_decision",                "Once per agent — terminates the loop",
         "Commits FLAG, ACCEPT, or NEEDS_EVIDENCE. Comment must cite specific numbers. Agent is enforcement-isolated to its own project ID — cross-project writes return an error."),
    ]

    CAT_COLORS = {
        "Portfolio":    ("#1d4ed8", "#eff6ff"),
        "Investigation":("#92400e", "#fffbeb"),
        "Deep-dive":    ("#166534", "#f0fdf4"),
        "Decision":     ("#5b21b6", "#faf5ff"),
    }

    tbl = '<table class="tbl"><thead><tr>'
    for h in ["Category", "Tool", "When called", "Returns"]:
        tbl += f'<th>{h}</th>'
    tbl += '</tr></thead><tbody>'

    for i, (cat, name, trigger, desc) in enumerate(TOOLS_DEF):
        fc, bc = CAT_COLORS.get(cat, ("#374151", "#f9fafb"))
        bg = "#fff" if i % 2 == 0 else "#fafafa"
        tbl += (
            f'<tr style="background:{bg}">'
            f'<td style="white-space:nowrap">'
            f'<span class="pill" style="background:{bc};color:{fc}">{cat}</span></td>'
            f'<td><code style="font-size:0.75rem;color:#111827;font-weight:600">{name}</code></td>'
            f'<td style="color:#6b7280;font-size:0.73rem">{trigger}</td>'
            f'<td style="color:#374151;font-size:0.75rem;line-height:1.5">{desc}</td>'
            f'</tr>')
    tbl += '</tbody></table>'
    st.markdown(tbl, unsafe_allow_html=True)
