"""
Forecast Challenge Desk -- Parallel agentic review.

Architecture:
  1. Orchestrator calls load_all_summaries + get_portfolio_exposure_ranking ONCE.
  2. 20 mini-agents run in parallel via ThreadPoolExecutor (max 10 concurrent).
     Each mini-agent handles exactly ONE project and has no knowledge of others.
  3. Results are aggregated as they arrive (live streaming).

Wall-clock time: ~slowest single project (~20-40s) instead of sum of all (~120s).
"""
from __future__ import annotations
import json, os, threading, time
from typing import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic
from dotenv import load_dotenv

from tools.challenge_tools import (
    tool_load_all_summaries, tool_get_portfolio_exposure_ranking,
    tool_get_project_detail, tool_get_change_order_exposure,
    tool_get_wbs_cost_breakdown, tool_get_spend_acceleration,
    tool_get_cpi_history, tool_get_pm_eac_history,
    tool_get_prior_explanations, tool_write_decision,
)
from data.forecast_submissions import SUBMISSIONS

load_dotenv()
MODEL      = "claude-haiku-4-5-20251001"
MAX_TURNS  = 14   # per project — enough for deep investigation + write_decision
MAX_WORKERS = 10  # parallel LLM calls
_CB_LOCK   = threading.Lock()


def _client():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY not set in .env")
    return anthropic.Anthropic(api_key=key)


# ── Per-project tool set (no portfolio-level tools) ───────────────────────────

PROJECT_TOOLS = [
    {
        "name": "get_project_detail",
        "description": (
            "Full EVM investigation for this project: CPI/SPI, WBS breakdown, "
            "EAC credibility, implied future CPI, PM narrative, risk note, "
            "and a change order alert if material COs are missing from the PM EAC. "
            "Call this first."
        ),
        "input_schema": {
            "type": "object", "required": ["project_id"],
            "properties": {"project_id": {"type": "string"}},
        },
    },
    {
        "name": "get_change_order_exposure",
        "description": (
            "Full change order register — reveals pending/disputed costs the PM "
            "has NOT included in their EAC. "
            "Call when get_project_detail shows a CO alert, or when the PM narrative "
            "mentions acceleration, rework, contamination, FX exposure, or regulatory steps."
        ),
        "input_schema": {
            "type": "object", "required": ["project_id"],
            "properties": {"project_id": {"type": "string"}},
        },
    },
    {
        "name": "get_wbs_cost_breakdown",
        "description": (
            "Dollar overrun per WBS package at completion. "
            "Call when HIDDEN_WBS signal is present — quantifies exactly which "
            "package is the problem and how much it will cost."
        ),
        "input_schema": {
            "type": "object", "required": ["project_id"],
            "properties": {"project_id": {"type": "string"}},
        },
    },
    {
        "name": "get_spend_acceleration",
        "description": (
            "Monthly actual-cost trend for last 6 periods. "
            "Call when SPI_TRAP is present — acceleration costs flow through as "
            "future AC spikes, predicting a CPI drop even if current CPI is clean."
        ),
        "input_schema": {
            "type": "object", "required": ["project_id"],
            "properties": {"project_id": {"type": "string"}},
        },
    },
    {
        "name": "get_cpi_history",
        "description": (
            "Month-by-month CPI trajectory. "
            "Call when STRUCTURAL_DECLINE or STEP_CHANGE signals are present "
            "to confirm whether the decline is sustained or event-driven."
        ),
        "input_schema": {
            "type": "object", "required": ["project_id"],
            "properties": {"project_id": {"type": "string"}},
        },
    },
    {
        "name": "get_pm_eac_history",
        "description": (
            "PM's submitted EAC vs system EAC over the last 6 months. "
            "Call when PM credibility is UNLIKELY or NOT_CREDIBLE — "
            "detects persistent optimism bias across multiple reporting periods."
        ),
        "input_schema": {
            "type": "object", "required": ["project_id"],
            "properties": {"project_id": {"type": "string"}},
        },
    },
    {
        "name": "get_prior_explanations",
        "description": (
            "3 months of PM narrative text. "
            "Call ONLY when REPEATED_NARRATIVE signal is flagged."
        ),
        "input_schema": {
            "type": "object", "required": ["project_id"],
            "properties": {"project_id": {"type": "string"}},
        },
    },
    {
        "name": "write_decision",
        "description": (
            "Write your final decision for this project. "
            "Call exactly once when you have enough evidence."
        ),
        "input_schema": {
            "type": "object",
            "required": ["project_id", "decision", "comment"],
            "properties": {
                "project_id": {"type": "string"},
                "decision":   {"type": "string", "enum": ["ACCEPT", "FLAG", "NEEDS_EVIDENCE"]},
                "comment": {
                    "type": "string",
                    "description": (
                        "1-2 sentences. Always cite the specific number. "
                        "FLAG: 'CPI 0.762 for 11 periods; PM needs 0.936 — not credible. $6M CO not in EAC.' "
                        "ACCEPT: 'CPI 0.998 stable, gap +1.2%, narrative accurate.' "
                        "NEEDS_EVIDENCE: 'Only 2 periods, 14% complete.'"
                    ),
                },
            },
        },
    },
]

MINI_SYSTEM = """\
You are a finance controller reviewing ONE infrastructure project for NorthStar Infrastructure Group.
You will be given the project ID, portfolio context, and tools to investigate.

LABELS:
  FLAG           -- any concern: CPI decline, EAC gap, narrative contradicts data,
                    contingency exhausted, SPI trap, hidden WBS disaster,
                    repeated excuses, undisclosed change orders
  ACCEPT         -- EAC gap <3%, CPI >0.97 stable, honest narrative, adequate contingency
  NEEDS_EVIDENCE -- EARLY_PHASE (<4 periods or <20% complete)

CONTRACT TYPE MATTERS:
  REIMBURSABLE -- client pays all actual costs; PM optimism directly hits the client budget
  LUMP_SUM     -- contractor absorbs overrun; but contractor distress risk if CPI <0.80
  TARGET_COST  -- pain/gain share; hidden COs still matter

INVESTIGATION DEPTH:
  QUICK: no !! signals, CPI >0.97, gap <3% -> write_decision immediately (no tools needed)
  QUICK NEEDS_EVIDENCE: EARLY_PHASE signal -> write_decision immediately
  STANDARD: any !! signal -> get_project_detail -> write_decision
  DEEP: severe or compound signals:
    CO alert shown      -> get_change_order_exposure
    HIDDEN_WBS          -> get_wbs_cost_breakdown
    SPI_TRAP            -> get_spend_acceleration
    STRUCTURAL_DECLINE  -> get_cpi_history
    PM credibility low  -> get_pm_eac_history
    REPEATED_NARRATIVE  -> get_prior_explanations

FIVE TRAPS TO ALWAYS FLAG:
  SPI_TRAP        -- CPI clean but SPI <0.88: call get_spend_acceleration
  IMPOSSIBLE_CPI  -- PM needs >20% CPI recovery: cite the implied future CPI
  CONT_AHEAD      -- contingency % consumed >> project % complete
  HIDDEN_WBS      -- Civil CPI <0.78 masked at project level: call get_wbs_cost_breakdown
  REPEATED_NARRATIVE -- same phrase across months, CPI still worsening

COMMENT RULE: cite specific numbers. Never vague.
  Good: "CPI 0.762 for 11 periods; PM's $95M requires future CPI 0.936 — not credible. $6M CO not in EAC."
  Bad:  "Performance declining and EAC may be too low."
"""


def _execute_one(name: str, inp: dict, assigned_pid: str, cycle: int) -> str:
    """Execute a tool call for one project. Enforces pid isolation on write_decision."""
    try:
        pid_in = inp.get("project_id", "").upper()
        if name == "get_project_detail":
            return tool_get_project_detail(pid_in, cycle=cycle)
        if name == "get_change_order_exposure":
            return tool_get_change_order_exposure(pid_in, cycle=cycle)
        if name == "get_wbs_cost_breakdown":
            return tool_get_wbs_cost_breakdown(pid_in, cycle=cycle)
        if name == "get_spend_acceleration":
            return tool_get_spend_acceleration(pid_in, cycle=cycle)
        if name == "get_cpi_history":
            return tool_get_cpi_history(pid_in, cycle=cycle)
        if name == "get_pm_eac_history":
            return tool_get_pm_eac_history(pid_in, cycle=cycle)
        if name == "get_prior_explanations":
            return tool_get_prior_explanations(pid_in, cycle=cycle)
        if name == "write_decision":
            if pid_in != assigned_pid.upper():
                return json.dumps({"error": f"You are assigned to {assigned_pid} only."})
            return tool_write_decision(pid_in, inp["decision"], inp["comment"])
        return json.dumps({"error": f"Unknown tool: {name}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _analyse_one(
    pid:            str,
    portfolio_scan: str,
    ranking_text:   str,
    cycle:          int,
) -> tuple[dict | None, list[dict]]:
    """
    Single-project mini-agent. Runs in its own thread.
    Returns (decision_dict, trace_list).
    """
    client  = _client()
    trace:  list[dict] = []
    decision: dict | None = None

    sub  = SUBMISSIONS.get(pid, {})
    name = sub.get("project_name", pid)

    messages = [{
        "role": "user",
        "content": (
            f"Review project {pid} — {name}.\n\n"
            f"=== PORTFOLIO OVERVIEW (for calibration) ===\n{portfolio_scan}\n\n"
            f"=== DOLLAR EXPOSURE RANKING ===\n{ranking_text}\n\n"
            f"Now investigate {pid} and call write_decision('{pid}', ...) when ready."
        ),
    }]

    for _ in range(MAX_TURNS):
        resp = client.messages.create(
            model=MODEL, max_tokens=2048,
            system=MINI_SYSTEM, tools=PROJECT_TOOLS, messages=messages,
        )

        if resp.stop_reason in ("end_turn", "stop_sequence", None):
            break
        if resp.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []

        for block in resp.content:
            if block.type != "tool_use":
                continue

            raw    = _execute_one(block.name, block.input, pid, cycle)
            parsed = _try_json(raw)
            entry  = {"tool": block.name, "input": block.input, "pid": pid}
            # Store result for investigation tools (not write_decision — just ok/status)
            if block.name != "write_decision":
                entry["result"] = raw
            trace.append(entry)

            if block.name == "write_decision" and isinstance(parsed, dict) and parsed.get("status") == "ok":
                decision = {
                    "project_id": pid,
                    "decision":   block.input.get("decision", "").upper(),
                    "comment":    block.input.get("comment", ""),
                }

            tool_results.append({
                "type":        "tool_result",
                "tool_use_id": block.id,
                "content":     raw,
            })

        messages.append({"role": "user", "content": tool_results})

        if decision:
            break

    return decision, trace


def run_challenge_analysis(
    cycle:       int | None = None,
    on_decision: Callable | None = None,   # called from MAIN THREAD — safe for Streamlit
) -> tuple[dict | None, list[dict]]:

    from data.forecast_submissions import CURRENT_CYCLE
    cycle = cycle or CURRENT_CYCLE

    # ── Step 1: Shared portfolio context (called once) ────────────────────────
    portfolio_scan = tool_load_all_summaries(cycle=cycle)
    ranking_text   = tool_get_portfolio_exposure_ranking(cycle=cycle)

    all_trace: list[dict] = [
        {"tool": "load_all_summaries",            "input": {}},
        {"tool": "get_portfolio_exposure_ranking", "input": {}},
    ]

    # ── Step 2: 20 independent agents in parallel ────────────────────────────
    # Worker threads do NO UI work. on_decision is called here, in the main thread,
    # as each future completes — safe to call Streamlit methods from on_decision.
    projects = list(SUBMISSIONS.keys())
    decided:  dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(_analyse_one, pid, portfolio_scan, ranking_text, cycle): pid
            for pid in projects
        }
        for future in as_completed(futures):
            decision, trace = future.result()
            all_trace.extend(trace)
            if decision:
                decided[decision["project_id"]] = decision
                if on_decision:
                    on_decision(decision)   # main thread — Streamlit safe

    if not decided:
        return None, all_trace

    decisions = list(decided.values())
    summary   = {"ACCEPT": 0, "FLAG": 0, "NEEDS_EVIDENCE": 0}
    for d in decisions:
        k = d["decision"]
        if k in summary:
            summary[k] += 1

    return {"status": "ok", "decisions": decisions, "summary": summary}, all_trace


def _try_json(s: str):
    try:    return json.loads(s)
    except: return s
