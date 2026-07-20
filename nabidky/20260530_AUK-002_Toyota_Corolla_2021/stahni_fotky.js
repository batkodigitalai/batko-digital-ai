// Spustit: node stahni_fotky.js
const https = require('https');
const fs = require('fs');
const path = require('path');

const DIR = path.join(__dirname, 'img');
if (!fs.existsSync(DIR)) fs.mkdirSync(DIR);

const URLS = [
  "https://images.openlane.eu/carimgs/5767147/general/65436fad-da3d-46e0-b0de-8b4e24e623e7.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/c4ddf0c6-485a-4ae8-be65-8afcff86b5b5.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/f0ff5710-d22f-4a61-bed8-9df2e22469a4.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/4b9cea2c-a117-4bc7-954d-de79621f5073.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/59ca4e9f-9cc9-45a3-b747-45e92ee8f6ce.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/f81e5c72-9dd1-4bb1-be48-61efacb72048.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/e5d01167-30ab-4281-8c99-b8e63c5ce510.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/5e04fe37-b54a-4392-9263-0123109d5bd2.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/16f08a3f-1197-4134-9fd7-2221e7da5fa9.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/df8d5b04-eb13-4496-8aa2-976e58cae613.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/2612ae65-31ed-473e-8570-9635d9d70ee0.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/a6cea010-cc0e-4067-ae5a-242713eaa4fa.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/79c7bae2-ea9e-445a-ad8d-5be308f65dee.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/f472cae5-2d8d-4552-ba2e-97c295a93644.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/fbaf67d3-7706-4232-b653-5052219a4749.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/dc96a5f9-2eae-4f3a-8954-6292278ab881.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/497b077e-e33f-4896-a4d9-f579cec4a2b8.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/1c93ada0-3ef4-4b40-bade-cff45d90a7bc.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/e561838f-e344-4206-8636-a5a435746085.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/ad4b95b4-9be0-458f-9031-c2ca0e92a767.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/a1c94021-9275-4a61-8e92-0fea7f0629dd.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/026c8d54-7969-452e-892d-53643fdb9635.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/c3d3dd47-7609-4b1d-a524-42dc35a280ac.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/0b9d6f69-18b0-4559-9be3-3344e1144678.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/a9f1b6d7-2615-4b38-b839-8dd80cf0eb1a.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/d80fc22f-ea34-43e8-8ffe-4f72b834330a.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/f0fabb38-f9c4-4231-9761-876d0302d0d6.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/664ca3f4-8d29-4f19-8f5c-b4f4f038409e.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/7a443bab-b224-41e6-acd3-e084c1da40b7.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/09d91b29-6825-4fcd-affb-4a02fda51b5d.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/50b24c72-8f20-4aff-a005-5731c2cc5fec.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/95b25b0e-7c5e-4d18-be5b-79ba3d943354.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/299f1e2c-4f1f-4897-9b00-6d7ac89d0ef4.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/72bb86b0-fcd7-4f9a-9048-70d6394526a4.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/af12ed61-129b-4084-95d0-e84900a8e4a4.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/673c3e55-2935-4760-817a-8ce23511114d.JPG",
  "https://images.openlane.eu/carimgs/5767147/general/93e1651a-9d88-4764-a362-31cb96d2cf84.JPG"
];

function download(url, dest) {
  return new Promise((resolve, reject) => {
    if (fs.existsSync(dest)) { console.log(`SKIP (existuje): ${path.basename(dest)}`); return resolve(); }
    const file = fs.createWriteStream(dest);
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, res => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        file.close(); fs.unlinkSync(dest);
        return download(res.headers.location, dest).then(resolve).catch(reject);
      }
      res.pipe(file);
      file.on('finish', () => { file.close(); console.log(`OK: ${path.basename(dest)}`); resolve(); });
    }).on('error', err => { fs.unlink(dest, () => {}); reject(err); });
  });
}

(async () => {
  for (let i = 0; i < URLS.length; i++) {
    const fname = `foto_${String(i+1).padStart(2,'0')}.jpg`;
    try { await download(URLS[i], path.join(DIR, fname)); }
    catch(e) { console.log(`CHYBA ${fname}: ${e.message}`); }
  }
  console.log('\nHotovo!');
})();
