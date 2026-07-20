@echo off
cd /d "%~dp0\..\.."
echo Nahravam Toyota Corolla TS #11010628 na GitHub Pages...
node scripts/upload_single_folder_to_github.js "nabidky_aut\20260528_auto1_11010628_Toyota_Corolla_TS" "20260528_auto1_11010628_Toyota_Corolla_TS"
pause
