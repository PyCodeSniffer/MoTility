@echo off

mode con: cols=112 lines=20

set "INSTALLER=py\python-manager-26.2.msix"

python --version >nul 2>&1

if %ERRORLEVEL% equ 0 (
    echo [OK] Python erkannt. Starte MOTILITY...
    git pull
    python -m pip install -r py\requirements.txt
    python py\main.py
) else (
    echo [!] Python nicht gefunden.
    if exist "%INSTALLER%" (
        echo Starte Installer: %INSTALLER%
        start "" "%INSTALLER%"
    ) else (
        echo [FEHLER] %INSTALLER% fehlt!
    )
)
pause