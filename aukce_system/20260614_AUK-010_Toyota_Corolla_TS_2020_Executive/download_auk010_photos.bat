@echo off
cd /d "C:\Users\tomas\OneDrive\Dokumenty\Claude\Projects\auto1\aukce_system\20260614_AUK-010_Toyota_Corolla_TS_2020_Executive\img"
echo Stahuji 20 fotek Toyota Corolla AUK-010 z OPENLANE CDN...
echo.

set CDN=https://images.openlane.eu/carimgs/5874937/general
set REF=https://www.openlane.eu/cs/car/info?auctionId=11090843
set UA=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124

curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/272dee63-a46c-4454-9820-6729b68d8551.jpg" -o foto_01.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/0bff92bc-65a2-47c6-aa40-b826f90cdb97.jpg" -o foto_02.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/44021eac-4b29-4d57-a05d-539fafdab45e.jpg" -o foto_03.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/24bbb295-ccd4-4a24-b5fe-4a6929563731.jpg" -o foto_04.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/7631170e-981b-460e-af3c-0e69c92e2fe6.jpg" -o foto_05.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/776e3a86-9ebf-4be0-982c-507a5efefc57.jpg" -o foto_06.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/2ac3cfbf-8cf7-4152-b381-4f3f0aecb73a.jpg" -o foto_07.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/b21b6919-9719-46bf-a20e-fe81804aa6b5.jpg" -o foto_08.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/cf701fcb-afb5-4d2a-9eae-b368a968bd6c.jpg" -o foto_09.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/eda2846e-ad95-4c35-96aa-446657e8929c.jpg" -o foto_10.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/81c77ac8-080b-47ea-bb17-dedccbaadfa3.jpg" -o foto_11.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/b5075df7-736d-4b11-ba84-548fe7159c61.jpg" -o foto_12.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/4f6ae77a-d65f-4b51-a397-e660603de5be.jpg" -o foto_13.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/aefad98d-9802-4e8b-ba5e-36a8d0cd805e.jpg" -o foto_14.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/9643bcfb-54b7-4622-a378-348d761038f6.jpg" -o foto_15.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/cc409004-19e9-4d04-911c-05cb43ffece7.jpg" -o foto_16.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/37ef872c-9e0e-45ae-819a-2041175878ac.jpg" -o foto_17.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/8c237e12-b432-4997-8edb-1ec8f8998b1b.jpg" -o foto_18.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/eb75583d-ff86-419e-9cbb-61f67f638739.jpg" -o foto_19.jpg
curl.exe -L -A "%UA%" -e "%REF%" "%CDN%/5668c7af-2c46-48e2-999a-6c547e2ffadc.jpg" -o foto_20.jpg

echo.
echo Kontrola velikosti fotek (musi byt > 10000 bajtu):
for %%f in (foto_*.jpg) do (
  for %%s in ("%%f") do echo %%f: %%~zs bajtu
)
echo.
echo Hotovo. Zkontroluj chybove hlasky a velikosti souboru.
echo Pokud je soubor mensi nez 5000 bajtu, je to chybova odpoved CDN, ne fotka.
pause
