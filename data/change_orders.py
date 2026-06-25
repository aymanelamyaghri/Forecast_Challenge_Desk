"""
Change order register and project contract metadata.
These represent the real-world complexity PMs often omit from their EAC narratives:
  - Pending variations not yet priced into the forecast
  - Disputed back-charges that may or may not materialise
  - Known risks that have been quantified but not yet formally submitted

CONTRACT TYPES (affects who bears cost overrun risk):
  LUMP_SUM     -- fixed price; contractor absorbs cost overrun but client bears delay risk
  REIMBURSABLE -- client pays all actual costs; finance must catch PM optimism directly
  TARGET_COST  -- pain/gain share; incentive to stay near target but less skin in game than LS
"""

# Project-level metadata (not in EVM data)
PROJECT_META = {
    "P01": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 3, "contractor": "North Offshore Ltd"},
    "P02": {"contract_type": "REIMBURSABLE", "open_risks_above_500k": 5, "contractor": "GCC Infra JV"},
    "P03": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 0, "contractor": "Antipodean Civil"},
    "P04": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 1, "contractor": "Gulf Coast Engineering"},
    "P05": {"contract_type": "REIMBURSABLE", "open_risks_above_500k": 1, "contractor": "SEA Fitout Partners"},
    "P06": {"contract_type": "REIMBURSABLE", "open_risks_above_500k": 6, "contractor": "Cairo EPC Group"},
    "P07": {"contract_type": "TARGET_COST",  "open_risks_above_500k": 2, "contractor": "Northern Roads Alliance"},
    "P08": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 2, "contractor": "SG Process Systems"},
    "P09": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 0, "contractor": "Deutsche Bau GmbH"},
    "P10": {"contract_type": "REIMBURSABLE", "open_risks_above_500k": 7, "contractor": "IndoCon Marine"},
    "P11": {"contract_type": "REIMBURSABLE", "open_risks_above_500k": 2, "contractor": "Nordic Wind AS"},
    "P12": {"contract_type": "TARGET_COST",  "open_risks_above_500k": 1, "contractor": "Trans-Canada Civil"},
    "P13": {"contract_type": "REIMBURSABLE", "open_risks_above_500k": 4, "contractor": "Riyadh Builders Co"},
    "P14": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 0, "contractor": "WA Mining Constructors"},
    "P15": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 1, "contractor": "Cape Civil Works"},
    "P16": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 0, "contractor": "AMS Fitout BV"},
    "P17": {"contract_type": "REIMBURSABLE", "open_risks_above_500k": 8, "contractor": "West Africa Pipeline Co"},
    "P18": {"contract_type": "TARGET_COST",  "open_risks_above_500k": 3, "contractor": "Pacific Civil Ventures"},
    "P19": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 1, "contractor": "Gulf Aviation Builders"},
    "P20": {"contract_type": "LUMP_SUM",     "open_risks_above_500k": 0, "contractor": "Balkan Utilities Ltd"},
}

# Change orders per project.
# status:  "approved" | "pending" | "disputed"
# in_eac:  True = PM has included this in their submitted EAC
#          False = PM has NOT included this — represents hidden future cost
# significance: "material" | "minor" | "watch"
CHANGE_ORDERS = {
    "P01": [
        {
            "ref": "CO-P01-003",
            "desc": "Jacket interface rework — scope not yet fully quantified",
            "value": 2_500_000, "status": "disputed", "in_eac": False,
            "significance": "material",
            "note": "Disputed between NIG and contractor. If awarded to contractor, goes straight to overrun.",
        },
        {
            "ref": "CO-P01-004",
            "desc": "Q1 offshore campaign extension — weather mitigation",
            "value": 1_100_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Extension agreed in principle but not formally priced. PM's recovery plan depends on this working.",
        },
    ],
    "P02": [
        {
            "ref": "CO-P02-007",
            "desc": "FX provisions — UAE subcontractor packages (AED exposure)",
            "value": 1_800_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "FX hedge expired. Remaining AED packages unhedged at current rates.",
        },
        {
            "ref": "CO-P02-008",
            "desc": "Civil interface redesign — new to existing station connections",
            "value": 2_200_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Design sign-off outstanding. Cost estimate preliminary.",
        },
    ],
    "P03": [],
    "P04": [
        {
            "ref": "CO-P04-002",
            "desc": "Electrical subcontractor back-charge (NIG to recover)",
            "value": -350_000, "status": "disputed", "in_eac": True,
            "significance": "minor",
            "note": "PM has included this recovery in EAC. Outcome uncertain — disputed claim.",
        },
    ],
    "P05": [],
    "P06": [
        {
            "ref": "CO-P06-005",
            "desc": "Additional foundation piling — unexpected soil conditions",
            "value": 5_200_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Geotechnical assessment complete. Additional piling scope fully quantified but not submitted to PM EAC.",
        },
        {
            "ref": "CO-P06-006",
            "desc": "Civil re-sequencing premium — mobilisation/demobilisation cycles",
            "value": 1_100_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Three additional mob/demob cycles required due to soil conditions. Not priced in PM EAC.",
        },
    ],
    "P07": [
        {
            "ref": "CO-P07-003",
            "desc": "Acceleration programme — extended hours and weekend premium rates",
            "value": 1_650_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Contractor invoices not yet received. PM says acceleration 'within contingency' but contingency is 75% consumed.",
        },
    ],
    "P08": [
        {
            "ref": "CO-P08-004",
            "desc": "Regulatory review point 3 — additional commissioning testing",
            "value": 620_000, "status": "pending", "in_eac": False,
            "significance": "watch",
            "note": "MAS has indicated a third review point. Cost estimate based on prior review durations.",
        },
    ],
    "P09": [],
    "P10": [
        {
            "ref": "CO-P10-008",
            "desc": "Marine equipment procurement premium — supply chain surcharge",
            "value": 2_100_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Specialist marine crane confirmed at premium rate. PM has not updated EAC.",
        },
        {
            "ref": "CO-P10-009",
            "desc": "Offshore labour acceleration — additional crew mobilisation",
            "value": 1_400_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Two additional offshore crews mobilised this month. Premium rates apply. Invoices outstanding.",
        },
    ],
    "P11": [],
    "P12": [
        {
            "ref": "CO-P12-005",
            "desc": "Winter working conditions — heating, lighting, ground preparation",
            "value": 350_000, "status": "approved", "in_eac": True,
            "significance": "minor",
            "note": "Approved and included in EAC. No exposure.",
        },
    ],
    "P13": [
        {
            "ref": "CO-P13-006",
            "desc": "M&E specialist design iterations — medical equipment interfaces",
            "value": 1_400_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Three specialist design iterations required beyond original scope. Not in PM EAC.",
        },
        {
            "ref": "CO-P13-007",
            "desc": "HVAC integration — hospital infection control requirements",
            "value": 880_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Regulatory requirement identified post-contract. Client acknowledges but formal CO not raised.",
        },
    ],
    "P14": [],
    "P15": [
        {
            "ref": "CO-P15-003",
            "desc": "Membrane procurement lead time premium — air freight vs sea freight",
            "value": 380_000, "status": "approved", "in_eac": True,
            "significance": "minor",
            "note": "Approved. In PM EAC. No hidden exposure.",
        },
    ],
    "P16": [
        {
            "ref": "CO-P16-002",
            "desc": "IT equipment delivery premium — US export compliance delay",
            "value": 95_000, "status": "pending", "in_eac": True,
            "significance": "minor",
            "note": "Minor. Included in PM EAC contingency provision.",
        },
    ],
    "P17": [
        {
            "ref": "CO-P17-009",
            "desc": "FX exposure — unhedged 40% of remaining procurement (NGN/USD)",
            "value": 3_200_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "PM has hedged 60% of procurement exposure. 40% remains at spot rate risk. Current NGN weakness adds ~$3.2M.",
        },
        {
            "ref": "CO-P17-010",
            "desc": "Swamp crossing rework — additional survey and remediation",
            "value": 2_800_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Geotechnical survey of swamp sections not complete. Preliminary estimate $2.8M but could be higher.",
        },
    ],
    "P18": [
        {
            "ref": "CO-P18-004",
            "desc": "Contamination remediation Zone 1 & 2 — pending client approval",
            "value": 4_000_000, "status": "pending", "in_eac": True,
            "significance": "material",
            "note": "Included in PM EAC but CLIENT HAS NOT APPROVED. If rejected, this becomes contractor risk.",
        },
        {
            "ref": "CO-P18-005",
            "desc": "Zone 3 residual contamination — unexcavated, risk only",
            "value": 2_500_000, "status": "pending", "in_eac": False,
            "significance": "material",
            "note": "Zone 3 not yet excavated. Contamination likely based on historical site records. Not in PM EAC.",
        },
    ],
    "P19": [
        {
            "ref": "CO-P19-003",
            "desc": "Passenger interface design variation — client-requested change",
            "value": 520_000, "status": "approved", "in_eac": True,
            "significance": "minor",
            "note": "Client variation, approved and funded. In EAC. No exposure.",
        },
    ],
    "P20": [
        {
            "ref": "CO-P20-002",
            "desc": "Defects reinstatement reserve — liability period",
            "value": 180_000, "status": "pending", "in_eac": True,
            "significance": "minor",
            "note": "Standard reserve. In EAC. No hidden exposure.",
        },
    ],
}
