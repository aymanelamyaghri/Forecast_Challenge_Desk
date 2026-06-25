"""
Monthly forecast submissions from project managers.
Period 14 (Nov 2024) has rich hand-crafted narratives.
Prior periods are generated deterministically from portfolio EVM data.
"""
from __future__ import annotations

CURRENT_CYCLE  = 14
CURRENT_LABEL  = "November 2024"
REVIEW_CYCLES  = [9, 10, 11, 12, 13, 14]

PERIOD_LABELS = {
    9:  "Jun 2024",
    10: "Jul 2024",
    11: "Aug 2024",
    12: "Sep 2024",
    13: "Oct 2024",
    14: "Nov 2024",
}

# ── Rich hand-crafted submissions for Nov 2024 (period 14) ────────────────────
SUBMISSIONS: dict[str, dict] = {

    "P01": {
        "project_name": "North Sea Platform Upgrade",
        "pm_eac": 50_200_000,
        "explanation": (
            "Civil and structural works continue to be impacted by North Sea weather "
            "windows. Productivity over the last quarter ran at approximately 84% of plan. "
            "The team has revised the work sequencing for Q1 to take advantage of forecast "
            "improved conditions. We anticipate recovery of approximately 60% of the current "
            "variance through accelerated offshore campaigns and a revised logistics strategy. "
            "The forecast of $50.2M reflects a conservative estimate of this recovery. "
            "The project remains committed to delivery within the approved $45.2M budget envelope with contingency."
        ),
        "risk_note": "Weather window risk remains open. Rework scope on jacket interface not fully quantified.",
        "prior_explanations": [
            "Civil works productivity impacted by weather. Recovery expected as conditions improve Q1. "
            "Forecast revised to $49.8M. Committed to delivery within approved budget.",
            "Temporary weather-related productivity loss on platform jacket. Expected to recover next quarter. "
            "No change to approved budget target.",
        ],
        "ground_truth": {"decision": "ESCALATE", "why": "CPI declined 13 consecutive periods to 0.820. PM EAC $50.2M vs system $57.8M. 'Recovery expected' phrase used for 3 consecutive months."},
    },

    "P02": {
        "project_name": "Dubai Metro Extension",
        "pm_eac": 125_000_000,
        "explanation": (
            "Following the October rebaseline from $105M to $120M, the project is performing "
            "well against the revised programme. Post-rebaseline CPI is 0.93, reflecting the "
            "additional three-station scope now fully incorporated. Contingency consumption is "
            "tracking in line with project milestones. EAC of $125M includes prudent provisions "
            "for final package close-outs."
        ),
        "risk_note": "FX exposure on UAE subcontractor packages remains open. Civil interfaces require design sign-off.",
        "prior_explanations": [
            "Rebaseline approved this month absorbing prior overrun into revised $120M budget. Project reset to deliver within new baseline.",
            "Cost performance continues below plan (CPI 0.81). Rebaseline submission being prepared for Oct PRB.",
        ],
        "ground_truth": {"decision": "ESCALATE", "why": "Post-rebaseline CPI already declining again. Same pattern as pre-rebaseline deterioration."},
    },

    "P03": {
        "project_name": "Sydney Water Treatment Plant",
        "pm_eac": 28_700_000,
        "explanation": (
            "Project continues to track closely to plan. CPI 0.995 and SPI 0.997 reflect stable "
            "performance across all work packages. A minor survey delay in Month 10 was resolved "
            "within the period at no additional cost. All major packages are on track. "
            "EAC of $28.7M reflects a minor contingency draw for the survey delay resolution."
        ),
        "risk_note": "No open risk items above $50K threshold.",
        "prior_explanations": [
            "Project tracking to plan. CPI 0.997. No issues.",
            "Stable performance. No variance to report.",
        ],
        "ground_truth": {"decision": "ACCEPT", "why": "Narrative accurate. System EAC within 0.7% of PM EAC."},
    },

    "P04": {
        "project_name": "Houston Refinery Turnaround",
        "pm_eac": 19_800_000,
        "explanation": (
            "Project is 85% complete. The CPI of 0.91 reflects additional inspection and rework "
            "identified during the electrical package close-out. We expect to recover approximately "
            "40% of the current cost variance through commercial close-out provisions and back-charges "
            "to the specialist subcontractor for defective work. The submitted EAC of $19.8M is net "
            "of these expected recoveries."
        ),
        "risk_note": "Back-charge claim against electrical subcontractor: $350K — disputed, outcome uncertain.",
        "prior_explanations": [
            "Electrical rework identified. CPI 0.908. Commercial close-out provisions expected to recover variance.",
            "Rework scope being quantified. No change to EAC pending assessment.",
        ],
        "ground_truth": {"decision": "CHALLENGE", "why": "EAC assumes 40% recovery from disputed back-charge. Not confirmed."},
    },

    "P05": {
        "project_name": "Kuala Lumpur Tower Fitout",
        "pm_eac": 8_700_000,
        "explanation": (
            "Project mobilised in October 2024. Month 2 CPI of 0.88 reflects vendor mobilisation "
            "fees and initial setup costs which are non-recurring. We expect CPI to normalise above "
            "1.0 by Month 4 once the main fitout works are underway. Forecast of $8.7M is indicative "
            "pending a detailed bottom-up review in Month 4."
        ),
        "risk_note": "Procurement of specialist AV systems — lead time risk.",
        "prior_explanations": [
            "Project mobilising. Month 1 CPI 0.92 reflects setup costs. Early-stage figure only.",
        ],
        "ground_truth": {"decision": "NEEDS_EVIDENCE", "why": "Only 2 periods at 18% complete. PM explanation plausible."},
    },

    "P06": {
        "project_name": "Cairo Power Station",
        "pm_eac": 98_000_000,
        "explanation": (
            "Overall project CPI of 0.93 reflects scope adjustments to the civil programme following "
            "unexpected subsoil conditions encountered during foundation works. The civil package has "
            "been re-scoped and is expected to reach revised productivity targets from Month 16 onward. "
            "The mechanical and electrical package continues to outperform plan and is expected to "
            "partially offset the civil variance. EAC of $98M includes a provision for residual civil risk."
        ),
        "risk_note": "Civil foundation rework scope: additional piling and reinforcement. M&E vendor performance ahead of plan.",
        "prior_explanations": [
            "Civil scope adjustments ongoing. Project CPI 0.93. M&E offsetting. EAC under review.",
            "Subsoil conditions worse than anticipated. Civil package replanning. Project-level CPI 0.94.",
        ],
        "ground_truth": {"decision": "ESCALATE", "why": "Civil WBS CPI 0.61 masked by project CPI 0.93. M&E CPI 1.08 hiding a $15M+ civil overrun."},
    },

    "P07": {
        "project_name": "Manchester Roads Programme",
        "pm_eac": 22_000_000,
        "explanation": (
            "Cost performance remains on track with CPI of 1.01. A schedule slippage of approximately "
            "18% has been identified, primarily in the carriageway resurfacing packages. An acceleration "
            "programme commenced this month with the main contractor to recover the programme by Month 15. "
            "The acceleration involves extended working hours and weekend shifts. EAC is unchanged at $22M "
            "as the acceleration is expected to be completed within the existing contingency envelope."
        ),
        "risk_note": "Acceleration programme underway — premium rate invoices not yet received. Contingency 75% consumed.",
        "prior_explanations": [
            "Schedule delay emerging. Acceleration plan being developed. CPI 1.01 — cost on track. EAC unchanged.",
            "Minor schedule slippage on resurfacing packages. Cost performance solid. Monitoring closely.",
        ],
        "ground_truth": {"decision": "ESCALATE", "why": "SPI 0.82 — acceleration costs not yet in actuals. Contingency 75% at 52% complete."},
    },

    "P08": {
        "project_name": "Singapore LNG Terminal",
        "pm_eac": 68_500_000,
        "explanation": (
            "The two additional safety systems required under the MAS regulatory update have been fully "
            "scoped and incorporated into the baseline. CPI of 0.97 reflects these additional costs and "
            "is considered acceptable given the regulatory nature. The risk register has been updated "
            "and remaining risk items are assessed as manageable within the current contingency position. "
            "EAC of $68.5M reflects the complete regulatory scope."
        ),
        "risk_note": "Two further regulatory review points outstanding (minor).",
        "prior_explanations": [
            "Regulatory scope addition integrated. CPI 0.962. Risk items manageable.",
            "Additional regulatory systems scoped. Cost impact being absorbed. Contingency draw tracked.",
        ],
        "ground_truth": {"decision": "CHALLENGE", "why": "Contingency 91% consumed at 58% complete. PM says 'manageable' — contradicts data."},
    },

    "P09": {
        "project_name": "Berlin Office Development",
        "pm_eac": 14_300_000,
        "explanation": (
            "Project is performing to plan with stable cost performance at CPI 0.984. A minor schedule "
            "delay of 5-6% has been reported due to structural steel supplier lead times, but this has "
            "no anticipated cost impact as the delay falls on the non-critical path. All major packages "
            "are on track for practical completion in Month 16."
        ),
        "risk_note": "Steel delivery delay — non-critical path. No cost impact expected.",
        "prior_explanations": [
            "Stable performance. Minor schedule note on steel lead times. No cost impact.",
            "Project on track. CPI 0.987.",
        ],
        "ground_truth": {"decision": "ACCEPT", "why": "Narrative accurate. System EAC within 1% of PM EAC."},
    },

    "P10": {
        "project_name": "Mumbai Port Expansion",
        "pm_eac": 61_000_000,
        "explanation": (
            "Civil and procurement challenges continue to affect project performance. The team has "
            "implemented targeted recovery measures including additional site resource mobilisation and "
            "revised procurement packaging for remaining marine works. These measures are expected to "
            "improve cost performance from Month 17 onward. The current forecast of $61M reflects a "
            "challenging but achievable recovery scenario. Management is actively monitoring weekly."
        ),
        "risk_note": "Supply chain disruption on marine equipment. Labour productivity below plan for 8 consecutive months.",
        "prior_explanations": [
            "Civil and procurement challenges ongoing. Recovery measures in place. CPI 0.789. Forecast $60M.",
            "Compounding supply chain and labour issues. Recovery programme underway. Weekly monitoring in place.",
        ],
        "ground_truth": {"decision": "ESCALATE", "why": "CPI 0.793, SPI 0.862, contingency 88%. System EAC ~$69M vs PM $61M. Recovery requires future CPI 1.15."},
    },

    "P11": {
        "project_name": "Oslo Wind Farm",
        "pm_eac": 39_000_000,
        "explanation": (
            "Project remains in early mobilisation phase at Month 5. CPI volatility seen in Months 1-5 "
            "is consistent with early-phase setup activities and seasonal offshore wind mobilisation. "
            "A detailed bottom-up review will be completed by Month 8 when the main turbine installation "
            "phase is underway. EAC of $39M is indicative."
        ),
        "risk_note": "Turbine delivery schedule from OEM — lead time monitoring active.",
        "prior_explanations": [
            "Early mobilisation. CPI volatile — normal at this stage. Forecast indicative.",
            "Setup phase. No material variance calls yet.",
        ],
        "ground_truth": {"decision": "NEEDS_EVIDENCE", "why": "Only 5 periods at 20% complete. CPI volatile but not structural."},
    },

    "P12": {
        "project_name": "Toronto Highway Widening",
        "pm_eac": 32_500_000,
        "explanation": (
            "Cost performance has shown consistent improvement over the last 8 months following "
            "tighter productivity targets and package re-sequencing in Month 6. CPI has recovered "
            "from a low of 0.882 in Month 5 to the current 0.960. The finance team has verified "
            "the improvement is driven by genuine productivity gains. EAC of $32.5M reflects the "
            "current trend plus provisions for winter working conditions."
        ),
        "risk_note": "Winter working conditions — minor cost provision included in EAC.",
        "prior_explanations": [
            "Continued performance improvement. CPI 0.950. Recovery on track.",
            "Recovery trajectory maintained. CPI recovering from 0.882 to 0.940.",
        ],
        "ground_truth": {"decision": "ACCEPT", "why": "CPI genuinely recovering 0.882 to 0.960. System EAC within 1%."},
    },

    "P13": {
        "project_name": "Riyadh Hospital Complex",
        "pm_eac": 76_500_000,
        "explanation": (
            "The mechanical and electrical package continues to run below plan due to complex system "
            "integration requirements for the hospital specialist medical equipment interfaces. CPI of "
            "0.94 is below target but within acceptable tolerance. The team does not anticipate further "
            "deterioration. Contingency remains available to manage residual risk items. EAC of $76.5M "
            "is unchanged and the project remains on track for completion within the approved $72M budget plus contingency."
        ),
        "risk_note": "M&E integration complexity — further specialist design required.",
        "prior_explanations": [
            "M&E integration issues persisting. CPI 0.940. Contingency available. EAC unchanged.",
            "Specialist medical equipment interfaces more complex than planned. Contingency sufficient.",
        ],
        "ground_truth": {"decision": "ESCALATE", "why": "PM says 'contingency remains available' — 97% consumed at 60% complete."},
    },

    "P14": {
        "project_name": "Perth Mining Facility",
        "pm_eac": 42_500_000,
        "explanation": (
            "Project continues to outperform plan across all packages. CPI of 1.028 and SPI of 1.045 "
            "reflect effective procurement strategy and strong site productivity. The piling package "
            "was completed $1.2M under budget due to favourable ground conditions. Revised EAC of "
            "$42.5M represents a $1.5M saving against the original BAC."
        ),
        "risk_note": "No open risk items above threshold. Commissioning plan finalised.",
        "prior_explanations": [
            "Outperforming plan. CPI 1.027. Piling savings confirmed.",
            "Strong performance continuing. Cost savings on ground improvement package.",
        ],
        "ground_truth": {"decision": "ACCEPT", "why": "Narrative accurate. System EAC within 1%. Healthy project."},
    },

    "P15": {
        "project_name": "Cape Town Desalination Plant",
        "pm_eac": 19_500_000,
        "explanation": (
            "Following the September rebaseline from $16M to $19M, the project is progressing well "
            "against the revised programme. Post-rebaseline CPI of 0.971 reflects the newly incorporated "
            "membrane filtration scope. EAC of $19.5M includes a minor provision for membrane procurement "
            "lead time risk."
        ),
        "risk_note": "Membrane procurement lead time — 14-week delivery window.",
        "prior_explanations": [
            "Rebaseline completed September. Post-rebaseline performance stable.",
            "Pre-rebaseline: CPI 0.813 — rebaseline proposal being prepared.",
        ],
        "ground_truth": {"decision": "CHALLENGE", "why": "Pre-rebaseline CPI was 0.78. PM narrative presents only post-rebaseline metrics."},
    },

    "P16": {
        "project_name": "Amsterdam Data Centre Fit-Out",
        "pm_eac": 11_400_000,
        "explanation": (
            "Project is on track with a minor cost variance within contingency tolerance. CPI of 0.968 "
            "reflects a small quantity overrun on raised flooring due to a design change in Month 3. "
            "This has been fully absorbed. Schedule on track for Month 12 handover."
        ),
        "risk_note": "Commissioning risk: IT equipment delivery from US — minor.",
        "prior_explanations": [
            "Stable performance. Minor raised flooring overrun absorbed. CPI 0.970.",
            "Design change on cable management absorbed. No material impact.",
        ],
        "ground_truth": {"decision": "ACCEPT", "why": "System EAC matches PM EAC. Narrative accurate."},
    },

    "P17": {
        "project_name": "Lagos Pipeline",
        "pm_eac": 95_000_000,
        "explanation": (
            "Terrain productivity challenges continue to affect civil and procurement performance. "
            "The swamp crossing sections have proven more difficult than anticipated in the original "
            "geotechnical survey. A revised work sequencing plan has been developed that moves crews "
            "to more favourable terrain segments in Q1. FX exposure on imported pipe fittings has been "
            "partially hedged. We expect productivity improvement from Month 21 as crews transition to "
            "the easier northern segments. EAC of $95M reflects the revised sequencing plan."
        ),
        "risk_note": "FX hedge covers 60% of remaining procurement — 40% unhedged. Swamp section rework scope not fully quantified.",
        "prior_explanations": [
            "Terrain challenges continuing. CPI 0.758. Revised sequencing plan in development. EAC under review.",
            "Swamp crossing productivity significantly below plan. FX impact on procurement. Recovery measures being prepared.",
        ],
        "ground_truth": {"decision": "ESCALATE", "why": "System EAC $123M. PM $95M — $28M gap. Implied future CPI 0.93 from 0.762. Not credible."},
    },

    "P18": {
        "project_name": "Vancouver Transit Hub",
        "pm_eac": 54_000_000,
        "explanation": (
            "The contaminated soil discovery in Month 8 triggered an immediate remediation mobilisation. "
            "The remediation contractor has been on site since Month 9 and the scope is substantially "
            "complete. A formal change order for $4M has been submitted to the client and is pending "
            "approval. Post-remediation civil works will resume in Month 11. Our current EAC of $54M "
            "assumes change order approval at $4M and no further contamination in the remaining excavation areas."
        ),
        "risk_note": "Change order approval pending client sign-off. Residual contamination risk in Zone 3 — not yet excavated.",
        "prior_explanations": [
            "Contamination remediation ongoing. Change order submitted. CPI impacted. Expecting normalisation post-remediation.",
            "Step-change event: contaminated soil discovered Month 8. Remediation mobilised. Change order being prepared.",
        ],
        "ground_truth": {"decision": "ESCALATE", "why": "EAC assumes $4M change order approval — not confirmed. Zone 3 contamination unquantified."},
    },

    "P19": {
        "project_name": "Doha Airport Terminal Expansion",
        "pm_eac": 133_500_000,
        "explanation": (
            "Flagship project continues to track to plan. CPI 1.009 reflects effective procurement "
            "and strong contractor performance. SPI 0.980 is within acceptable tolerance. Procurement "
            "savings of $1.8M have been confirmed on the glazing package. EAC of $133.5M represents "
            "a $1.5M saving against the original BAC."
        ),
        "risk_note": "Passenger interface design sign-off — minor, within schedule.",
        "prior_explanations": [
            "Strong performance continuing. Procurement savings confirmed. CPI 1.010.",
            "On track. Glazing package progressing ahead of schedule.",
        ],
        "ground_truth": {"decision": "ACCEPT", "why": "System EAC within 0.2% of PM EAC. Narrative accurate."},
    },

    "P20": {
        "project_name": "Bucharest Water Network Upgrade",
        "pm_eac": 16_800_000,
        "explanation": (
            "Project is 90% complete with a locked-in minor cost variance. CPI of 0.950 reflects "
            "higher-than-planned backfill material costs in the pipe reinstatement package. These "
            "costs are now complete and behind us. No further cost increases are anticipated. "
            "EAC of $16.8M is considered the final out-turn figure."
        ),
        "risk_note": "Defects liability period commences at practical completion — minor.",
        "prior_explanations": [
            "90% complete. Backfill variance finalised. EAC $16.8M — no change expected.",
            "Near completion. Minor backfill overrun locked in. On track for Month 14.",
        ],
        "ground_truth": {"decision": "ACCEPT", "why": "90% complete, small variance locked in, narrative honest."},
    },
}

GROUND_TRUTH = {pid: s["ground_truth"]["decision"] for pid, s in SUBMISSIONS.items()}

CYCLE_GROUND_TRUTH: dict[int, dict[str, str]] = {
    9:  {"P01":"CHALLENGE","P02":"CHALLENGE","P03":"ACCEPT","P04":"CHALLENGE",
         "P05":"NEEDS_EVIDENCE","P06":"CHALLENGE","P07":"CHALLENGE","P08":"ACCEPT",
         "P09":"ACCEPT","P10":"ESCALATE","P11":"NEEDS_EVIDENCE","P12":"CHALLENGE",
         "P13":"CHALLENGE","P14":"ACCEPT","P15":"ACCEPT","P16":"ACCEPT",
         "P17":"ESCALATE","P18":"CHALLENGE","P19":"ACCEPT","P20":"ACCEPT"},
    10: {"P01":"CHALLENGE","P02":"CHALLENGE","P03":"ACCEPT","P04":"CHALLENGE",
         "P05":"NEEDS_EVIDENCE","P06":"CHALLENGE","P07":"CHALLENGE","P08":"CHALLENGE",
         "P09":"ACCEPT","P10":"ESCALATE","P11":"NEEDS_EVIDENCE","P12":"CHALLENGE",
         "P13":"CHALLENGE","P14":"ACCEPT","P15":"ACCEPT","P16":"ACCEPT",
         "P17":"ESCALATE","P18":"CHALLENGE","P19":"ACCEPT","P20":"ACCEPT"},
    11: {"P01":"ESCALATE","P02":"ESCALATE","P03":"ACCEPT","P04":"CHALLENGE",
         "P05":"NEEDS_EVIDENCE","P06":"ESCALATE","P07":"ESCALATE","P08":"CHALLENGE",
         "P09":"ACCEPT","P10":"ESCALATE","P11":"NEEDS_EVIDENCE","P12":"CHALLENGE",
         "P13":"CHALLENGE","P14":"ACCEPT","P15":"CHALLENGE","P16":"ACCEPT",
         "P17":"ESCALATE","P18":"ESCALATE","P19":"ACCEPT","P20":"ACCEPT"},
    12: {"P01":"ESCALATE","P02":"ESCALATE","P03":"ACCEPT","P04":"CHALLENGE",
         "P05":"NEEDS_EVIDENCE","P06":"ESCALATE","P07":"ESCALATE","P08":"CHALLENGE",
         "P09":"ACCEPT","P10":"ESCALATE","P11":"NEEDS_EVIDENCE","P12":"ACCEPT",
         "P13":"ESCALATE","P14":"ACCEPT","P15":"CHALLENGE","P16":"ACCEPT",
         "P17":"ESCALATE","P18":"ESCALATE","P19":"ACCEPT","P20":"ACCEPT"},
    13: {"P01":"ESCALATE","P02":"ESCALATE","P03":"ACCEPT","P04":"CHALLENGE",
         "P05":"NEEDS_EVIDENCE","P06":"ESCALATE","P07":"ESCALATE","P08":"CHALLENGE",
         "P09":"ACCEPT","P10":"ESCALATE","P11":"NEEDS_EVIDENCE","P12":"ACCEPT",
         "P13":"ESCALATE","P14":"ACCEPT","P15":"CHALLENGE","P16":"ACCEPT",
         "P17":"ESCALATE","P18":"ESCALATE","P19":"ACCEPT","P20":"ACCEPT"},
    14: GROUND_TRUTH,
}


# ── Generated submissions for prior periods ───────────────────────────────────

def _pm_optimism_factor(cpi: float) -> float:
    """Deterministic optimism factor: bad projects -> PM submits lower than system EAC."""
    if cpi >= 0.97: return 0.99
    if cpi >= 0.93: return 0.96
    if cpi >= 0.88: return 0.92
    if cpi >= 0.83: return 0.88
    if cpi >= 0.78: return 0.84
    return 0.80


def _brief_narrative(cpi: float, spi: float, pct: float, pm_eac: float, sys_eac: float) -> str:
    if pct < 20:
        return f"Project in early mobilisation at {pct:.0f}% complete. Forecast of ${pm_eac/1e6:.1f}M is indicative pending detailed review."
    gap = (pm_eac - sys_eac) / sys_eac * 100
    if cpi >= 0.97 and spi >= 0.95:
        return f"Project tracking to plan. CPI {cpi:.3f}, SPI {spi:.3f}. No material variances. EAC ${pm_eac/1e6:.1f}M."
    elif cpi >= 0.93:
        return (f"Minor cost variance. CPI {cpi:.3f}. Recovery measures in place. "
                f"EAC ${pm_eac/1e6:.1f}M within approved budget envelope.")
    elif cpi >= 0.87:
        return (f"Performance below plan. CPI {cpi:.3f}, SPI {spi:.3f}. Recovery programme underway. "
                f"Management monitoring closely. EAC ${pm_eac/1e6:.1f}M challenging but achievable.")
    else:
        return (f"Ongoing performance challenges. CPI {cpi:.3f}. Recovery measures in place. "
                f"EAC ${pm_eac/1e6:.1f}M reflects best estimate pending programme improvement.")


def get_submissions_for_period(period: int) -> dict[str, dict]:
    """
    Return submissions dict for the given period.
    Period 14 (Nov 2024): rich hand-crafted narratives.
    Prior periods: generated deterministically from EVM data.
    """
    if period == CURRENT_CYCLE:
        return SUBMISSIONS

    from data.mock_portfolio import build_portfolio
    from tools.evm_engine import (eac_cpi, eac_remaining_at_budget, eac_composite,
                                   analyse_cpi_trend, detect_step_change, recommend_eac_method)

    portfolio = build_portfolio(as_of_period=period)
    gt        = CYCLE_GROUND_TRUTH.get(period, {})
    result    = {}

    for pid, sub_tpl in SUBMISSIONS.items():
        proj = portfolio.get(pid)
        if not proj:
            continue
        cpi = proj["cpi"]; spi = proj["spi"]; pct = proj["pct_complete"]
        bac = proj["bac"]; ev  = proj["ev"];  ac  = proj["ac"]
        cpi_hist = [p["cpi"] for p in proj["periods"]]
        trend = analyse_cpi_trend(cpi_hist)
        step  = detect_step_change(cpi_hist)
        method, _ = recommend_eac_method(pct, trend, step is not None)
        sys_eac = {"cpi":       eac_cpi(bac, ev, ac),
                   "at_budget": eac_remaining_at_budget(bac, ev, ac),
                   "composite": eac_composite(bac, ev, ac, spi)}[method]
        pm_eac = sys_eac * _pm_optimism_factor(cpi)

        # One prior narrative from period-1
        prior_exp = []
        prior_p = build_portfolio(as_of_period=period - 1)
        prior_proj = prior_p.get(pid)
        if prior_proj:
            p_cpi = prior_proj["cpi"]; p_spi = prior_proj["spi"]; p_pct = prior_proj["pct_complete"]
            p_hist = [p["cpi"] for p in prior_proj["periods"]]
            p_trend = analyse_cpi_trend(p_hist)
            p_step  = detect_step_change(p_hist)
            p_meth, _ = recommend_eac_method(p_pct, p_trend, p_step is not None)
            p_bac = prior_proj["bac"]; p_ev = prior_proj["ev"]; p_ac = prior_proj["ac"]
            p_sys = {"cpi":       eac_cpi(p_bac, p_ev, p_ac),
                     "at_budget": eac_remaining_at_budget(p_bac, p_ev, p_ac),
                     "composite": eac_composite(p_bac, p_ev, p_ac, p_spi)}[p_meth]
            p_pm  = p_sys * _pm_optimism_factor(p_cpi)
            prior_exp.append(_brief_narrative(p_cpi, p_spi, p_pct, p_pm, p_sys))

        result[pid] = {
            "project_name":      sub_tpl["project_name"],
            "pm_eac":            round(pm_eac),
            "explanation":       _brief_narrative(cpi, spi, pct, pm_eac, sys_eac),
            "risk_note":         sub_tpl["risk_note"],
            "prior_explanations": prior_exp,
            "ground_truth":      {"decision": gt.get(pid, "ACCEPT"), "why": ""},
        }

    return result
