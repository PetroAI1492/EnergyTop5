# main.py
import shutil
from datetime import datetime
from pathlib import Path

from generator import generate_brief
from render_html import render_html


# ------------------------------------------------------------
# Sanity check to ensure output is valid and complete
# ------------------------------------------------------------
def sanity_check_output():
    path = Path("index.html")

    if not path.exists():
        raise RuntimeError("Sanity check failed: index.html not created")

    if path.stat().st_size < 2500:
        raise RuntimeError("Sanity check failed: index.html too small")

    html = path.read_text(encoding="utf-8", errors="ignore")

    required_markers = [
        "Executive Snapshot",
        "What Changed Since Yesterday",
        "Market Signal",
        "Market Overview",
        "Supply & Operations",
        "Demand & Products",
        "Regulatory & Geopolitical",
        "Risk Radar",
        "Three Things That Matter Today",
        "Key Decisions & Watchpoints",
    ]

    for marker in required_markers:
        if marker not in html:
            raise RuntimeError(f"Sanity check failed: missing section '{marker}'")


# ------------------------------------------------------------
# Main execution
# ------------------------------------------------------------
if __name__ == "__main__":
    # Generate the full brief (data + narrative)
    brief = generate_brief()

    # Render HTML
    html = render_html(brief)

    # Write latest brief
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # Validate output
    sanity_check_output()

    # Archive immutable daily copy
    today = datetime.now().strftime("%Y%m%d")
    archive_dir = Path("archive")
    archive_dir.mkdir(exist_ok=True)

    archive_path = archive_dir / f"{today}.html"
    shutil.copyfile("index.html", archive_path)

    print("Petroleum Morning Brief generated -> index.html")
