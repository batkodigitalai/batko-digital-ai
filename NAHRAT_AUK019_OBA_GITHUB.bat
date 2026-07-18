@echo off
chcp 65001 >nul
title auto1 :: Nahrat obe verze AUK-019 na GitHub Pages
cd /d "%~dp0"

echo [1/2] Nahravam hlavni aukci AUK-019...
python scripts\upload_github_folder.py --folder "aukce_system\20260718_AUK-019_VW_Golf_Variant_2023_Life_DSG" --remote-path "aukce_system/20260718_AUK-019_VW_Golf_Variant_2023_Life_DSG"
if errorlevel 1 goto error

echo [2/2] Nahravam investor brief AUK-019B...
python scripts\upload_github_folder.py --folder "aukce_system\20260718_AUK-019B_Golf_Investor_Brief" --remote-path "aukce_system/20260718_AUK-019B_Golf_Investor_Brief"
if errorlevel 1 goto error

echo Hotovo.
echo Hlavni aukce:
echo https://batkodigitalai.github.io/batko-digital-ai/aukce_system/20260718_AUK-019_VW_Golf_Variant_2023_Life_DSG/index.html
echo Investor brief:
echo https://batkodigitalai.github.io/batko-digital-ai/aukce_system/20260718_AUK-019B_Golf_Investor_Brief/index.html
pause
exit /b 0

:error
echo CHYBA: Upload se nepovedl.
pause
exit /b 1
