// Vyrobí grafickou kartu 1080x1350 (4:5) ve stylu Auto pod lupou: tmavě modrá, bílá, oranžový rámeček.
// Použití: node scripts/publikace_karta.js '{"vystup":"cesta.png","nadpis":"...","radky":["..",".."],"zvyrazni":"CENA","pata":"Auto pod lupou | Jaroslav Batko"}'
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const p = JSON.parse(process.argv[2]);
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const radky = (p.radky || []).map(r => {
    const t = esc(r);
    return p.zvyrazni && t.includes(p.zvyrazni)
      ? t.replace(p.zvyrazni, '<span class="z">' + p.zvyrazni + '</span>') : t;
  });
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
  body{margin:0;width:1080px;height:1350px;background:#0b1f3a;color:#fff;font-family:Arial,Helvetica,sans-serif;display:flex;flex-direction:column;justify-content:space-between;padding:80px;box-sizing:border-box}
  .lbl{font-size:34px;letter-spacing:4px;color:#f28c28;font-weight:bold}
  h1{font-size:${p.nadpis.length > 40 ? 76 : 92}px;line-height:1.08;margin:30px 0 0;font-weight:900;text-wrap:balance}
  .r{font-size:50px;line-height:1.35;margin-top:36px;padding-left:34px;border-left:10px solid #f28c28}
  .z{background:#f28c28;color:#0b1f3a;padding:2px 16px;border-radius:10px;font-weight:bold;white-space:nowrap}
  .pata{font-size:34px;color:#9fb3cc;display:flex;justify-content:space-between;border-top:3px solid #1e3a5f;padding-top:28px}
  </style></head><body>
  <div><div class="lbl">${esc(p.stitek || 'AUTO POD LUPOU')}</div><h1>${esc(p.nadpis)}</h1>
  ${radky.map(r => '<div class="r">' + r + '</div>').join('')}</div>
  <div class="pata"><span>${esc(p.pata || 'Ing. Jaroslav Batko')}</span><span>${esc(p.datum || '')}</span></div>
  </body></html>`;
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await pg.setContent(html);
  await pg.screenshot({ path: p.vystup, type: p.vystup.endsWith('.jpg') ? 'jpeg' : 'png', quality: p.vystup.endsWith('.jpg') ? 88 : undefined });
  await b.close();
  console.log('OK', p.vystup, fs.statSync(p.vystup).size);
})();
