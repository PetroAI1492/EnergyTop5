import os
import json
import feedparser
from datetime import datetime, timedelta, timezone
from openai import OpenAI

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
SECRETS_DIR = r"c:\mygit\secrets"
OPENAI_KEY_PATH = os.path.join(SECRETS_DIR, "openai.key")
MODEL_NAME = "gpt-4o-mini"
ARCHIVE_DIR = "archive"

GLOBAL_QUERY = (
    "oil+OR+energy+OR+crude+OR+OPEC+OR+gasoline+OR+%22fossil+fuels%22+when:2d"
)

COUNTRY_QUERY = (
    "China+OR+Russia+OR+India+OR+Venezuela+OR+USA+OR+Saudi+Arabia+OR+Iran+OR+Iraq+"
    "OR+UAE+OR+Brazil+OR+Nigeria+OR+Mexico+OR+Libya+OR+Norway+OR+Qatar+OR+Canada+OR+Kazakhstan+when:2d"
)

NOW = datetime.now(timezone.utc)
WINDOW_START = NOW - timedelta(days=2)

# ---------------------------------------------------------
# LOAD KEY + CLIENT
# ---------------------------------------------------------
def load_key(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

OPENAI_KEY = load_key(OPENAI_KEY_PATH)
client = OpenAI(api_key=OPENAI_KEY)

# ---------------------------------------------------------
# TIME WINDOW CHECK
# ---------------------------------------------------------
def within_window(pubdate):
    try:
        dt = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
        dt = dt.replace(tzinfo=timezone.utc)
        return dt >= WINDOW_START
    except:
        return False

# ---------------------------------------------------------
# GOOGLE RSS URL
# ---------------------------------------------------------
def google_rss_url(query):
    return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

# ---------------------------------------------------------
# FETCH ARTICLES
# ---------------------------------------------------------
def fetch_rss_articles():
    feeds = [
        google_rss_url(GLOBAL_QUERY),
        google_rss_url(COUNTRY_QUERY)
    ]

    articles = []

    for url in feeds:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            pubdate = entry.get("published", "")
            if not within_window(pubdate):
                continue

            source_title = "Unknown Source"
            source_obj = entry.get("source")
            if isinstance(source_obj, dict):
                source_title = source_obj.get("title", "Unknown Source")

            articles.append({
                "title": entry.get("title"),
                "url": entry.get("link"),
                "description": entry.get("summary", ""),
                "published": pubdate,
                "source": source_title
            })

    return articles

# ---------------------------------------------------------
# SAFE JSON PARSER
# ---------------------------------------------------------
def parse_json_safely(raw):
    cleaned = raw.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError("Model did not return valid JSON.")

# ---------------------------------------------------------
# PICK TOP 5 ARTICLES
# ---------------------------------------------------------
def pick_top_articles(articles):
    prompt = f"""
You are an energy‑market analyst. From the list below, select the TOP 5 most important
oil/energy articles from the past 48 hours.

Rank them by:
1. Geopolitical impact
2. Supply/demand implications
3. Policy significance
4. Market sensitivity

Return ONLY a JSON list of 5 objects.
No markdown. No commentary.

Each object must contain:
"title", "url", "description", "published", "source"

Articles:
{articles}
"""

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = completion.choices[0].message.content or ""
    top5 = parse_json_safely(raw)

    if not isinstance(top5, list) or len(top5) == 0:
        raise ValueError("Model did not return a valid list.")

    return top5[:5]

# ---------------------------------------------------------
# SIGNAL STRENGTH
# ---------------------------------------------------------
def generate_signal_strength(article):
    prompt = f"""
Classify the strategic relevance of this energy article.

Return ONE of:
High geopolitical relevance
High market relevance
Moderate relevance
Low relevance

Return ONLY the label.

Article:
{article}
"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return (completion.choices[0].message.content or "").strip()

# ---------------------------------------------------------
# WHY NOW
# ---------------------------------------------------------
def generate_why_now(article):
    prompt = f"""
Write ONE sentence explaining why this article matters right now
for an energy‑sector executive.

No markdown.

Article:
{article}
"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return (completion.choices[0].message.content or "").strip()

# ---------------------------------------------------------
# EXECUTIVE NARRATIVE
# ---------------------------------------------------------
def generate_narrative(article):
    prompt = f"""
Write a concise, 3–5 sentence executive‑grade narrative explaining:
- why this article matters,
- the strategic or geopolitical implications,
- what an energy‑sector executive should take away.

No markdown.

Article:
{article}
"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return (completion.choices[0].message.content or "").strip()

# ---------------------------------------------------------
# COUNTRY TAG
# ---------------------------------------------------------
def generate_country_tag(article):
    prompt = f"""
Tag the PRIMARY country associated with this energy article.

Return ONLY ONE of:
China, Russia, India, Venezuela, USA, Saudi Arabia, Iran, Iraq, UAE, Brazil,
Nigeria, Mexico, Libya, Norway, Qatar, Canada, Kazakhstan, Global

Return ONLY the country name.

Article:
{article}
"""
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    return (completion.choices[0].message.content or "").strip()

# ---------------------------------------------------------
# BUILD HTML
# ---------------------------------------------------------
def build_html(enriched_articles):
    today = datetime.now().strftime("%B %d, %Y")

    sections = ""
    for idx, a in enumerate(enriched_articles, start=1):
        sections += f"""
      <div class="article-block">
        <div class="rank-badge">#{idx}</div>
        <div class="country-tag">{a['country']}</div>

        <div class="kicker">Most Important Article #{idx}</div>

        <h1>{a['title']}</h1>

        <div class="subhead">{a['description']}</div>

        <div class="signal">Signal Strength: {a['signal']}</div>

        <div class="attribution">
          Source: {a['source']}<br>
          Published: {a['published']}<br>
          <a href="{a['url']}">Read full article</a>
        </div>

        <div class="why-now">
          <strong>Why This Matters Now:</strong> {a['why_now']}
        </div>

        <div class="narrative">
          {a['narrative']}
        </div>
      </div>
      <hr class="divider">
"""

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Energy Intelligence Brief – Top 5</title>
<style>
  body {{
    margin: 0;
    padding: 0;
    background-color: #f4f4f5;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #111;
  }}
  .page {{
    max-width: 900px;
    margin: 40px auto;
    background-color: #ffffff;
    border: 1px solid #d8d8dc;
    box-shadow: 0 2px 6px rgba(0,0,0,0.06);
  }}
  .header {{
    padding: 18px 24px;
    border-bottom: 1px solid #2a2d33;
    background: #0b0c10;
    color: #f5f5f5;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }}
  .brand {{
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}
  .section-label {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #a0a4b0;
  }}
  .dateline {{
    font-size: 12px;
    color: #c5c7d0;
    text-align: right;
  }}
  .content {{
    padding: 24px 28px 28px 28px;
  }}
  .article-block {{
    margin-bottom: 28px;
  }}
  .rank-badge {{
    display: inline-block;
    background-color: #11141c;
    color: #f5f5f5;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 6px;
  }}
  .country-tag {{
    display: inline-block;
    margin-left: 8px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    color: #4b4f5c;
  }}
  .kicker {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #a0a4b0;
    margin-top: 6px;
    margin-bottom: 8px;
  }}
  h1 {{
    font-size: 20px;
    line-height: 1.25;
    margin: 0 0 10px 0;
    font-weight: 700;
  }}
  .subhead {{
    font-size: 14px;
    color: #4b4f5c;
    margin-bottom: 12px;
  }}
  .signal {{
    font-size: 13px;
    color: #2a2d33;
    margin-bottom: 8px;
    font-weight: 600;
  }}
  .attribution {{
    font-size: 12px;
    color: #6b6f7c;
    margin-bottom: 12px;
  }}
  .why-now {{
    margin-top: 8px;
    font-size: 13px;
    color: #22252f;
  }}
  .narrative {{
    margin-top: 10px;
    font-size: 13px;
    line-height: 1.6;
    color: #22252f;
  }}
  .divider {{
    border: none;
    border-top: 1px solid #e0e1e6;
    margin: 24px 0;
  }}
  .footer {{
    padding: 14px 24px 18px 24px;
    border-top: 1px solid #d8d8dc;
    background-color: #fafbfc;
    font-size: 11px;
    color: #7a7f8c;
  }}
</style>
</head>

<body>
  <div class="page">

    <div class="header">
      <div>
        <div class="brand">ENERGY INTELLIGENCE BRIEF</div>
        <div class="section-label">Top 5 Articles • Last 48 Hours</div>
      </div>
      <div class="dateline">{today}</div>
    </div>

    <div class="content">
      {sections}
    </div>

    <div class="footer">
      © 2026 Randy Hinton. All rights reserved. Internal briefing only.
    </div>

  </div>
</body>
</html>
"""
    return html

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    # ALWAYS create archive folder first
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)

    articles = fetch_rss_articles()

    if not articles:
        print("No oil/energy articles found in the last 48 hours.")
    else:
        top5 = pick_top_articles(articles)

        enriched = []
        for a in top5:
            enriched.append({
                "title": a["title"],
                "url": a["url"],
                "description": a["description"],
                "published": a["published"],
                "source": a["source"],
                "signal": generate_signal_strength(a),
                "why_now": generate_why_now(a),
                "narrative": generate_narrative(a),
                "country": generate_country_tag(a)
            })

        html = build_html(enriched)

        # Write main brief
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Write archive copy
        archive_name = datetime.now().strftime(os.path.join(ARCHIVE_DIR, "%Y%m%d.html"))
        with open(archive_name, "w", encoding="utf-8") as f:
            f.write(html)

        print("index.html and archive copy created successfully.")
