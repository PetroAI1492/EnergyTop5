EnergyTop5 — Daily Energy Intelligence Brief
EnergyTop5 is an automated, executive‑grade intelligence brief that identifies the five most strategically important oil and energy articles from the past 48 hours.
It evaluates global and country‑specific signals, classifies relevance, and produces a polished HTML brief suitable for internal decision‑makers.

The brief is generated locally and published to GitHub Pages for easy daily access.

How It Works
The pipeline performs the following steps:

Fetches global and country‑specific energy news  
Sources include Google News RSS feeds filtered for oil, energy, geopolitics, and major producing nations.

Filters articles by time window  
Only items published within the last 48 hours are considered.

Selects the Top 5 articles  
Ranking is based on:

Geopolitical impact

Supply/demand implications

Policy significance

Market sensitivity

Enriches each article  
The script generates:

Signal strength

Country tag

“Why this matters now”

Executive narrative

Builds a clean, professional HTML brief  
Output includes:

index.html (latest brief)

archive/YYYYMMDD.html (daily archive)

Automated publishing  
A batch file (run_energy_brief.bat) runs the generator, commits changes, and pushes updates.

Repository Structure
Code
EnergyTop5/
│
├── archive/               # Daily archived briefs
├── energy_brief.py        # Main intelligence generator
├── run_energy_brief.bat   # Automation script
└── README.md              # This file
After the first run, you will also see:

Code
index.html                 # Latest published brief
archive/YYYYMMDD.html      # Daily archive entry
Running the Brief
To generate and publish the daily brief:

Code
run_energy_brief.bat
The batch file will:

Pull the latest repo changes

Run the intelligence generator

Commit new output

Push updates to GitHub

If the run fails, a Windows notification will appear.

Requirements
Python 3.10+

feedparser

openai Python client

A valid OpenAI API key stored at:

Code
C:\mygit\secrets\openai.key
Purpose
EnergyTop5 is designed as a fast, deterministic, executive‑ready intelligence product that cuts through noise and highlights only the most strategically relevant global energy developments.

It is optimized for:

Daily situational awareness

Executive briefings

Geopolitical monitoring

Market‑moving signal detection

If you want, I can also generate:

A .gitignore

A GitHub Pages–ready index.html header

A repo description

A commit message template

Just tell me what you want next.
