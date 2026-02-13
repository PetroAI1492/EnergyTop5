import os
import shutil
from datetime import datetime
from pathlib import Path

from openai import OpenAI
from render_html import render_html

# ---------------------------------------------------------
# Load OpenAI API Key Safely
# ---------------------------------------------------------
def load_openai_key():
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return key

    try:
        with open("secrets/openai.key", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise RuntimeError(
            "OpenAI key not found. Add it to secrets/openai.key or set OPENAI_API_KEY env variable."
        )

OPENAI_API_KEY = load_openai_key()
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------------------------------------------------
# Helper: Generate a section with a controlled prompt
# ---------------------------------------------------------
def generate_section(title, instructions):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        max_tokens=500,
        messages=[
            {
                "role": "system",
                "content": "You are a senior petroleum market analyst writing for executives."
            },
            {
                "role": "user",
                "content": f"{instructions}"
            }
        ]
    )
    return response.choices[0].message.content.strip()

# ---------------------------------------------------------
# Sanity check for generated output
# ---------------------------------------------------------
def sanity_check_output():
    path = Path("index.html")

    if not path.exists():
        raise RuntimeError("Sanity check failed: index.html not created")

    if path.stat().st_size < 5_000:
        raise RuntimeError("Sanity check failed: index.html too small")

    html = path.read_text(encoding="utf-8", errors="ignore")

    required_markers = [
        "Executive Snapshot",
        "Market Signal",
        "Market Overview",
        "Supply & Operations",
        "Demand & Products",
        "Regulatory & Geopolitical",
        "Key Decisions & Watchpoints",
    ]

    for marker in required_markers:
        if marker not in html:
            raise RuntimeError(
                f"Sanity check failed: missing section '{marker}'"
            )

# ---------------------------------------------------------
# Generate the full structured brief
# ---------------------------------------------------------
def generate_brief():
    brief = {}

    # Executive Snapshot
    brief["executive_snapshot"] = generate_section(
        "Executive Snapshot",
        "Do NOT include headings, bullet points, markdown, section titles, labels, or lists. "
        "Write clean, professional paragraphs only. "
        "Summarize the last 24 hours in global crude markets in an executive tone. "
        "Reference Brent, WTI, and crack spreads naturally in narrative form. "
        "Focus on price direction, market tone, and the dominant drivers influencing sentiment."
    )

    # Market Signal
    brief["market_signal"] = generate_section(
        "Market Signal",
        "Do NOT include headings, bullet points, markdown, section titles, labels, or lists. "
        "Write clean, professional paragraphs only. "
        "Assess whether the physical oil market is tightening, loosening, or neutral over the last 24 hours. "
        "Base the assessment on inventories, refining margins, OPEC+ discipline, and price action. "
        "Conclude with a single clear regime label in brackets: [TIGHTENING], [LOOSENING], or [NEUTRAL]. "
        "Tone: decisive, institutional, physical-market focused."
    )

    # Market Overview (table rows only)
    brief["market_overview"] = generate_section(
        "Market Overview",
        "Generate exactly three HTML <tr> rows for a Bloomberg-style market table. "
        "Rows must be: Brent Crude, WTI Crude, and the 3-2-1 crack spread. "
        "For EACH row, output four <td> cells in this exact order: "
        "1) Instrument name, 2) Current price (e.g., $92.45), "
        "3) Daily dollar change wrapped in <span class='pos'> or <span class='neg'>, "
        "4) Daily percentage change wrapped in <span class='pos'> or <span class='neg'>. "
        "Use <span class='pos'> for positive values and <span class='neg'> for negative values. "
        "Do NOT output headers, commentary, markdown, or labels. "
        "Output ONLY three <tr>...</tr> rows and nothing else."
    )

    # Supply & Operations
    brief["supply_operations"] = generate_section(
        "Supply & Operations",
        "Do NOT include headings, bullet points, markdown, section titles, labels, or lists. "
        "Write clean, professional paragraphs only. "
        "Analyze supply-side conditions affecting physical crude markets, including OPEC+ compliance, "
        "U.S. shale output, inventory trends, and operational or logistical constraints. "
        "Maintain an analytical, executive tone."
    )

    # Demand & Products
    brief["demand_products"] = generate_section(
        "Demand & Products",
        "Do NOT include headings, bullet points, markdown, section titles, labels, or lists. "
        "Write clean, professional paragraphs only. "
        "Discuss demand conditions across major refined products, including gasoline, diesel, and jet fuel, "
        "and their influence on refining margins. "
        "Focus on near-term physical demand signals rather than long-term forecasts."
    )

    # Regulatory & Geopolitical
    brief["regulatory_geopolitical"] = generate_section(
        "Regulatory & Geopolitical",
        "Do NOT include headings, bullet points, markdown, section titles, labels, or lists. "
        "Write clean, professional paragraphs only. "
        "Summarize the most relevant regulatory developments and geopolitical risks influencing crude oil supply, "
        "trade flows, and market sentiment over the last 24 hours. "
        "Prioritize material impacts on physical markets."
    )

    # Key Decisions & Watchpoints
    brief["watchpoints"] = generate_section(
        "Key Decisions & Watchpoints",
        "Do NOT include headings, bullet points, markdown, section titles, labels, or lists. "
        "Write clean, professional paragraphs only. "
        "Highlight the most important near-term considerations executives should monitor, "
        "focusing on factors that could materially alter supply, demand, or price dynamics."
    )

    return brief

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    brief = generate_brief()
    html = render_html(brief)

    # Write latest brief
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Sanity check before archive + git
    sanity_check_output()

    # Archive immutable daily copy
    today = datetime.now().strftime("%Y%m%d")

    archive_dir = Path("archive")
    archive_dir.mkdir(exist_ok=True)

    archive_path = archive_dir / f"{today}.html"
    shutil.copyfile("index.html", archive_path)

    print("Petroleum Morning Brief generated -> index.html")
