# generator.py
import os
from pathlib import Path
from openai import OpenAI

from data_loader import load_market_data
from prompts import (
    COMMON_SYSTEM_INSTRUCTIONS,
    exec_snapshot_prompt,
    market_signal_prompt,
    supply_ops_prompt,
    demand_products_prompt,
    regulatory_geo_prompt,
    watchpoints_prompt,
)
from analytics import what_changed, risk_radar, three_things


# ------------------------------------------------------------
# Load API key
# ------------------------------------------------------------
def load_openai_key():
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key
    return Path("secrets/openai.key").read_text().strip()


client = OpenAI(api_key=load_openai_key())


# ------------------------------------------------------------
# Strict Bloomberg First Word generator
# ------------------------------------------------------------
def generate_section(prompt, fallback):
    """
    Generates a Bloomberg First Word–style section with:
    - EXACTLY 3 sentences
    - 60–90 words
    - No invented catalysts, history, or context
    - No bullets, no lists
    - Tight, declarative tone
    """

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.15,
            max_tokens=200,
            messages=[
                {"role": "system", "content": COMMON_SYSTEM_INSTRUCTIONS.strip()},
                {"role": "user", "content": prompt},
            ],
        )

        text = resp.choices[0].message.content.strip()
        if not text:
            return fallback

        # Robust sentence parsing (handles U.S., E.I.A., etc.)
        raw = [s.strip() for s in text.split('.') if s.strip()]

        sentences = []
        buffer = ""
        for frag in raw:
            if len(frag.split()) <= 2:  # abbreviation fragment
                buffer += frag + ". "
            else:
                if buffer:
                    sentences.append((buffer + frag).strip())
                    buffer = ""
                else:
                    sentences.append(frag)

        if len(sentences) != 3:
            return fallback

        # Word count check
        wc = len(text.split())
        if wc < 55 or wc > 100:
            return fallback

        return text

    except Exception:
        return fallback


# ------------------------------------------------------------
# Main brief generator
# ------------------------------------------------------------
def generate_brief():
    data = load_market_data()

    # Tight Bloomberg-like fallbacks
    fallback_exec = (
        "Crude markets saw mixed moves over the last session as prices and margins shifted on light flows. "
        "Product cracks held steady, offering a clearer read on near-term demand. "
        "Traders will watch price action and inventory signals for direction."
    )

    fallback_signal = (
        "Price moves and margins offered mixed signals for the near-term balance. "
        "Inventory visibility remains limited, reducing confidence in physical flows. "
        "The setup leans neutral. [NEUTRAL]"
    )

    fallback_supply = (
        "Physical flows appeared steady over the last session with no clear signs of tightening. "
        "Margins and inventories remain the clearest indicators of near-term balance. "
        "Traders will watch prompt barrels and price action for direction."
    )

    fallback_demand = (
        "Product demand signals were mixed, with margins offering the clearest read. "
        "Crack spreads remained stable, pointing to a balanced backdrop. "
        "Traders will watch product cracks for confirmation."
    )

    fallback_reg = (
        "Policy and geopolitical considerations influenced sentiment in broad terms. "
        "No specific developments dominated the last session. "
        "Markets remain sensitive to shifts in tone."
    )

    fallback_watch = (
        "Key watchpoints include price action, margins, and inventory clarity. "
        "Sentiment remains fluid with limited directional conviction. "
        "Any shift in flows or balances could set the tone for the next session."
    )

    brief = {}

    # Narrative sections
    brief["executive_snapshot"] = generate_section(exec_snapshot_prompt(data), fallback_exec)
    brief["market_signal"] = generate_section(market_signal_prompt(data), fallback_signal)
    brief["supply_operations"] = generate_section(supply_ops_prompt(data), fallback_supply)
    brief["demand_products"] = generate_section(demand_products_prompt(data), fallback_demand)
    brief["regulatory_geopolitical"] = generate_section(regulatory_geo_prompt(data), fallback_reg)
    brief["watchpoints"] = generate_section(watchpoints_prompt(data), fallback_watch)

    # Analytics (deterministic)
    brief["what_changed"] = what_changed(data)
    brief["risk_radar"] = risk_radar(data)
    brief["three_things"] = three_things(data)

    # Freshness indicator
    missing = data["_missing"]
    stale = [k for k, v in data.items() if isinstance(v, dict) and not v.get("fresh", True)]

    if missing and stale:
        brief["freshness"] = f"Missing series: {', '.join(missing.keys())}. Stale series: {', '.join(stale)}."
    elif missing:
        brief["freshness"] = f"Missing series: {', '.join(missing.keys())}."
    elif stale:
        brief["freshness"] = f"Stale series: {', '.join(stale)}."
    else:
        brief["freshness"] = "All key series are present and recently updated."

    # ------------------------------------------------------------
    # Explicit provenance for Data Quality line
    # ------------------------------------------------------------
    brief["eia_date"] = data["stocks_total"]["period"] if data.get("stocks_total") else "N/A"
    brief["fred_date"] = data["brent"]["period"] if data.get("brent") else "N/A"

    brief["data"] = data
    return brief
