@echo off
REM --------------------------------------------------
REM ENERGY INTELLIGENCE BRIEF - Automated Run
REM --------------------------------------------------

set REPO_DIR=C:\mygit\EnergyIntelligenceBrief
set LOG_FILE=%REPO_DIR%\run_energy_brief.log
set FAILED=0

echo. >> "%LOG_FILE%"
echo Run started %DATE% %TIME% >> "%LOG_FILE%"

REM --------------------------------------------------
REM Change to repo directory
REM --------------------------------------------------
cd /d "%REPO_DIR%"
if errorlevel 1 (
    echo Failed to change directory >> "%LOG_FILE%"
    set FAILED=1
)

REM --------------------------------------------------
REM Pull latest changes
REM --------------------------------------------------
if %FAILED%==0 (
    git pull --rebase >> "%LOG_FILE%" 2>&1
    if errorlevel 1 set FAILED=1
)

REM --------------------------------------------------
REM Run the ENERGY INTELLIGENCE BRIEF generator
REM --------------------------------------------------
if %FAILED%==0 (
    python energy_brief.py >> "%LOG_FILE%" 2>&1
    if errorlevel 1 set FAILED=1
)

REM --------------------------------------------------
REM Stage + commit only if generation succeeded
REM --------------------------------------------------
if %FAILED%==0 (
    git add index.html archive >> "%LOG_FILE%" 2>&1

    git diff --cached --quiet
    if errorlevel 1 (
        git commit -m "Automated ENERGY INTELLIGENCE BRIEF update" >> "%LOG_FILE%" 2>&1
    ) else (
        echo No changes to commit >> "%LOG_FILE%"
    )

    git push >> "%LOG_FILE%" 2>&1
    if errorlevel 1 set FAILED=1
)

echo Run finished %DATE% %TIME% >> "%LOG_FILE%"

REM --------------------------------------------------
REM Failure-only notification
REM --------------------------------------------------
if %FAILED%==1 (
    powershell -Command ^
      "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; ^
       [System.Windows.Forms.MessageBox]::Show('ENERGY INTELLIGENCE BRIEF FAILED. Check run_energy_brief.log','Energy Brief Failure')"
)

endlocal
