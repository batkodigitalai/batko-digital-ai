// download_photos.js — stáhne 10 fotek AUK-009 do img/
const https = require('https');
const fs = require('fs');
const path = require('path');

const TARGET_DIR = path.join(__dirname, 'img');
if (!fs.existsSync(TARGET_DIR)) fs.mkdirSync(TARGET_DIR);

const PHOTOS = [
  "https://images.openlane.eu/carimgs/5875023/general/5991aea0-de02-43db-9559-8fd8ecaee9e9.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/24da1b41-7b8a-43d9-be93-d191d8d93db9.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/d5196a17-128e-44c3-bbbd-7ed0193db713.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/750e6465-5cdc-4aa9-ab68-77d504998b19.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/5702118b-e235-47ac-b1bb-2fc1276d8b22.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/f3373bbd-0a1f-41b8-8287-5322dcd2020d.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/5ebaae25-43c0-4bf4-a3bf-7df638bd6934.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/779d48dc-8182-4673-aeb7-77144773fd48.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/1e99c520-46f9-4149-b5f7-855be1cdfc2d.jpg",
  "https://images.openlane.eu/carimgs/5875023/general/3c8dfecc-f93e-4d8e-b599-342c1bd6681b.jpg"
];

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, { headers: { 'Referer': 'https://www.openlane.eu/', 'User-Agent': 'Mozilla/5.0' } }, res => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        file.close();
        return download(res.headers.location, dest).then(resolve).catch(reject);
      }
      res.pipe(file);
      file.on('finish', () => { file.close(); resolve(); });
    }).on('error', err => { fs.unlink(dest, () => {}); reject(err); });
  });
}

(async () => {
  for (let i = 0; i < PHOTOS.length; i++) {
    const num = String(i + 1).padStart(2, '0');
    const dest = path.join(TARGET_DIR, `foto_${num}.jpg`);
    process.stdout.write(`Stahuji foto_${num}.jpg ... `);
    await download(PHOTOS[i], dest);
    const size = fs.statSync(dest).size;
    console.log(`OK (${Math.round(size/1024)} kB)`);
  }
  console.log('\nHotovo! Všechny fotky jsou v img/');
})();
