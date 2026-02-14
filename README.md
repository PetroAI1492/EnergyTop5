README.md — EnergyTop5
Overview
EnergyTop5 is a fully automated daily intelligence brief that generates a clean, executive‑grade HTML report summarizing the top five energy‑market developments.
The system is designed for deterministic, reproducible, artifact‑only publishing using GitHub Pages.

The pipeline runs locally on a ThinkPad, generates HTML output, and publishes only the final artifacts to GitHub.
All processing logic, scripts, and data remain offline for security, stability, and performance.

Architecture
Local Pipeline (ThinkPad)
All computation, data loading, and HTML rendering occur in:

Code
C:\EnergyTop5
This folder contains:

Python scripts (energy_brief.py, loaders, renderers)

Local archive of historical briefs

Logs and backups

The batch file that runs the pipeline

Git does not track this folder.

GitHub Publishing Shelf
The GitHub repository contains only HTML artifacts:

Code
index.html
archive/
README.md
.gitignore
A strict .gitignore ensures that only HTML files are tracked and published.

GitHub Pages hosts the live brief at:

Code
https://petroai1492.github.io/EnergyTop5/
Daily Workflow
The batch file runs the pipeline:

Loads data

Generates the daily HTML brief

Writes index.html and an archived copy

The batch file copies the HTML artifacts into the Git repo:

Code
C:\mygit\EnergyTop5
Git commits and pushes only:

index.html

archive/YYYYMMDD.html

GitHub Pages updates automatically.

This creates a clean, deterministic, zero‑noise publishing pipeline.

Batch File (run_energy_brief.bat)
The batch file:

Pulls the latest HTML from GitHub

Runs the local pipeline

Copies HTML artifacts into the Git repo

Commits and pushes only HTML

This ensures a stable, conflict‑free workflow.

Repository Philosophy
This repository intentionally contains no code.

No Python

No BAT files

No logs

No data

No pipeline logic

Only the final HTML artifacts are published.

This separation ensures:

Maximum stability

Zero Git conflicts

Clean version history

Clear provenance

A professional, artifact‑grade output

License
This project is maintained privately for personal research and executive‑grade reporting.
No license is applied.

If you want, I can also generate:

a project badge header

a GitHub Pages banner

a “How to Run Locally” section

a Provenance & Data Sources section

a Changelog
