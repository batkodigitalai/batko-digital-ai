// download_photos.js — stáhne 26 fotek AUK-010 do img/
// Spuštění: node download_photos.js
const https = require('https');
const http  = require('http');
const fs    = require('fs');
const path  = require('path');

const TARGET_DIR = path.join(__dirname, 'img');
if (!fs.existsSync(TARGET_DIR)) fs.mkdirSync(TARGET_DIR, { recursive: true });

const BASE = 'https://images.openlane.eu/carimgs/5873873/general/';

const PHOTOS = [
  BASE + 'c5442a49-0da9-43ac-ab68-26bcceb651ed.jpg',   // foto_01
  BASE + '002dc4e9-b55d-4314-a8bf-13f81d4b4669.jpg',   // foto_02
  BASE + 'ddd2bd73-4021-4b94-9eda-fa5f131a8546.jpg',   // foto_03
  BASE + 'da14bd1d-13cd-4efe-9f23-7d616b62c036.jpg',   // foto_04
  BASE + '13f2a159-209b-4afd-82ec-1c9818d24b3c.jpg',   // foto_05
  BASE + '27032e39-3a8c-41ce-80e6-963c306e929a.jpg',   // foto_06
  BASE + '4151a646-7755-472c-bb09-d28b1816be6b.jpg',   // foto_07
  BASE + 'ce0208af-bbef-4c92-82e1-4d4d72dad37e.jpg',   // foto_08
  BASE + 'b9719520-f84c-4838-ac21-6223114be994.jpg',   // foto_09
  BASE + 'd5d2160e-89e4-4357-9dba-2801eaca4b0a.jpg',   // foto_10
  BASE + '54755a1d-fedb-4a63-adcd-454b6b3525b3.jpg',   // foto_11
  BASE + 'c7b1a2d8-1ee4-426e-8304-ae26e7da7029.jpg',   // foto_12
  BASE + 'e57f65b2-52fd-4ab4-aa40-60d627eff9a2.jpg',   // foto_13
  BASE + 'ce350932-0f09-413d-b889-2f8ce747ad02.jpg',   // foto_14
  BASE + '61b7c0f1-cd50-4acc-9c01-15aa76c3d411.jpg',   // foto_15
  BASE + '4366a3e9-1032-4cf9-82d8-e32df04e94a1.jpg',   // foto_16
  BASE + '1386e77e-6618-4d86-bf65-f26da4b821ee.jpg',   // foto_17
  BASE + '893b8ce8-78e0-4d18-bc48-4ca6ed2e045b.jpg',   // foto_18
  BASE + '815de125-2798-41a2-8d4e-2aa0286fd823.jpg',   // foto_19
  BASE + 'b82078b6-83d5-4fcc-8cf6-fd9734dfa396.jpg',   // foto_20
  BASE + '6d6d1547-7e53-4a37-ad8f-d82abc26b5b5.jpg',   // foto_21
  BASE + '0682bb35-dd31-4fc2-8fd8-97e0f5575778.jpg',   // foto_22
  BASE + '7a1371a9-331f-48f6-93a4-4cb14d2758f2.jpg',   // foto_23
  BASE + '85889b04-bb86-4be6-b891-968b49fe0b09.jpg',   // foto_24
  BASE + '76e51b9e-83bd-4e7c-a58c-bd39acc8278d.jpg',   // foto_25
  BASE + 'bccee105-0bac-44af-95a2-c0f88d86b130.jpg',   // foto_26
];

const HEADERS = {
  'Referer':    'https://www.openlane.eu/',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
};

function download(url, dest, depth = 0) {
  if (depth > 5) return Promise.reject(new Error('Příliš mnoho přesměrování'));
  return new Promise((resolve, reject) => {
    const lib = url.startsWith('https') ? https : http;
    const file = fs.createWriteStream(dest);
    lib.get(url, { headers: HEADERS }, res => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        file.close();
        fs.unlinkSync(dest);
        return download(res.headers.location, dest, depth + 1).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        file.close();
        fs.unlinkSync(dest);
        return reject(new Error(`HTTP ${res.statusCode}`));
      }
      res.pipe(file);
      file.on('finish', () => { file.close(); resolve(); });
      file.on('error', err => { fs.unlinkSync(dest); reject(err); });
    }).on('error', err => {
      try { fs.unlinkSync(dest); } catch(e) {}
      reject(err);
    });
  });
}

(async () => {
  console.log(`AUK-010 — stahuji ${PHOTOS.length} fotek do ${TARGET_DIR}\n`);
  let ok = 0, fail = 0;
  for (let i = 0; i < PHOTOS.length; i++) {
    const num  = String(i + 1).padStart(2, '0');
    const dest = path.join(TARGET_DIR, `foto_${num}.jpg`);
    process.stdout.write(`  foto_${num}.jpg ... `);
    try {
      await download(PHOTOS[i], dest);
      const size = fs.statSync(dest).size;
      if (size < 5000) {
        console.log(`CHYBA — příliš malý soubor (${size} B), pravděpodobně chybová odpověď CDN`);
        fs.unlinkSync(dest);
        fail++;
      } else {
        console.log(`OK (${Math.round(size / 1024)} kB)`);
        ok++;
      }
    } catch(err) {
      console.log(`CHYBA — ${err.message}`);
      fail++;
    }
  }
  console.log(`\nHotovo: ${ok} OK, ${fail} chyb`);
  if (fail > 0) console.log('Zkontrolujte přihlášení na openlane.eu nebo zkuste znovu.');
})();
