# analytics.py

def what_changed(data):
    """
    A compressed, declarative summary of price moves.
    This is NOT a 3-sentence section — it's a short analytic block
    used inside the HTML brief.
    """

    parts = []

    brent = data.get("brent")
    wti = data.get("wti")
    crack = data.get("crack")

    # Brent
    if brent:
        if brent["delta"] > 0:
            parts.append(f"Brent firmed, rising {brent['delta']:+.2f} ({brent['pct']:+.2f}%).")
        elif brent["delta"] < 0:
            parts.append(f"Brent softened, falling {brent['delta']:+.2f} ({brent['pct']:+.2f}%).")
        else:
            parts.append("Brent was steady.")
    else:
        parts.append("Brent data was unavailable.")

    # WTI
    if wti:
        if wti["delta"] > 0:
            parts.append(f"WTI tracked higher, gaining {wti['delta']:+.2f} ({wti['pct']:+.2f}%).")
        elif wti["delta"] < 0:
            parts.append(f"WTI moved lower, losing {wti['delta']:+.2f} ({wti['pct']:+.2f}%).")
        else:
            parts.append("WTI was steady.")
    else:
        parts.append("WTI data was unavailable.")

    # Crack spreads
    if crack:
        if crack["delta"] > 0:
            parts.append(f"Crack spreads widened, rising {crack['delta']:+.2f} ({crack['pct']:+.2f}%).")
        elif crack["delta"] < 0:
            parts.append(f"Crack spreads narrowed, falling {crack['delta']:+.2f} ({crack['pct']:+.2f}%).")
        else:
            parts.append("Crack spreads were unchanged.")
    else:
        parts.append("Crack spread data was unavailable.")

    return " ".join(parts)


def risk_radar(data):
    """
    A compressed, declarative risk summary.
    No invented catalysts, no speculation.
    """

    crack = data.get("crack")
    brent = data.get("brent")
    stocks = data.get("stocks_total")

    parts = []

    # Inventory visibility
    if stocks and stocks.get("fresh", False):
        parts.append("Inventory levels offer a clearer read on near-term balances.")
    else:
        parts.append("Inventory visibility is limited by stale or missing data.")

    # Margins
    if crack and crack["value"] is not None:
        if crack["value"] > 15:
            parts.append("Refining margins remain firm, supporting product demand.")
        else:
            parts.append("Refining margins are more moderate, pointing to a balanced product backdrop.")
    else:
        parts.append("Refining margin signals are unclear due to missing data.")

    # Price tone
    if brent and brent["value"] is not None:
        parts.append("Crude prices remain sensitive to shifts in macro tone and positioning.")

    return " ".join(parts)


def three_things(data):
    """
    A compressed, declarative 3-part summary.
    Not a 3-sentence section — this is a short analytic block.
    """

    brent = data.get("brent")
    stocks = data.get("stocks_total")
    crack = data.get("crack")

    parts = []

    # Price tone
    if brent:
        if brent["delta"] > 0:
            parts.append("Crude prices firmed, reflecting a modest improvement in sentiment.")
        elif brent["delta"] < 0:
            parts.append("Crude prices eased as traders adopted a more cautious tone.")
        else:
            parts.append("Crude prices were steady with limited directional signals.")
    else:
        parts.append("Price signals were unclear due to missing Brent data.")

    # Inventory clarity
    if stocks:
        if stocks.get("fresh", False):
            parts.append("The latest crude stock level remains a key gauge of physical tightness.")
        else:
            parts.append("Stale inventory data limits clarity on the underlying balance.")
    else:
        parts.append("No recent crude stock reading was available.")

    # Margins
    if crack:
        if crack["value"] > 15:
            parts.append("Refining margins remain strong, supporting robust product runs.")
        else:
            parts.append("Margins are more moderate, suggesting a balanced product environment.")
    else:
        parts.append("Refining margin signals were unavailable.")

    return " ".join(parts)
