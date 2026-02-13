# render_html.py
from datetime import datetime

def render_html(brief):
    data = brief["data"]

    # Extract table values safely
    brent = data.get("brent")
    wti = data.get("wti")
    crack = data.get("crack")
    stocks = data.get("stocks_total")

    def fmt_price(d):
        if not d:
            return "N/A"
        return f"${d['value']:.2f}"

    def fmt_delta(d):
        if not d:
            return "N/A"
        return f"{d['delta']:+.2f}"

    def fmt_pct(d):
        if not d:
            return "N/A"
        return f"{d['pct']:+.2f}%"

    # Timestamp
    now = datetime.now().strftime("%B %d, %Y %H:%M")

    # ------------------------------------------------------------
    # HTML
    # ------------------------------------------------------------
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Petroleum Morning Brief</title>
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        margin: 40px;
        color: #111;
        line-height: 1.45;
    }}

    h1 {{
        font-size: 28px;
        margin-bottom: 4px;
        font-weight: 600;
    }}

    h2 {{
        font-size: 20px;
        margin-top: 28px;
        margin-bottom: 6px;
        font-weight: 600;
    }}

    .meta {{
        font-size: 13px;
        color: #555;
        margin-bottom: 20px;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 14px;
    }}

    th {{
        text-align: left;
        border-bottom: 2px solid #000;
        padding-bottom: 6px;
        font-weight: 600;
    }}

    td {{
        padding: 6px 0;
        border-bottom: 1px solid #ddd;
    }}

    .section {{
        margin-bottom: 22px;
        font-size: 15px;
    }}

    .footer {{
        margin-top: 40px;
        font-size: 12px;
        color: #666;
    }}
</style>
</head>

<body>

<h1>Petroleum Morning Brief</h1>
<div class="meta">
    Coverage: Last 24 Hours<br>
    Generated: {now}<br>
    Internal Market Intelligence<br>
    Data Quality: EIA ({brief["eia_date"]}) • FRED ({brief["fred_date"]})
</div>

<h2>Executive Snapshot</h2>
<div class="section">{brief["executive_snapshot"]}</div>

<h2>What Changed Since Yesterday</h2>
<div class="section">{brief["what_changed"]}</div>

<h2>Market Signal</h2>
<div class="section">{brief["market_signal"]}</div>

<h2>Market Overview</h2>
<table>
    <tr>
        <th>Instrument</th>
        <th>Price</th>
        <th>Δ (Daily)</th>
        <th>% Change</th>
    </tr>
    <tr>
        <td>Brent Crude</td>
        <td>{fmt_price(brent)}</td>
        <td>{fmt_delta(brent)}</td>
        <td>{fmt_pct(brent)}</td>
    </tr>
    <tr>
        <td>WTI Crude</td>
        <td>{fmt_price(wti)}</td>
        <td>{fmt_delta(wti)}</td>
        <td>{fmt_pct(wti)}</td>
    </tr>
    <tr>
        <td>3-2-1 Crack Spread</td>
        <td>{fmt_price(crack)}</td>
        <td>{fmt_delta(crack)}</td>
        <td>{fmt_pct(crack)}</td>
    </tr>
    <tr>
        <td>U.S. Crude Stocks (EIA)</td>
        <td>{stocks["value"] if stocks else "N/A"} mb</td>
        <td>—</td>
        <td>—</td>
    </tr>
</table>

<h2>Supply & Operations</h2>
<div class="section">{brief["supply_operations"]}</div>

<h2>Demand & Products</h2>
<div class="section">{brief["demand_products"]}</div>

<h2>Regulatory & Geopolitical</h2>
<div class="section">{brief["regulatory_geopolitical"]}</div>

<h2>Risk Radar</h2>
<div class="section">{brief["risk_radar"]}</div>

<h2>Three Things That Matter Today</h2>
<div class="section">{brief["three_things"]}</div>

<h2>Key Decisions & Watchpoints</h2>
<div class="section">{brief["watchpoints"]}</div>

<div class="footer">
© {datetime.now().year} Randy Hinton. All rights reserved.<br>
This brief is an analytical synthesis provided for informational purposes only and does not constitute investment advice.
</div>

</body>
</html>
"""
