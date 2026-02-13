# prompts.py

def fmt_change(d):
    if not d:
        return "N/A"
    return f"${d['value']:.2f} ({d['delta']:+.2f}, {d['pct']:+.2f}%)"


# ------------------------------------------------------------
# Bloomberg First Word — Hard System Instructions
# ------------------------------------------------------------
COMMON_SYSTEM_INSTRUCTIONS = """
You are writing a Bloomberg First Word–style crude oil brief.

You must follow these rules:
1. Write exactly 3 sentences per section.
2. Total length must be 60–90 words.
3. Focus strictly on the last 24 hours.
4. Use only the data provided; do not invent numbers, catalysts, history, or context.
5. If no catalyst is provided, attribute moves only to broader sentiment, positioning, or flows.
6. Do not reference OPEC+, shale, regulations, geopolitics, demand trends, or supply drivers unless explicitly provided.
7. Do not reference production levels, operational metrics, disruptions, logistics, refining activity, trading volumes, open interest, or technical levels unless explicitly provided.
8. Do not explain background, history, or long-term themes.
9. No bullets, no lists, no headings inside the generated text.
10. Maintain a tight, declarative, professional tone.
"""


# ------------------------------------------------------------
# Executive Snapshot
# ------------------------------------------------------------
def exec_snapshot_prompt(data):
    return COMMON_SYSTEM_INSTRUCTIONS + f"""
DATA:
Brent: {fmt_change(data['brent'])}
WTI: {fmt_change(data['wti'])}
3-2-1 Crack Spread: {fmt_change(data['crack'])}

TASK:
Write exactly 3 sentences (60–90 words) summarizing the last 24 hours in global crude markets.
Sentence 1: Describe the moves in Brent and WTI using only the numbers above, with no interpretation beyond direction and magnitude.
Sentence 2: Describe what the crack spread signals about margins or product demand, without adding causes or background.
Sentence 3: State what traders will watch next using only generic phrasing (price action, margins, inventories) with no invented catalysts.
"""


# ------------------------------------------------------------
# Market Signal
# ------------------------------------------------------------
def market_signal_prompt(data):
    return COMMON_SYSTEM_INSTRUCTIONS + f"""
DATA:
Crude stocks (latest): {data['stocks_total']}
Crack spread: {data['crack']}
Brent: {data['brent']}
WTI: {data['wti']}

TASK:
Write exactly 3 sentences (60–90 words) assessing whether the physical market appears to be tightening, loosening, or neutral.
Base your conclusion ONLY on the provided price moves, margins, and inventory level.
End the final sentence with one of these labels: [TIGHTENING], [LOOSENING], or [NEUTRAL].
"""


# ------------------------------------------------------------
# Supply & Operations
# ------------------------------------------------------------
def supply_ops_prompt(data):
    return COMMON_SYSTEM_INSTRUCTIONS + """
TASK:
Write exactly 3 sentences (60–90 words) describing near-term supply and operational tone.
You may only speak in generic terms such as "flows," "barrels," "physical tone," or "near-term balance."
You may NOT reference production levels, operational metrics, disruptions, logistics, sentiment, volatility, or any specific supply driver unless explicitly provided.
Focus strictly on what the last 24 hours imply for physical flows using only generic, non-specific language.
"""


# ------------------------------------------------------------
# Demand & Products
# ------------------------------------------------------------
def demand_products_prompt(data):
    return COMMON_SYSTEM_INSTRUCTIONS + """
TASK:
Write exactly 3 sentences (60–90 words) summarizing near-term product demand conditions.
You may only infer demand from margins or crack spreads if provided.
Do not reference seasonal patterns, travel trends, or multi-year dynamics.
Keep the tone tight, data-driven, and focused on the last session.
"""


# ------------------------------------------------------------
# Regulatory & Geopolitical
# ------------------------------------------------------------
def regulatory_geo_prompt(data):
    return COMMON_SYSTEM_INSTRUCTIONS + """
TASK:
Write exactly 3 sentences (60–90 words) summarizing regulatory or geopolitical factors.
If no specific events are provided, speak in general terms about policy or geopolitical uncertainty without inventing details.
Do not reference specific countries, conflicts, regulations, or policy actions unless explicitly given.
"""


# ------------------------------------------------------------
# Watchpoints
# ------------------------------------------------------------
def watchpoints_prompt(data):
    return COMMON_SYSTEM_INSTRUCTIONS + """
TASK:
Write exactly 3 sentences (60–90 words) highlighting key near-term watchpoints.
You may reference only generic elements such as price action, margins, inventories, or shifts in tone.
You may NOT reference technical levels, support/resistance, refining activity, trading volumes, open interest, or any specific market mechanics unless explicitly provided.
Keep the commentary general, actionable, and strictly tied to the last 24 hours.
"""
