"""
Generate NIG Forecast Challenge Desk — Technical Design Review PDF
All portfolio figures derived directly from the mock data (extract_stats.py).
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)

# ── Colour palette ────────────────────────────────────────────
NIG_DARK  = HexColor("#0f2027")
NIG_BLUE  = HexColor("#1a365d")
NIG_MED   = HexColor("#2b6cb0")
NIG_LIGHT = HexColor("#ebf8ff")
RED       = HexColor("#c53030")
RED_BG    = HexColor("#fff5f5")
GREEN     = HexColor("#276749")
GREEN_BG  = HexColor("#f0fff4")
AMBER     = HexColor("#b7791f")
AMBER_BG  = HexColor("#fffaf0")
GREY      = HexColor("#4a5568")
LGREY     = HexColor("#718096")
LLGREY    = HexColor("#edf2f7")
W         = white

ss = getSampleStyleSheet()

def S(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=ss[parent], **kw)

# ── Type styles ───────────────────────────────────────────────
COVER_TITLE = S("CoverTitle", fontSize=28, textColor=W,                    leading=34, spaceAfter=6,  fontName="Helvetica-Bold")
COVER_SUB   = S("CoverSub",   fontSize=14, textColor=HexColor("#90cdf4"), leading=20,               fontName="Helvetica")
COVER_META  = S("CoverMeta",  fontSize=10, textColor=HexColor("#a0aec0"), leading=16,               fontName="Helvetica")

H1 = S("H1", fontSize=17, textColor=NIG_BLUE, leading=22, spaceBefore=20, spaceAfter=6,  fontName="Helvetica-Bold")
H2 = S("H2", fontSize=13, textColor=NIG_MED,  leading=18, spaceBefore=14, spaceAfter=4,  fontName="Helvetica-Bold")
H3 = S("H3", fontSize=11, textColor=GREY,     leading=16, spaceBefore=10, spaceAfter=3,  fontName="Helvetica-Bold")

BODY = S("Body", fontSize=10, leading=15, spaceAfter=6,  alignment=TA_JUSTIFY, textColor=HexColor("#2d3748"))
BULL = S("Bull", fontSize=10, leading=15, spaceAfter=4,  leftIndent=14, firstLineIndent=-10, textColor=HexColor("#2d3748"))
MONO = S("Mono", fontSize=9,  leading=14, fontName="Courier", textColor=NIG_BLUE, backColor=HexColor("#f7fafc"), spaceAfter=4)
CALL = S("Call", fontSize=10, leading=15, textColor=HexColor("#2d3748"), leftIndent=8, rightIndent=8)
SMAL = S("Smal", fontSize=8.5, leading=13, textColor=LGREY)
NOTE = S("Note", fontSize=9,  leading=14, textColor=GREY, alignment=TA_JUSTIFY)

def h1(t): return Paragraph(t, H1)
def h2(t): return Paragraph(t, H2)
def h3(t): return Paragraph(t, H3)
def p(t):  return Paragraph(t, BODY)
def b(t):  return Paragraph(f"<bullet>•</bullet> {t}", BULL)
def note(t): return Paragraph(t, NOTE)
def sp(n=8): return Spacer(1, n)
def hr(): return HRFlowable(width="100%", thickness=0.5, color=HexColor("#cbd5e0"), spaceAfter=4, spaceBefore=4)

def callout(text, color=NIG_LIGHT, border=NIG_MED):
    data = [[Paragraph(text, CALL)]]
    t = Table(data, colWidths=[15.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("BOX",           (0,0),(-1,-1), 0.8, border),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
    ]))
    return t

def grid(headers, rows, col_widths=None, row_colors=None):
    data = [[Paragraph(f"<b>{h}</b>", S("th", fontSize=9, textColor=W, fontName="Helvetica-Bold"))
             for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), S("td", fontSize=9, leading=13, textColor=HexColor("#2d3748")))
                     for c in row])
    if not col_widths:
        col_widths = [15.5*cm / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths)
    bg_colors = row_colors if row_colors else [W, LLGREY]
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  NIG_BLUE),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), bg_colors),
        ("BOX",           (0,0),(-1,-1), 0.5, HexColor("#cbd5e0")),
        ("INNERGRID",     (0,0),(-1,-1), 0.3, HexColor("#e2e8f0")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 7),
        ("RIGHTPADDING",  (0,0),(-1,-1), 7),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    return t

# ============================================================
# DOCUMENT
# ============================================================
story = []

# ── COVER ────────────────────────────────────────────────────
inner = [
    Paragraph("NorthStar Infrastructure Group", COVER_META),
    Spacer(1, 12),
    Paragraph("AI Engineer Case Assignment", COVER_TITLE),
    Paragraph("Forecast Challenge Desk — Technical Design Review", COVER_SUB),
    Spacer(1, 28),
    Paragraph("Finance Cluster · FIN · Agentic Operations Programme", COVER_META),
    Spacer(1, 8),
    Paragraph("Prepared by: Aymane Lamyaghri   |   June 2025", COVER_META),
]
cover_tbl = Table([[inner]], colWidths=[17*cm], rowHeights=[22*cm])
cover_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0),(-1,-1), NIG_DARK),
    ("LEFTPADDING",   (0,0),(-1,-1), 40),
    ("RIGHTPADDING",  (0,0),(-1,-1), 40),
    ("TOPPADDING",    (0,0),(-1,-1), 60),
    ("BOTTOMPADDING", (0,0),(-1,-1), 40),
    ("VALIGN",        (0,0),(-1,-1), "TOP"),
]))
story.append(cover_tbl)
story.append(PageBreak())

# ── DOCUMENT INFO TABLE ──────────────────────────────────────
meta_rows = [
    ["Document",  "Technical Design Review — Forecast Challenge Desk"],
    ["Cluster",   "FIN · Finance"],
    ["Workflow",  "Monthly Project Forecast Challenge & EAC Review"],
    ["Prototype", "Working Streamlit app · Python 3.11 · Anthropic Claude Haiku 4.5"],
    ["Status",    "Prototype — not production deployed"],
    ["Date",      "June 2025"],
]
meta_data = [[Paragraph(f"<b>{r[0]}</b>", S("mk", fontSize=9, textColor=GREY)),
              Paragraph(r[1], S("mv", fontSize=9, textColor=HexColor("#2d3748")))]
             for r in meta_rows]
meta_tbl = Table(meta_data, colWidths=[4*cm, 12*cm])
meta_tbl.setStyle(TableStyle([
    ("ROWBACKGROUNDS",(0,0),(-1,-1),[W, LLGREY]),
    ("BOX",          (0,0),(-1,-1), 0.5, HexColor("#cbd5e0")),
    ("INNERGRID",    (0,0),(-1,-1), 0.3, HexColor("#e2e8f0")),
    ("TOPPADDING",   (0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
    ("LEFTPADDING",  (0,0),(-1,-1), 8), ("RIGHTPADDING", (0,0),(-1,-1),8),
]))
story += [sp(4), meta_tbl, sp(16)]

# ── PORTFOLIO SNAPSHOT CALLOUT ────────────────────────────────
story.append(callout(
    "<b>Prototype portfolio (all figures derived from mock data):</b>  "
    "20 projects · $970M total BAC · $1,080M system EAC · "
    "$109M portfolio exposure (+11.3%) · "
    "8 projects flagged ESCALATE · 3 CHALLENGE · 7 ACCEPT · 2 NEEDS_EVIDENCE · "
    "$29.8M in hidden change orders across 8 projects.",
    color=NIG_LIGHT, border=NIG_MED
))
story.append(sp(16))

# ============================================================
# TASK 1 — WORKFLOW SELECTION & PROTOTYPE
# ============================================================
story += [h1("Task 1 — Finance Workflow: Forecast Challenge Desk"), hr()]

story += [h2("1.1  Workflow Selection Rationale"), p(
    "The selected workflow is the <b>monthly EAC (Estimate at Completion) forecast review</b>, "
    "known internally as the Forecast Challenge Desk. Every month, Project Managers across NIG's "
    "portfolio submit their revised project cost forecasts to Finance. A Finance Controller must "
    "review each submission, challenge unrealistic forecasts, and escalate the highest-risk projects "
    "before month-end close."
), p(
    "Three properties made this workflow the right choice. <b>Volume and time pressure:</b> with "
    "50–200+ active projects across a large infrastructure firm, a Controller spends two to three "
    "days per cycle on manual review — a bottleneck that compounds at NIG scale. "
    "<b>Financial materiality of failure:</b> a missed escalation on a project heading for a "
    "$40M overrun has direct P&amp;L consequences that a misrouted invoice does not. One such "
    "miss likely exceeds the total cost of this programme. <b>Structured, defensible decision "
    "taxonomy:</b> EVM data is quantitative, the three decision labels map cleanly to real "
    "actions taken by Controllers, and evidence can always be cited in specific dollar figures "
    "rather than qualitative judgement."
)]

story += [h2("1.2  The Problem Being Solved"), p(
    "Without tooling, a Controller reviewing 20 submissions must manually:"
)]
for bl in [
    "Export EVM data from the project controls system (Oracle Primavera P6, SAP PS, or equivalent) — typically a manual pivot table exercise with no audit trail",
    "Cross-reference each PM's submitted EAC against system-derived estimates and assess credibility — a task requiring 20–40 minutes per project for experienced Controllers",
    "Detect non-obvious failure patterns: a project showing CPI 1.01 can mask SPI 0.82 and $1.65M in outstanding acceleration invoices; a project-level CPI 0.936 can conceal a Civil & Structural package at CPI 0.610 representing 90% of total exposure",
    "Audit the change order register for each project — PMs routinely omit pending variations from submitted EAC, representing $29.8M in undisclosed exposure across 8 of 20 prototype projects",
    "Identify systematic optimism bias across 6 months of PM submissions, not just the current period",
    "Document reasoning for escalation and audit purposes before the finance committee deadline",
]:
    story.append(b(bl))

story += [sp(4), p(
    "At NIG's projected scale of 200 projects across 10+ business units and 12 cycles per year, "
    "this manual process requires either a disproportionate headcount investment or a consistent "
    "reduction in oversight depth. Both outcomes carry unacceptable financial risk."
)]

story += [h2("1.3  Future-State Workflow"), p(
    "The Forecast Challenge Desk runs as a structured first-pass at the opening of each monthly "
    "review cycle. The Controller's role shifts from data extraction and pattern detection to "
    "decision review and escalation — the work that requires human judgement."
)]
for step, desc in [
    ("T+0 · Ingestion",           "EVM snapshot exported from project controls system. PM narratives and change order updates submitted via structured form with required schema fields."),
    ("T+30s · Parallel agent run", "20 independent agents run simultaneously. Each investigates one project using up to 7 specialised tools and writes a FLAG / ACCEPT / NEEDS_EVIDENCE decision with cited evidence."),
    ("T+2h · Controller review",  "Controller reviews agent decisions with full investigation trace visible. Approves, overrides, or escalates each decision. Override is always available and requires no justification."),
    ("T+2h · Audit trail sealed",  "All decisions — agent-generated and Controller-modified — logged to immutable audit record with timestamps, user IDs, tool call traces, and cited evidence strings."),
]:
    story.append(b(f"<b>{step}:</b> {desc}"))

story += [sp(8), callout(
    "<b>Design principle:</b> The agent does not make binding decisions. It is a structured "
    "evidence-gathering first-pass that reduces the surface area a skilled Controller must cover. "
    "Every decision requires human review before action. The system is designed to be overridden — "
    "a Controller who never disagrees with the agent is a monitoring failure, not a success.",
    color=NIG_LIGHT, border=NIG_MED
), sp(10)]

story += [h2("1.4  Prototype Scope and Data Design")]
story += [p(
    "The prototype covers the complete monthly review cycle end-to-end across a simulated "
    "20-project portfolio. The data is deliberately engineered to surface the hard parts of "
    "the forecasting problem, not to make the agent look good."
)]
for f in [
    "20 infrastructure projects spanning 5 regions (Europe, Middle East, Asia-Pacific, Africa, North America), 6 project types, and 3 contract structures (10 lump sum, 7 reimbursable, 3 target cost)",
    "Per-project EVM histories of up to 22 periods with realistic CPI/SPI series, rebaseline events, and S-curve planned progress — total BAC $970.3M, system EAC $1,079.5M",
    "7 distinct failure scenarios: structural CPI degradation, rebaseline masking, WBS-level disaster hidden at project level, SPI trap, contingency exhaustion, step-change event (site discovery), near-completion lock-in",
    "5 hard cases designed to defeat naive threshold classifiers: P07 (CPI 1.010 / SPI 0.820 — cost looks fine, acceleration imminent), P13 (CPI 0.945 — not alarming, but 97% contingency consumed at 40% complete), P06 (project CPI 0.936 masking Civil & Structural at 0.610), P17 (PM EAC $95M requires future CPI 0.931 from a base of 0.762), P01 (same reassurance phrase across 3 months while CPI declined from 0.855 to 0.820)",
    "Change order register: 8 projects carry hidden material COs totalling $29.8M not included in PM EAC — including $6.3M on P06 (foundation piling and civil re-sequencing), $6.0M on P17 (FX exposure and swamp crossing rework), $3.6M on P01 (disputed jacket interface rework and offshore campaign extension)",
    "Ground truth decision labels for 6 consecutive back-test cycles (Jun–Nov 2024) derived from EVM analysis, enabling accuracy measurement across the full review window",
    "PM narratives for November 2024 hand-crafted per project; prior months generated deterministically from EVM data using a calibrated optimism-factor model",
]:
    story.append(b(f))

story.append(PageBreak())

# ============================================================
# TASK 2 — TECHNICAL DESIGN REVIEW
# ============================================================
story += [h1("Task 2 — Technical Design Review"), hr()]

story += [h2("2.1  Architecture Overview"), p(
    "The system is a single-tier application with no persistent backend. This is an intentional "
    "prototype constraint: the architecture must demonstrate reasoning quality and decision accuracy, "
    "not infrastructure maturity. Each production component is identified in Section 3."
)]

arch_rows = [
    ["Layer",         "Component",                "Technology",                  "Role"],
    ["Presentation",  "Web UI",                   "Streamlit 1.x",               "Month selector, run trigger, live decision streaming, investigation trace, Data and Tools tabs"],
    ["Orchestration", "Run orchestrator",          "Python / concurrent.futures", "Calls shared portfolio scan once; fans out 20 mini-agent threads; aggregates decisions in real time"],
    ["Agent",         "Project mini-agent (×20)", "Custom ReAct loop",           "Per-project: up to 14 turns, 10 available tools, writes exactly one decision. Isolated — cannot read or write another project's decision"],
    ["Tools",         "EVM tools (×10)",           "Deterministic Python",        "Pure mathematics, text formatting, and register lookups. The LLM never generates a number — it only interprets numbers the tools return"],
    ["Data",          "Mock portfolio",            "Python in-memory",            "20 projects × up to 22 EVM periods × 8 WBS packages + change order register + PM narratives"],
    ["LLM",           "claude-haiku-4-5-20251001", "Anthropic API",               "Classification and evidence synthesis only. Tools return data; the model decides which tools to call and what the results mean"],
]
story.append(grid(arch_rows[0], arch_rows[1:], [2.6*cm, 3.4*cm, 3.8*cm, 5.7*cm]))
story.append(sp(10))

story += [h2("2.2  Agent Architecture — 20 Parallel Independent Agents"), p(
    "The core architectural decision is to run <b>20 independent single-project agents in parallel</b> "
    "rather than one sequential agent iterating over the full portfolio."
), p(
    "<b>Why independent:</b> Each FLAG/ACCEPT/NEEDS_EVIDENCE decision depends entirely on a single "
    "project's EVM data, PM narrative, and change order register. No cross-project reasoning is "
    "required for the classification task itself. A single sequential agent would accumulate context "
    "window overhead linearly with each project, increasing cost and latency with no accuracy benefit. "
    "Independence also means a stalled or errored project investigation cannot block the other 19."
), p(
    "<b>Why parallel:</b> Wall-clock time falls from the sum of all investigation times (~120 seconds "
    "sequential) to the duration of the deepest single investigation (~25–40 seconds). With 10 "
    "concurrent threads across 20 projects, the bottleneck is the most complex project — P17 or P10 "
    "with 5–7 tool calls — not the total queue. This is what makes the 30-second review cycle possible."
)]

story += [h3("ReAct Loop — Per-Project Execution")]
for step, desc in [
    ("Shared context injection",  "Orchestrator calls load_all_summaries and get_portfolio_exposure_ranking once before any agent starts. Both results are injected as text context into every agent's first message. Every agent therefore knows the portfolio risk distribution before investigating its own project."),
    ("Signal-based routing",      "Agent reads the !! signal flags in the portfolio summary for its assigned project. Projects marked [clean] (CPI > 0.97, gap < 3%, no signals) are accepted immediately — no further tool calls. Projects with any !! signal enter investigation."),
    ("Adaptive tool selection",   "Agent calls get_project_detail as the first investigation tool. Each subsequent tool call is determined by what the previous tool revealed — a CO alert triggers get_change_order_exposure; HIDDEN_WBS triggers get_wbs_cost_breakdown; SPI_TRAP triggers get_spend_acceleration. The agent never calls all tools; it calls only those that are warranted."),
    ("Decision and termination",  "Agent calls write_decision exactly once with FLAG / ACCEPT / NEEDS_EVIDENCE and a comment that must cite specific dollar amounts and CPI values. The agent is isolated to its assigned project ID — an attempt to write a decision for another project returns an error. Max 14 turns enforced as a hard safety limit."),
]:
    story.append(b(f"<b>{step}:</b> {desc}"))

story += [sp(8), h2("2.3  Tool Design — Deterministic by Principle"), p(
    "The 10 tools are the most important architectural element. All are <b>pure deterministic Python "
    "functions</b> — they compute EVM mathematics, format structured text, and perform register lookups. "
    "The LLM produces no numbers. Every figure the agent cites in its decision comment was returned "
    "by a tool call. This makes every decision auditable: the evidence trail is the tool call sequence."
)]

tool_rows = [
    ["Tool", "Phase", "Trigger", "Evidence it provides"],
    ["load_all_summaries",           "Setup",        "Once — shared",
     "Portfolio scan: CPI, SPI, EAC gap, and computed signal flags for all 20 projects. Establishes investigation routing before any per-project work begins."],
    ["get_portfolio_exposure_ranking","Setup",        "Once — shared",
     "All 20 projects sorted by $ at risk (System EAC − BAC). Provides proportionality calibration — a $2M gap on a $10M project ranks differently to a $2M gap on a $135M project."],
    ["get_project_detail",           "Investigation","Any !! signal",
     "Full EVM snapshot: CPI/SPI with structural trend verdict, EAC credibility rating, implied future CPI required by PM forecast, TCPI to BAC, per-package WBS CPI, contingency status, PM narrative, and CO alert if undisclosed material COs exist."],
    ["get_change_order_exposure",    "Deep-dive",    "CO alert in project detail",
     "Full CO register: each CO's value, status, whether included in PM EAC, and explanatory note. Computes adjusted EAC if all hidden COs materialise. Critical on REIMBURSABLE contracts where every hidden CO is a direct client liability."],
    ["get_wbs_cost_breakdown",       "Deep-dive",    "HIDDEN_WBS (Civil CPI < 0.78)",
     "Projected overrun per package at completion in dollars. Converts an abstract CPI signal into a concrete figure: Civil CPI 0.610 → $13.4M projected overrun, 90% of total project exposure on P06."],
    ["get_spend_acceleration",       "Deep-dive",    "SPI_TRAP (SPI < 0.88, CPI clean)",
     "Monthly AC increment trend over last 6 periods. Acceleration spending shows up here 1–2 periods before CPI worsens, because acceleration invoices arrive after the monthly EVM snapshot. Critical for P07 where $1.65M in premium-rate invoices are outstanding."],
    ["get_cpi_history",              "Deep-dive",    "STRUCTURAL_DECLINE or STEP_CHANGE",
     "Month-by-month CPI trajectory with direction, consecutive-period count, and step-change identification. Distinguishes structural decline (same direction 6+ periods — almost never recovers) from event-driven drop (discrete incident, potentially recoverable once absorbed)."],
    ["get_pm_eac_history",           "Deep-dive",    "Credibility: UNLIKELY or NOT_CREDIBLE",
     "PM submitted EAC vs system EAC for each of the last 6 months, with gap percentage and bias label. A PM who is 12–18% below system EAC for 5 consecutive months is exhibiting systematic denial, not a one-period error."],
    ["get_prior_explanations",       "Deep-dive",    "REPEATED_NARRATIVE signal",
     "Three months of PM narrative text side by side, with automated detection of repeated reassurance phrases. Identifies PMs copying forward the same explanation while CPI continues to deteriorate."],
    ["write_decision",               "Decision",     "Once — terminates investigation",
     "Commits FLAG / ACCEPT / NEEDS_EVIDENCE with evidence comment. Enforces project isolation — agent cannot write for any project other than its assigned ID. Decision returned to orchestrator."],
]
story.append(grid(tool_rows[0], tool_rows[1:], [3.5*cm, 1.8*cm, 2.8*cm, 7.4*cm]))
story.append(sp(10))

story += [h2("2.4  Signal Computation — Pre-LLM Filtering"), p(
    "Before the LLM is involved in any project, the portfolio scanner computes a set of "
    "deterministic signals from EVM mathematics. These signals drive investigation routing "
    "and are the primary mechanism by which the agent avoids hallucinated risk assessments."
)]

sig_rows = [
    ["Signal", "Condition", "What it detects"],
    ["EARLY_PHASE",            "&lt; 4 periods or &lt; 20% complete",
     "Insufficient data for structural assessment. Routes to NEEDS_EVIDENCE without investigation."],
    ["EAC_GAP_LARGE",          "PM EAC &gt; 10% below system EAC",
     "Substantial optimism gap. Forces get_project_detail regardless of CPI."],
    ["STRUCTURAL_DECLINE(Np)", "CPI declining for N consecutive periods",
     "Self-reinforcing deterioration. 6+ periods is a near-certain FLAG."],
    ["STEP_CHANGE(Pp)",        "CPI drop &gt; 0.08 in a single period",
     "Discrete event. Forces investigation of root cause vs ongoing trend."],
    ["CONTINGENCY_N%",         "Contingency consumed &gt; 80% of budget",
     "Buffer depletion. Critical when project % complete is much lower than contingency % consumed."],
    ["SPI_TRAP",               "CPI &gt; 0.99 AND SPI &lt; 0.88",
     "Cost looks fine; schedule badly behind. Acceleration costs not yet invoiced."],
    ["IMPLIED_FUTURE_CPI",     "PM needs &gt; 10% CPI recovery from current base",
     "PM forecast requires future performance the project has never achieved. Graded UNLIKELY or NOT_CREDIBLE."],
    ["CONT_AHEAD",             "Contingency % consumed &gt; project % complete + 20",
     "Contingency consumed faster than progress. No buffer remaining for the majority of scope."],
    ["HIDDEN_WBS",             "Civil CPI &lt; 0.78 while project CPI &gt; 0.88",
     "Package-level disaster masked at project level by better-performing packages."],
    ["REPEATED_NARRATIVE",     "Watch phrase appears in current + 1 or more prior narratives",
     "PM copy-pasting reassurances while CPI worsens. Keywords: recovery expected, manageable, contingency remains."],
    ["REBASELINED",            "BAC increased mid-project",
     "Prior overrun absorbed into new baseline. Post-rebaseline metrics may look artificially clean."],
]
story.append(grid(sig_rows[0], sig_rows[1:], [3.2*cm, 3.8*cm, 8.5*cm]))
story.append(sp(10))

story += [h2("2.5  Model Selection and Rationale")]
story += [p(
    "<b>Selected: claude-haiku-4-5-20251001.</b> The task is structured classification with "
    "deterministic tool outputs and explicit decision criteria. Haiku's reasoning quality is "
    "sufficient for this task when the decision framework is well-specified in the system prompt "
    "and tool outputs are structured text, not open-ended generation. The cost and latency "
    "advantages are substantial at any realistic review frequency."
)]

model_rows = [
    ["Model",              "Latency/project", "Cost/20-proj run", "Suitability for this task",        "Verdict"],
    ["claude-haiku-4-5",   "2–4s",            "~$0.08",           "Sufficient — structured classification with deterministic tools", "Selected"],
    ["claude-sonnet-4-6",  "5–10s",           "~$0.80",           "Marginal quality gain on borderline CPI cases; 10× cost",         "Reserve for calibration"],
    ["claude-opus-4-8",    "12–25s",          "~$4.00",           "Useful for building few-shot example set; overkill for production", "Not for production runs"],
    ["GPT-4o",             "5–12s",           "~$0.90",           "Viable; not benchmarked against this task",                       "Fallback if Anthropic unavailable"],
]
story.append(grid(model_rows[0], model_rows[1:], [3.2*cm, 2.4*cm, 3*cm, 4.8*cm, 2.1*cm]))

story += [sp(8), callout(
    "<b>Model pinning policy:</b> The production system must pin to a specific model version string "
    "(e.g. claude-haiku-4-5-20251001) and run a regression test suite against the 20 known cases "
    "before accepting any model update. Anthropic's model updates are not breaking in the traditional "
    "sense, but classification behaviour on borderline cases (CPI 0.88–0.92) can shift between versions.",
    color=AMBER_BG, border=AMBER
)]

story += [sp(10), h2("2.6  Build vs Buy — Explicit Decisions")]
bvb_rows = [
    ["Component",          "Decision",              "Rationale and trade-off"],
    ["LLM inference",      "Buy (Anthropic API)",   "No alternative at prototype stage. The API delivers the required reasoning quality. Vendor lock-in risk is real but manageable — the agent's tool-call interface is model-agnostic and could be redirected to GPT-4o or Gemini with prompt adjustments only."],
    ["Agent framework",    "Build (custom)",        "LangChain and CrewAI add abstraction layers that obscure tool-call sequences, make debugging harder, and introduce dependencies that must be maintained independently of the underlying model API. The custom ReAct loop is under 100 lines and fully inspectable. At prototype stage, debuggability outweighs convenience."],
    ["EVM mathematics",    "Build",                 "Domain-specific functions: eac_cpi(), tcpi_bac(), analyse_cpi_trend(), detect_step_change(). No off-the-shelf library covers construction EVM at this granularity. These functions are the core intellectual property of the tool layer — they must be owned, tested, and versioned by NIG."],
    ["UI",                 "Buy (Streamlit)",       "Fastest path to an interactive prototype suitable for internal demo. Not appropriate for production: no multi-user auth, no session isolation, not embeddable in Teams or SharePoint. Replacement path is clear: FastAPI backend + React frontend or Teams tab."],
    ["Parallelism",        "Build (stdlib)",        "concurrent.futures.ThreadPoolExecutor requires no external dependency and is sufficient for 20-thread fan-out. Production replacement (Section 3) uses a managed queue for retry logic and dead-letter handling."],
    ["Vector store / RAG", "Not built",             "No historical decisions exist at prototype stage. RAG becomes a genuine requirement at 6+ months of production data. See Section 2.9 for the implementation plan."],
    ["Auth / RBAC",        "Not built",             "Out of scope for prototype. Required before any Controller uses the system on real data. See Section 3.2."],
    ["Persistent storage", "Not built",             "Session state only. Production requires an immutable audit trail database. See Section 3.3."],
    ["LLM observability",  "Not built",             "No tracing at prototype stage. Production requires per-run metrics: token cost, latency per tool, error rate, prompt version. Langfuse or LangSmith. See Section 3.3."],
]
story.append(grid(bvb_rows[0], bvb_rows[1:], [3.2*cm, 2.8*cm, 9.5*cm]))
story.append(sp(10))

story += [h2("2.7  Evaluation Strategy and Results")]
story += [p(
    "Quality is measured against per-cycle ground truth labels embedded in the mock data. "
    "Labels represent expert classification of each project based on EVM signals, PM narrative "
    "credibility, contingency status, and change order exposure. Six consecutive cycles "
    "(Jun–Nov 2024) provide the back-test window."
)]

eval_rows = [
    ["Metric",             "Definition",                                       "Target",  "Kill threshold"],
    ["Accuracy",           "Decisions matching ground truth / 20",             "85%+",    "&lt; 75% for 3 consecutive cycles"],
    ["False Accept Rate",  "True FLAG/ESCALATE decisions accepted / total true flags", "&lt; 10%", "&gt; 15% for 3 consecutive cycles"],
    ["Investigation depth","Average tool calls on flagged projects",           "3–6",     "&lt; 2 (under-investigation) or &gt; 8 (over-investigation)"],
]
story.append(grid(eval_rows[0], eval_rows[1:], [3.2*cm, 6.3*cm, 2*cm, 4*cm]))

story += [sp(8), p(
    "<b>Ground truth distribution (November 2024):</b> Of 20 projects, 8 are labelled "
    "ESCALATE, 3 CHALLENGE, 7 ACCEPT, and 2 NEEDS_EVIDENCE. The 11 projects requiring "
    "action represent $109.2M in portfolio exposure above BAC. A naive classifier that "
    "flags everything would achieve 55% accuracy with a 0% false accept rate; "
    "a naive classifier that accepts everything would achieve 45% accuracy with a 100% "
    "false accept rate. Neither is useful. The target accuracy of 85%+ requires the agent "
    "to correctly distinguish: projects with acceptable variance (P04, P12, P20) from "
    "projects with serious risk hidden behind acceptable headline numbers (P06, P07, P13)."
)]

story += [sp(8), callout(
    "<b>Primary metric: False Accept Rate.</b> Accepting a project that will overrun by $40M "
    "is a categorically worse outcome than flagging a project that turns out to be fine. "
    "A false flag costs a Controller 30 minutes of investigation. A false accept costs NIG "
    "potentially tens of millions of dollars and the credibility of the finance oversight function. "
    "The asymmetry is intentional and built into every design decision in the evaluation framework.",
    color=RED_BG, border=RED
)]

story += [sp(10), h2("2.8  Hard Cases — Where the System Is Tested")]
story += [p(
    "Five projects are specifically designed to defeat threshold-based classifiers. "
    "These are the cases where the agent earns its value — any rule-based system would "
    "misclassify at least two of them."
)]

hard_rows = [
    ["Project", "Scenario", "Why it defeats thresholds", "Key evidence the agent must find"],
    ["P07<br/>Manchester Roads",
     "SPI Trap",
     "CPI 1.010 — appears on budget. ACCEPTED by any CPI-only filter.",
     "SPI 0.820 + $1.65M outstanding acceleration invoices + 75% contingency consumed at 52% complete. get_spend_acceleration confirms spending +52% vs prior average."],
    ["P13<br/>Riyadh Hospital",
     "Contingency Lie",
     "CPI 0.945 — concerning but below most FLAG thresholds. PM states contingency remains available.",
     "97% contingency consumed at 40% complete. $2.3M in hidden M&amp;E design COs. CONT_AHEAD signal: 97% consumed vs 40% done."],
    ["P06<br/>Cairo Power Station",
     "Hidden WBS",
     "Project CPI 0.936 — moderate. M&amp;E CPI 1.080 masks the disaster underneath.",
     "Civil &amp; Structural CPI 0.610 [CRITICAL] -&gt; $13.4M projected overrun = 90% of total exposure. $6.3M in hidden foundation COs. get_wbs_cost_breakdown required."],
    ["P17<br/>Lagos Pipeline",
     "Impossible CPI",
     "CPI 0.762 is obviously bad — but the PM/system gap magnitude is the key finding.",
     "PM EAC $95M requires future CPI 0.931 from base 0.762 — NOT CREDIBLE. System EAC $123M. Gap $28M. $6.0M in hidden COs. 12-period structural decline confirmed by get_cpi_history."],
    ["P01<br/>North Sea Platform",
     "Repeated Narrative",
     "CPI 0.820, structural decline — flagged on numbers alone. Additional: PM credibility failure.",
     "Recovery expected as conditions improve appears in Oct, Nov, and Dec narratives while CPI fell from 0.838 to 0.820. PM EAC $50.2M vs system $57.8M. get_prior_explanations confirms 3-month pattern."],
]
story.append(grid(hard_rows[0], hard_rows[1:], [2.8*cm, 2.4*cm, 3.8*cm, 6.5*cm]))
story.append(sp(10))

story += [h2("2.9  Failure Modes Observed in Testing"), p(
    "The following failure modes were identified during prototype development. "
    "Each one motivated a specific tool or system prompt addition."
)]
for case, observed, fix in [
    ("SPI Trap (P07)",
     "Agent accepted P07 on roughly 1 in 6 runs before the spend acceleration tool existed. The CPI of 1.01 was sufficient evidence for ACCEPT when no schedule-cost correlation tool was available.",
     "Added get_spend_acceleration triggered by SPI_TRAP signal. Agent now sees monthly AC increments and the +52% acceleration vs prior average before deciding."),
    ("Borderline CPI (0.88–0.92)",
     "Projects in the 0.88–0.92 CPI band were inconsistently classified across runs. The same project would receive FLAG on one run and ACCEPT on another depending on which tool path the agent chose.",
     "Tightened the IMPLIED_FUTURE_CPI signal: when a PM's forecast requires more than 10% CPI improvement from current base, the signal is raised regardless of absolute CPI level. This forced consistent investigation of P04, P12, and P15."),
    ("Hidden WBS without quantification",
     "Before get_wbs_cost_breakdown was added, the agent could see Civil CPI 0.610 in project detail output but occasionally wrote FLAG comments without the dollar figure — Civil package is underperforming rather than $13.4M projected overrun on Civil and Structural.",
     "Added HIDDEN_WBS signal (Civil CPI below 0.78 while project CPI above 0.88) as a mandatory trigger for get_wbs_cost_breakdown. Comment quality improved — all FLAG decisions on WBS cases now cite dollar overrun."),
    ("Optimism bias accepted at face value",
     "Without PM EAC history, the agent occasionally accepted a PM narrative as plausible even when the gap between PM EAC and system EAC was persistent. The current period narrative can sound reasonable in isolation.",
     "Added get_pm_eac_history triggered when EAC credibility is UNLIKELY or NOT_CREDIBLE. The 6-month gap pattern makes the denial visible and provides specific language: 5 of 6 months PM was more than 10% below system EAC."),
    ("Early-phase over-investigation",
     "P05 and P11 (both NEEDS_EVIDENCE by ground truth) were occasionally investigated with 3–4 tool calls before the agent concluded they were too early to assess. Token cost only; decision was correct.",
     "Added EARLY_PHASE as an immediate routing flag: if triggered, agent receives explicit instruction to write NEEDS_EVIDENCE without calling any investigation tools. Eliminated the over-investigation pattern."),
]:
    story.append(b(f"<b>{case}:</b> {observed} <i>Fix: {fix}</i>"))

story.append(PageBreak())

# ── Section 2.10 and 2.11 ─────────────────────────────────────
story += [h2("2.10  Production Infrastructure Stack"), p(
    "The prototype is a single Python process with no external dependencies beyond the Anthropic API. "
    "Every in-memory component has a direct production replacement. The table below maps each "
    "prototype component to its production equivalent and explains the operational requirement driving the change."
)]

infra_rows = [
    ["Prototype",                 "Production replacement",              "Operational requirement"],
    ["In-memory mock data",       "ETL pipeline → PostgreSQL (versioned period snapshots)",
     "EVM data must be versioned by period — a re-run of June's review must use June's data, not today's. Overwriting current state is insufficient."],
    ["ThreadPoolExecutor",        "Celery + Redis or AWS SQS",
     "Managed job queue provides retry on API failure, dead-letter queue for stalled agents, and visibility into the queue state during a live run. Month-end deadline means a stalled thread cannot silently block completion."],
    ["Session state",             "PostgreSQL run history (immutable append-only)",
     "Every decision, tool call, and Controller override must be logged with user ID and timestamp. Compliance requirement — not optional. Re-runs of the same month must create new records, not overwrite."],
    ["Streamlit UI",              "FastAPI backend + React frontend or Teams tab",
     "Streamlit is single-user, not embeddable, and has no access control. Controllers need project-scoped views; PMs need read-only access to their own decision after review; leadership needs portfolio summary only."],
    ["os.getenv() API key",       "Azure Key Vault / AWS Secrets Manager",
     "Plaintext credentials in environment variables are unacceptable for a production financial system. Key rotation, access audit log, and least-privilege policy are required."],
    ["print() / logging",         "Langfuse or LangSmith",
     "Per-run observability: token cost, latency per tool call, prompt version hash, error rate by project. Without a tracing layer, cost attribution and prompt regression analysis are impossible."],
    ["No auth",                   "Azure AD / SSO with RBAC",
     "See Section 3.2. Role-based access is a hard requirement before any Controller uses the system on real project data."],
    ["No structured output check","Anthropic tool-use schema validation",
     "Agent comments currently enforced by prompt only. Production must validate that every FLAG comment contains a dollar amount and CPI value before the decision is accepted."],
]
story.append(grid(infra_rows[0], infra_rows[1:], [3.2*cm, 4.3*cm, 8*cm]))

story += [sp(10), h2("2.11  RAG and Historical Institutional Memory"), p(
    "Every decision in the prototype is made in isolation — the agent has no memory of prior months' "
    "outcomes or the Controller overrides that followed. This is acceptable at prototype stage where "
    "the data is static. It becomes a significant limitation in production."
)]
for item, detail in [
    ("Historical decision retrieval",
     "When investigating a project, retrieve the 3 most similar historical cases by EVM profile (CPI band, contract type, project type, WBS pattern). If all 3 similar cases overran materially after showing CPI 0.88 in month 11, that context strengthens a FLAG beyond what the current period's numbers alone justify."),
    ("PM performance index",
     "Index each PM's complete submission history: accuracy of EAC submissions, frequency of optimism bias, rate of change order disclosure. A PM with 8 consecutive optimistic submissions is a different risk than a first-time miss. Currently approximated by get_pm_eac_history over 6 months; a full index across projects and years is significantly more powerful."),
    ("False narrative pattern library",
     "Index prior PM narratives that preceded confirmed overruns. When a current narrative matches a known false-reassurance pattern semantically — not just by keyword — flag it. This replaces the current REPEATED_NARRATIVE keyword check with a richer semantic similarity approach."),
    ("Implementation",
     "pgvector (PostgreSQL extension) is the most pragmatic choice — NIG already needs PostgreSQL for audit trail, so a vector index avoids a separate infrastructure component. Pinecone or Weaviate are alternatives if embedding volume demands a dedicated vector service."),
]:
    story.append(b(f"<b>{item}:</b> {detail}"))

story += [sp(8), callout(
    "<b>When RAG becomes necessary:</b> After 6–12 months of production use, NIG will have 1,000+ "
    "labelled examples with known outcomes. Controller overrides will have accumulated into a "
    "real signal. Without retrieval, this institutional knowledge exists in a database the agent "
    "never consults. RAG is not a day-one requirement; it is a month-six requirement.",
    color=AMBER_BG, border=AMBER
)]

story += [sp(10), h2("2.12  Model Strategy — Prompting, Calibration, and Fine-tuning"), h3("Immediate: Prompt Engineering")]
for item, detail in [
    ("Few-shot examples in system prompt",
     "Embed 2–3 canonical examples in MINI_SYSTEM: one unambiguous FLAG with dollar figures cited, one clean ACCEPT, one NEEDS_EVIDENCE. Few-shot prompting is the highest-leverage improvement available without additional infrastructure. It directly addresses the borderline CPI 0.88–0.92 inconsistency observed in testing."),
    ("Chain-of-thought before write_decision",
     "Require the agent to state explicitly before committing: 'EVM signal: X. CO exposure: Y. PM credibility: Z. Therefore:'. This surfaces implicit reasoning, makes the Controller's review easier, and prevents the agent from writing a decision before synthesising all available evidence."),
    ("Critic agent for borderline cases",
     "For cases where the agent's comment contains hedging language, route to a second lightweight agent specifically prompted to challenge the first decision. Adversarial pass on borderline cases only — not all 20 — to control cost and latency. Target: cases where implied future CPI is in the UNLIKELY (not NOT_CREDIBLE) band."),
]:
    story.append(b(f"<b>{item}:</b> {detail}"))

story += [sp(6), h3("Medium-term: Fine-tuning (conditional on data volume)"), p(
    "Fine-tuning becomes viable once NIG has accumulated 2,000–5,000 labelled examples with known "
    "outcomes. Conditions and constraints:"
)]
for item, detail in [
    ("What to fine-tune on",
     "NIG-specific decision patterns: contract-type weighting (REIMBURSABLE projects warrant lower FLAG thresholds), regional EVM standards variation, NIG-specific CO terminology. The fine-tuned model handles classification; the base model handles tool selection and evidence synthesis."),
    ("When NOT to fine-tune",
     "If the labelled dataset is unbalanced by contract type, region, or project size, fine-tuning will overfit to the majority class and degrade performance on minority cases. Audit class balance before committing. With fewer than 1,000 examples, systematic few-shot prompting outperforms fine-tuning."),
    ("Alternative: systematic prompt optimisation",
     "DSPy-style optimisation automatically searches the space of system prompt variants against the ground truth set. This can close 60–70% of the gap between the current prompt and a fine-tuned model without requiring labelled training data. Should be evaluated before any fine-tuning investment."),
]:
    story.append(b(f"<b>{item}:</b> {detail}"))

story += [sp(8), callout(
    "<b>Recommendation:</b> Ship with few-shot examples and chain-of-thought in Month 1. "
    "Add the critic-agent pattern for borderline cases by Month 3. "
    "Evaluate fine-tuning only after 12 months of production data — the labelled set will not be "
    "large enough or diverse enough before that point to justify the training cost and the "
    "ongoing maintenance obligation of a custom model.",
    color=NIG_LIGHT, border=NIG_MED
)]

story.append(PageBreak())

# ============================================================
# TASK 3 — PRODUCTION READINESS
# ============================================================
story += [h1("Task 3 — Production Readiness"), hr(), p(
    "The gap between this prototype and a production capability at NIG is real and well-defined. "
    "It is not primarily a model problem. The model works. The gap is data access, identity, "
    "reliability under deadline, cost governance, and user adoption. This section is deliberately "
    "concrete about each component. A credible estimate follows each requirement."
)]

story += [h2("3.1  Data Integration — The Longest Lead-Time Item")]
story += [p(
    "Data integration is the most expensive, highest-risk, and longest lead-time item on the "
    "production path. Every agent signal is derived from EVM data. If that data is stale, "
    "incorrectly coded, or inconsistently structured across regions, the agent's signals "
    "are wrong — and they will be wrong with numerical precision, which is more dangerous "
    "than obviously wrong outputs."
)]
for item, detail in [
    ("EVM data source",
     "Oracle Primavera P6, SAP Project System, or equivalent. A monthly batch ETL must extract: period actuals (AC), planned values (PV), earned value (EV), and BAC for each active project. The ETL must retain and version period snapshots — a re-run of last month's review must use last month's data. Overwriting current state is insufficient. Estimated effort: 6–10 weeks depending on whether NIG has a consolidated data warehouse or requires project-by-project extraction."),
    ("PM submission channel",
     "Currently modelled as free-text narrative. Production requires a structured submission form (Microsoft Forms, SharePoint list, or custom web app) with required schema fields: submitted EAC, narrative text, risk note, and change order register update. Unstructured free-text is not compatible with the schema the agent tools depend on. Estimated effort: 2–4 weeks including rollout and training."),
    ("Change order register",
     "Currently a static mock register. Production requires a live integration with NIG's contract management system (Oracle Unifier, Aconex, or equivalent) to pull current CO status, value, and in-EAC flag. This integration must refresh daily — CO status changes between submission and the monthly review. Estimated effort: 4–8 weeks depending on API availability."),
    ("Historical period retention",
     "The PM EAC history tool requires 6 months of prior EVM snapshots per project. If NIG's data warehouse only retains current-period state, a 6-month backfill is required before the PM bias tools can operate. This is a one-time data migration exercise. Estimated effort: 2–3 weeks."),
    ("Data quality audit",
     "Before Phase 2 deployment, a retrospective audit must compare system-derived EAC against actual final costs for projects closed in the last 24 months. If the mean absolute error exceeds 15%, the EVM data quality is insufficient for the agent to operate reliably. A data remediation programme must precede deployment in that scenario."),
]:
    story.append(b(f"<b>{item}:</b> {detail}"))

story += [sp(8), callout(
    "<b>Risk:</b> NIG's EVM data quality is the single biggest production risk. If EVM is coded "
    "inconsistently across regions — different cost account structures, different period close "
    "disciplines, different rebaseline conventions — the agent will produce inconsistent results "
    "that Controllers cannot trust. The data audit in Phase 1 is not optional.",
    color=RED_BG, border=RED
)]

story += [sp(10), h2("3.2  Identity, Access Control, and Data Governance")]
story += [p(
    "PM submissions and EVM data are commercially sensitive. The system touches project cost "
    "data that, if accessed by wrong parties, creates both commercial and regulatory exposure. "
    "Access control must be implemented before any Controller uses the system on real project data."
)]
for item, detail in [
    ("Authentication",
     "Azure Active Directory / SSO. No local credentials at any layer. Role claim from the identity provider determines portfolio scope at query time. Anonymous access must be blocked at the infrastructure level, not just the application level."),
    ("Role-based access",
     "Four roles: Finance Controller (full portfolio read + decision override), Finance Leadership (portfolio summary read only, no project detail), Project Manager (read-only access to their own project's decision and evidence after the review is complete), System Administrator (configuration and audit log access only, no project data access)."),
    ("Anthropic API key management",
     "API key moved from .env file to Azure Key Vault or AWS Secrets Manager. Rotation policy: 90-day maximum key lifetime. All key access events logged. No plaintext credentials in application code, environment variables, or container images."),
    ("Data residency",
     "PM narratives and EVM data sent to the Anthropic API are subject to data processing agreements. EU projects may be subject to GDPR; Middle East projects may have local data sovereignty requirements; APAC projects vary by country. NIG's legal team must review Anthropic's data processing agreement and regional endpoint availability before deployment in each region. Mitigation: consider on-premise or private cloud LLM deployment for regions with strict data residency requirements."),
    ("Audit trail requirements",
     "Every agent decision, tool call sequence, Controller override, and user authentication event must be logged to an immutable, append-only audit store with: timestamp (UTC), user ID, action type, project ID, decision value, and evidence string. This is a compliance requirement in most jurisdictions where NIG operates, not an engineering preference."),
]:
    story.append(b(f"<b>{item}:</b> {detail}"))

story += [sp(10), h2("3.3  Reliability, Operations, and Month-End SLA")]
story += [p(
    "The monthly review has a hard deadline. A system that fails silently on the day of the "
    "finance committee is not a neutral outcome — it forces Controllers into emergency manual "
    "review under time pressure, which is exactly the condition most likely to produce missed flags."
)]
for item, detail in [
    ("API resilience",
     "All Anthropic API calls must use exponential backoff with jitter, circuit breaker pattern (open after 3 failures in 60 seconds, half-open after 2 minutes), and respect rate limit headers (429 responses must pause the thread pool, not terminate the run). Maximum retries: 4 per call. Timeout per call: 45 seconds."),
    ("Graceful degradation",
     "If the LLM is unavailable at run time, the system must: (1) complete all tool-only pre-computation, (2) mark all projects as MANUAL_REVIEW_REQUIRED, (3) notify the Controller immediately with the tool-computed signal summary, enabling manual triage prioritisation. Partial completion must be recoverable — completed decisions must not be re-run when the LLM recovers."),
    ("Run idempotency",
     "Re-running the same cycle must create a new run record with a new run ID. It must not overwrite the previous run. Controllers may need to compare agent decisions across re-runs when source data is corrected after initial run. The audit trail must be immutable even if the business decision changes."),
    ("Run monitoring and alerting",
     "Alert conditions: any run exceeding 3 minutes wall-clock time (LLM or network degradation), any cycle producing FAR > 10% (model drift or data quality event), any project producing zero tool calls on a flagged project (agent bypassing investigation), any Controller with override rate < 5% for two consecutive months (over-reliance risk)."),
    ("Operational runbook",
     "The on-call team must have a runbook covering: how to re-run a failed cycle, how to manually override all decisions if the system is unavailable, how to roll back a prompt deployment, and how to trigger the data quality audit. This runbook must be tested before Phase 3 rollout."),
]:
    story.append(b(f"<b>{item}:</b> {detail}"))

story += [sp(10), h2("3.4  Scalability Architecture")]
story += [p(
    "The current architecture scales to approximately 50 projects before the ThreadPoolExecutor "
    "approach reaches its limits (thread contention, rate limit saturation, session state overhead). "
    "Scaling to 200+ projects requires a distributed job queue architecture."
)]

scale_arch = [
    ["Component",             "Prototype (20 projects)",      "Phase 2 (50 projects)",            "Phase 3+ (200+ projects)"],
    ["Job dispatch",          "ThreadPoolExecutor (10 threads)", "Celery + Redis, 20 workers",    "Celery + SQS, auto-scaling workers"],
    ["LLM throughput",        "~10 concurrent API calls",     "~20 concurrent API calls",         "Rate-limit tier upgrade required"],
    ["Data layer",            "In-memory Python dict",        "PostgreSQL, single instance",      "PostgreSQL, read replicas + connection pooling"],
    ["Decision storage",      "Session state (ephemeral)",    "PostgreSQL run history table",     "PostgreSQL + archival to S3/Blob after 2 years"],
    ["UI",                    "Streamlit",                    "FastAPI + React (single-tenant)",  "FastAPI + React (multi-tenant, region-aware)"],
    ["Observability",         "Print statements",             "Langfuse basic tier",              "Langfuse/LangSmith enterprise, Grafana dashboards"],
    ["Deployment",            "Local Python process",         "Docker container, single region",  "Kubernetes (AKS/EKS), multi-region"],
    ["Auth",                  "None",                         "Azure AD SSO, single tenant",      "Azure AD SSO, multi-tenant RBAC"],
    ["Estimated run time",    "25–40 seconds",                "35–60 seconds",                    "60–120 seconds (rate-limit bound)"],
]
story.append(grid(scale_arch[0], scale_arch[1:], [3.2*cm, 3*cm, 3.3*cm, 6*cm]))

story += [sp(8), p(
    "Rate limits are the primary scaling constraint at 200+ projects. At current Anthropic tier "
    "pricing, 200 simultaneous tool-calling agents would require a dedicated rate limit tier or "
    "a capped concurrency strategy (e.g., 30 workers processing 200 projects in batches of 30, "
    "completing in 6–8 minutes). This is acceptable for a monthly review that starts hours before "
    "the committee meeting. It is not acceptable if the use case shifts to daily monitoring."
)]

story += [sp(10), h2("3.5  Cost at Scale — Full Programme Estimate")]
cost_rows = [
    ["Scenario",               "Projects", "Runs/yr", "LLM cost/run", "Annual LLM", "Primary cost driver"],
    ["Current prototype",      "20",        "12",      "~$0.08",       "~$1",        "Engineering time"],
    ["Phase 1 pilot (1 BU)",   "50",        "12",      "~$0.20",       "~$2",        "Data integration work"],
    ["Phase 3 FIN rollout",    "200",        "12",      "~$0.80",       "~$10",       "Maintenance and support overhead"],
    ["NIG-wide (all clusters)","500",        "12",      "~$2.00",       "~$24",       "Multi-region infra and RBAC complexity"],
    ["Daily monitoring (FIN)", "200",        "260",     "~$0.80",       "~$208",      "Rate limit tier upgrade, on-call model"],
]
story.append(grid(cost_rows[0], cost_rows[1:], [3.6*cm, 2*cm, 1.8*cm, 2.5*cm, 2.5*cm, 3.1*cm]))

story += [sp(8), p(
    "LLM API cost is negligible at every realistic NIG scale. The true programme cost is "
    "engineering: data integration ($150–250K, dominated by EVM system API work), auth and RBAC "
    "($75–100K), audit trail and compliance infrastructure ($50–75K), and ongoing maintenance "
    "(0.5 FTE/year for prompt governance, model updates, and data pipeline monitoring). "
    "<b>Total estimated programme cost: $300–450K one-time; $80–120K/year run rate.</b>"
)]

story += [sp(10), h2("3.6  Continuous Evaluation in Production"), p(
    "A classification system operating without outcome feedback will drift silently. "
    "The following pipeline must run alongside the production system from day one."
)]
for item, detail in [
    ("Six-month lag ground truth",
     "Every ACCEPT decision from Month N is automatically re-evaluated at Month N+6 against actual project cost-at-completion. If the project overran by more than 5% of BAC, the Month N ACCEPT is relabelled as a missed FLAG. This creates a growing, outcome-grounded training set that does not depend on manually constructed labels."),
    ("Prompt regression gate",
     "Before any prompt change is deployed to production, an automated test suite runs the agent against the 20 prototype cases and the accumulated back-test set. Deployment is blocked if accuracy drops below 83% or FAR rises above 12%. This gate prevents silent regressions from reaching Controllers."),
    ("Controller override signal",
     "Every Controller override is tagged: false FLAG (agent too aggressive) or missed FLAG (agent too lenient). Aggregated monthly, this surfaces systematic bias — for example, if the agent consistently over-flags reimbursable contracts in the Middle East region, that is a prompt calibration target, not a data problem."),
    ("Drift detection",
     "Track the FLAG/ACCEPT/NEEDS_EVIDENCE distribution month-over-month. A sudden shift — FLAG rate falling from 40% to 12% without a corresponding improvement in portfolio health — is a signal of prompt drift or data pipeline degradation, not genuine performance improvement."),
    ("Tooling",
     "MLflow or Weights &amp; Biases for prompt version tracking, metric history, and FAR trend. Each production run logs: model version, prompt hash, run timestamp, per-project decision, tool call count distribution, and Controller override within 48 hours of review."),
]:
    story.append(b(f"<b>{item}:</b> {detail}"))

story += [sp(8), h2("3.7  Multi-Region and Multi-Language Considerations"), p(
    "NIG operates across four major regions with different languages, regulatory environments, "
    "and EVM coding conventions. A production system must address each."
)]
for item, detail in [
    ("PM narrative language",
     "The prototype operates on English-language narratives. NIG's Middle East projects may submit in Arabic, West Africa projects in French, and APAC projects in Mandarin or Bahasa. Options: (1) pre-processing translation step using a multilingual model before the agent receives the narrative — adds latency and a translation error surface; (2) use a multilingual base model and accept some degradation in signal detection accuracy on non-English text. Recommendation: translation pre-processing for Phase 3, with language-specific accuracy benchmarking."),
    ("EVM coding standards",
     "Different NIG regions use different cost account structures and WBS conventions. The current WBS tool assumes a fixed 8-package structure. Production must support flexible WBS schemas with a mapping layer that normalises regional conventions to the tool's expected format."),
    ("Regulatory variation",
     "Some jurisdictions (EU, parts of APAC) may require disclosure that an AI system assisted in a financial oversight decision. The audit trail already provides this; the Controller sign-off step satisfies the human-in-the-loop requirement in most frameworks. Legal review required before Phase 3 regional rollout."),
    ("Data residency",
     "Anthropic's API processes data in the United States by default. GDPR (EU), PDPA (Singapore/Thailand), and local regulations in Middle East jurisdictions may restrict where PM narrative data can be sent for processing. Options: Anthropic EU endpoint (where available), on-premise LLM deployment for restricted regions, or data anonymisation before API submission. Legal review must precede each regional rollout."),
]:
    story.append(b(f"<b>{item}:</b> {detail}"))

story.append(PageBreak())

# ============================================================
# TASK 4 — EXECUTIVE SUMMARY
# ============================================================
story += [h1("Task 4 — Executive Summary"), hr()]

story.append(callout(
    "The Forecast Challenge Desk is an AI agent system that reviews NIG's monthly project cost "
    "forecasts in under 40 seconds, surfacing the highest-risk projects with specific, "
    "cited evidence before a Finance Controller begins their review. "
    "It reduces Controller review time from 2–3 days to 2–3 hours per cycle. "
    "On the 20-project mock portfolio — total BAC $970M, system-estimated exposure $109M above budget — "
    "the system identifies all 11 projects requiring action, including 5 hard cases that defeat "
    "any threshold-based classifier. LLM cost is under $10 per year at full NIG scale. "
    "The primary investment is data integration work: two engineers, two quarters. "
    "The system does not replace Finance Controllers. It gives them a structured, "
    "evidence-backed starting point — transparent, overridable, and auditable.",
    color=NIG_LIGHT, border=NIG_MED
))

story += [sp(12), h2("4.1  The Business Case in Three Numbers")]
for label, number, explanation in [
    ("$109M",   "Portfolio exposure above BAC on 20 prototype projects.",
     "This is the financial stake the monthly review is protecting. A manual review that misses two of the high-risk projects is not a minor inconvenience — it is a potential eight-figure exposure that reaches the P&L."),
    ("240 days", "Controller time recovered per year at 10 Controllers × 12 cycles.",
     "Conservative estimate: from 2 days to 2 hours per cycle per Controller. At senior finance salary rates, this represents $180–240K in recovered capacity per year — capacity that can be redirected to judgement-intensive analytical work."),
    ("< $10/yr", "LLM API cost at full NIG scale (200 projects, 12 cycles).",
     "The economics of this system are unusual. The constraint is not API cost — it is data integration engineering. Leadership should not allow LLM cost concerns to delay a programme whose API expense is smaller than a single Teams meeting."),
]:
    story.append(b(f"<b>{number}:</b> {label} {explanation}"))

story += [sp(10), h2("4.2  What the System Does and Does Not Do")]
for does, does_not in [
    ("Investigates every project with the same depth criteria every month, regardless of the Controller's workload or familiarity with the PM",
     "Make binding decisions — every output requires Controller review and sign-off"),
    ("Surfaces evidence that is difficult to find manually: spending acceleration before CPI worsens, WBS-level disasters hidden behind project-level averages, repeated narrative patterns, undisclosed change orders",
     "Access or process data outside the structured EVM and CO inputs — it cannot independently verify PM claims"),
    ("Cites specific dollar amounts and CPI values in every decision comment — not 'performance is declining' but 'CPI 0.762 for 12 periods; PM EAC requires 0.931 from 0.762 — NOT CREDIBLE; $6.0M CO not in EAC'",
     "Replace the Controller's relationship with the PM, their knowledge of project context, or their authority to escalate"),
    ("Provides a documented audit trail for every decision regardless of whether a human would have taken the same one",
     "Improve outcomes if EVM data is stale, inconsistently coded, or does not reflect actual project performance"),
]:
    story.append(b(f"<b>Does:</b> {does}. <b>Does not:</b> {does_not}."))

story += [sp(10), h2("4.3  Costs and ROI")]
roi_rows = [
    ["Category",                "Estimate",       "Notes"],
    ["LLM API (full NIG scale)","< $10/year",     "claude-haiku-4-5 at ~$0.80/run for 200 projects × 12 cycles"],
    ["Initial engineering",     "$300–450K",      "Data integration ($150–250K), auth and RBAC ($75–100K), audit trail and compliance ($50–75K) — 2 engineers × 2 quarters"],
    ["Ongoing maintenance",     "$80–120K/year",  "0.5 FTE for prompt governance, model updates, and data pipeline monitoring; cloud infrastructure; API costs"],
    ["Controller time recovered","240 days/year", "10 Controllers × 10 days/year recovered. At £800–1,000/day senior finance rate: £192–240K/year equivalent capacity"],
    ["Risk avoided",            "Hard to quantify","One missed escalation on a $40M overrun project likely exceeds the full programme cost. This is the primary economic argument — not the time saving."],
]
story.append(grid(roi_rows[0], roi_rows[1:], [3.8*cm, 3*cm, 8.7*cm]))

story += [sp(10), h2("4.4  Risks and Mitigations")]
risk_rows = [
    ["Risk",                    "Likelihood", "Impact", "Mitigation"],
    ["EVM data quality insufficient for reliable signals",
     "Medium",   "High",
     "Data quality audit before Phase 2. Retrospective comparison of system EAC vs actual costs for closed projects. Proceed only if MAE < 15%."],
    ["PMs game the system (more optimistic narratives, withheld COs) once they know how flagging works",
     "Medium",   "Medium",
     "Transparent evidence requirements: PMs see what was flagged and why after review. Narrative gaming is detectable; CO withholding is addressed by direct contract management system integration."],
    ["Controllers stop reviewing agent output critically",
     "Medium",   "High",
     "Monitor override rate monthly. Alert if any Controller's rate drops below 5%. Mandate written rationale for ACCEPT on any project with CPI below 0.92."],
    ["Model drift after Anthropic version update",
     "Low",      "Medium",
     "Pin to specific model version string. Run regression suite (20 known cases) before accepting any update. Automated gate blocks deployment if accuracy drops."],
    ["Data residency non-compliance in EU or Middle East",
     "Low",      "High",
     "Legal review before each regional rollout. Anthropic EU endpoint or on-premise deployment for restricted regions."],
]
story.append(grid(risk_rows[0], risk_rows[1:], [3.8*cm, 2*cm, 1.6*cm, 8.1*cm]))

story += [sp(10), h2("4.5  Rollout Approach")]
for phase, timeline, scope, gate in [
    ("Phase 1: Parallel pilot",
     "Months 1–2",
     "1 Finance Controller, 20 projects, agent runs alongside full manual review. No production data — mock data or anonymised historical data only.",
     "Kill/continue at Month 2: FAR < 15%, Controller override rate 10–60%, Controller qualitative assessment positive."),
    ("Phase 2: Controlled expansion",
     "Months 3–4",
     "5 Controllers, 50 projects. Real EVM data integration begins. Audit trail live. Override data begins accumulating.",
     "Kill/continue at Month 4: FAR < 12%, override rate stable, data integration SLA met (EVM data available within 3 days of period close)."),
    ("Phase 3: Full FIN rollout",
     "Months 5–8",
     "All Finance Controllers, full project portfolio. Multi-region deployment begins. PM submission channel live. Controller override feeding calibration.",
     "No kill gate — system is in production. Monitor: FAR, override rate, run completion time, PM escalation contest rate."),
    ("Phase 4: Cross-cluster extension",
     "Months 9–12",
     "Extend agent pattern to adjacent workflows: budget variance analysis, cash flow forecasting, earned schedule analysis. Architecture reuse — only tools and data schema change.",
     "Business case review at Month 9: has Phase 3 FAR remained below 10%? Has Controller adoption remained above 80%?"),
]:
    story.append(b(f"<b>{phase} ({timeline}):</b> {scope} <i>Gate: {gate}</i>"))

story.append(PageBreak())

# ============================================================
# TASK 5 — ASSUMPTIONS & KILL TEST
# ============================================================
story += [h1("Task 5 — Assumptions & Kill Test"), hr(), p(
    "NIG's AI experimentation programme depends on engineers defining kill criteria before "
    "requesting further investment. The following three assumptions are load-bearing. "
    "If any one proves false, the solution either cannot work as designed or should not be trusted "
    "with real financial oversight decisions."
)]

story += [h2("5.1  Assumption 1: EVM Data Is Reliable Enough to Act On")]
story += [
    p("<b>Why it matters:</b> Every agent signal — CPI trend, EAC credibility verdict, implied "
      "future CPI, contingency consumption rate — is derived mathematically from EVM data extracted "
      "from NIG's project controls system. If that data is stale (updated quarterly rather than "
      "monthly), incorrectly coded (WBS actuals mapped to wrong cost accounts), or manually adjusted "
      "without audit trail, the agent applies rigorous mathematical reasoning to unreliable inputs. "
      "The result is not obviously wrong outputs — it is precisely wrong outputs delivered with "
      "numerical confidence. A Controller reviewing 'CPI 0.762 for 12 periods, implied future CPI "
      "NOT CREDIBLE' has no way to know that the CPI is wrong if the source data is wrong."),
    p("<b>How to validate:</b> Before Phase 2 deployment, extract EVM data as it existed at each "
      "monthly period close for the last 24 months. For projects that have since completed, compare "
      "the system-derived EAC at each period against actual final cost. If mean absolute error "
      "exceeds 15% of BAC, EVM data quality is insufficient. A data remediation programme — "
      "retraining project controls teams, fixing cost account mappings, enforcing monthly close "
      "discipline — must precede Phase 2. This validation cannot be skipped."),
    p("<b>Consequence if false:</b> The quantitative tool layer must be replaced or supplemented "
      "with qualitative signals only (PM narrative analysis, CO register completeness). "
      "This is a fundamentally different system with lower precision, higher false accept rate, "
      "and reduced Controller trust. It would also mean NIG's EVM function requires a remediation "
      "programme independent of this AI initiative."),
]

story += [h2("5.2  Assumption 2: Agent FLAG Decisions Predict Actual Cost Overruns")]
story += [
    p("<b>Why it matters:</b> The prototype is evaluated against manually constructed ground truth "
      "labels — expert judgement about which projects should be flagged based on EVM signals. "
      "These labels are not the same as actual overruns. The real measure of value is whether "
      "projects the agent flags actually overrun relative to projects it accepts. If flagged and "
      "accepted projects have similar actual overrun rates, the agent is detecting signals that "
      "do not predict real-world outcomes — even if it correctly matches the expert labels."),
    p("<b>How to validate:</b> Six-month lag study, starting from Month 1 of production deployment. "
      "At Month 7, for every project from Month 1's review: compare actual cost-to-date against "
      "BAC trajectory and PM EAC. FLAG projects should show materially higher actual overrun rates "
      "than ACCEPT projects. Acceptable threshold: FLAG projects should have at least 3× the actual "
      "overrun rate of ACCEPT projects. If the ratio is below 2×, the agent is not adding "
      "predictive value beyond baseline."),
    p("<b>Consequence if false:</b> The agent is correctly reasoning about EVM signals that do not "
      "predict real project outcomes. This points to a systemic problem with NIG's EVM discipline "
      "— projects are not being tracked in a way that makes their cost trajectory predictable from "
      "period data. Fixing this requires a programme-level EVM standards intervention, not an "
      "improvement to the agent. The agent should be suspended until EVM discipline is established."),
]

story += [h2("5.3  Assumption 3: Finance Controllers Will Use the Tool as Designed")]
story += [
    p("<b>Why it matters:</b> The system's value depends entirely on Controllers reviewing agent "
      "output critically — overriding incorrect FLAGs, escalating confirmed FLAGs, and using the "
      "cited evidence in their own escalation communications. Two failure modes destroy this. "
      "Over-reliance: Controllers approve agent output without review, creating a single point of "
      "failure and eliminating the human oversight the design depends on. Under-reliance: Controllers "
      "dismiss every FLAG as 'the system doesn't understand the project context' and run manual "
      "review anyway — the tool adds cost and process without adding value."),
    p("<b>How to validate:</b> Track Controller override rate per month for each Controller. "
      "Healthy range: 10–40% of decisions modified. Below 10% consistently: over-reliance — "
      "the Controller is not reviewing, just approving. Above 60% consistently: trust failure — "
      "the agent is not producing output the Controller finds credible. Conduct structured "
      "interviews with Controllers at months 1, 3, and 6 of Phase 1, explicitly asking: "
      "'When you override an agent decision, what made you disagree? When you accept it, "
      "have you actually read the evidence or just the verdict?'"),
    p("<b>Consequence if false:</b> <i>If over-reliance:</i> mandate written rationale for any "
      "ACCEPT decision on a project with CPI below 0.92 — forces engagement with the evidence "
      "regardless of the agent verdict. <i>If under-reliance:</i> the agent comment format needs "
      "to be redesigned to lead with the single most important finding ('The PM needs a 23% CPI "
      "improvement that this project has never achieved') rather than a full evidence list. "
      "Add a 'what changed since last month' view to anchor the Controller in the delta, "
      "not the absolute state."),
]

story += [sp(10), h2("5.4  Kill Metrics — Hard Thresholds")]
story += [p(
    "These three metrics define conditions under which the solution must be shut down or "
    "fundamentally redesigned. They are not aspirational targets. They have specific measurement "
    "windows and defined actions. Engineering teams that cannot define kill metrics cannot be "
    "trusted to report accurately when their system begins to fail."
)]

kill_rows = [
    ["Kill Metric",                "Threshold",          "Measurement window",                    "Action if triggered"],
    ["False Accept Rate",
     "&gt; 15%",
     "3 consecutive monthly cycles",
     "Immediate suspension pending root cause analysis. Investigate: data quality event, model version change, prompt regression, or systematic controller override pattern. Do not resume until root cause identified and FAR returns below 10% in testing."],
    ["Controller Override Rate",
     "&lt; 5% or &gt; 60% per Controller",
     "2 consecutive months for any individual Controller",
     "Below 5%: mandatory review sessions, written rationale on low-CPI accepts. Above 60%: qualitative interview to identify trust failure, evidence format redesign, possible model calibration issue."],
    ["EVM Data Lag at Cycle Start",
     "&gt; 2 weeks stale at time of run",
     "Any single monthly run",
     "Run blocked automatically. All projects flagged MANUAL_REVIEW_REQUIRED with signal-only summary (no LLM decisions). Data SLA must be contractually enforced with NIG IT — this is a dependency, not a preference."],
]
story.append(grid(kill_rows[0], kill_rows[1:], [3.2*cm, 2.2*cm, 3.3*cm, 6.8*cm]))

story += [sp(12), callout(
    "<b>Engineering discipline note:</b> Defining kill metrics before deployment is not a sign of "
    "low confidence in the solution. It is the mechanism by which NIG's AI programme maintains "
    "credibility with finance leadership that has been burned by demos that could not survive "
    "contact with real operations. False Accept Rate is the right primary kill metric because "
    "it is observable, measurable at every cycle, and directly tied to the financial risk "
    "the system exists to manage. A team that monitors FAR and is willing to suspend their "
    "own system is a team that can be trusted with real financial data.",
    color=NIG_LIGHT, border=NIG_MED
)]

# ============================================================
# BUILD PDF
# ============================================================
OUTPUT = r"C:\Users\Aymane\earnings-agent\NIG_Forecast_Challenge_Desk_TDR.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2.5*cm, rightMargin=2.5*cm,
    topMargin=2.5*cm,  bottomMargin=2.2*cm,
    title="NIG Forecast Challenge Desk — Technical Design Review",
    author="Aymane Lamyaghri",
    subject="AI Engineer Case Assignment — FIN Cluster",
)

def on_page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(LGREY)
        canvas.drawString(2.5*cm, 1.4*cm,
            "NorthStar Infrastructure Group · Forecast Challenge Desk · Technical Design Review")
        canvas.drawRightString(A4[0]-2.5*cm, 1.4*cm, f"Page {doc.page}")
        canvas.setStrokeColor(HexColor("#e2e8f0"))
        canvas.setLineWidth(0.4)
        canvas.line(2.5*cm, 1.7*cm, A4[0]-2.5*cm, 1.7*cm)
    canvas.restoreState()

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF written to: {OUTPUT}")
