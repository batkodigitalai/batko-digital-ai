// ══════════════════════════════════════════════════════════════
// STAŽENÍ FOTEK AUK-003 — VW Passat Variant Business 11029593
// Spustit v konzoli prohlížeče (F12) NA stránce detailu auta v OPENLANE
// ══════════════════════════════════════════════════════════════
// INSTRUKCE:
//   1. Otevřít https://www.openlane.eu → detail auta 11029593
//   2. Stisknout F12 → záložka Console
//   3. Vložit celý tento kód a stisknout Enter
//   4. Prohlížeč začne stahovat fotky jako foto_01.jpg, foto_02.jpg …
//   5. Fotky uložit do složky: aukce_system\20260601_AUK-003_VW_Passat_2023_Business\img\
// ══════════════════════════════════════════════════════════════

(async function downloadCarPhotos() {
  // Najdi všechny obrázky v galerii (různé selektory pro různé verze OPENLANE)
  const selectors = [
    'img[src*="cdn"][src*="jpg"]',
    'img[src*="image"][src*="jpg"]',
    '.gallery img',
    '.car-gallery img',
    '.photo-gallery img',
    '[class*="gallery"] img',
    '[class*="carousel"] img',
    '[class*="slider"] img',
    'img[src*="openlane"]',
  ];

  let imgs = [];
  for (const sel of selectors) {
    const found = [...document.querySelectorAll(sel)];
    if (found.length > imgs.length) imgs = found;
  }

  // Deduplikovat podle src a filtrovat malé ikony
  const urls = [...new Set(
    imgs
      .map(img => img.src || img.dataset.src || img.getAttribute('data-lazy-src') || '')
      .filter(src => src && src.startsWith('http') && !src.includes('icon') && !src.includes('logo'))
  )];

  if (urls.length === 0) {
    // Záloha: hledej v srcset nebo background-image
    const allImgs = [...document.querySelectorAll('img')].filter(img => {
      const s = img.src || '';
      return s.includes('jpg') || s.includes('jpeg') || s.includes('webp');
    });
    allImgs.forEach(img => {
      const src = img.src || img.dataset.src || '';
      if (src && !urls.includes(src)) urls.push(src);
    });
  }

  console.log(`Nalezeno ${urls.length} fotek:`, urls);

  if (urls.length === 0) {
    console.error('❌ Žádné fotky nenalezeny. Zkuste ručně: pravý klik na foto → Zkopírovat adresu obrázku.');
    return;
  }

  // Stáhnout postupně s prodlevou
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    const filename = `foto_${String(i + 1).padStart(2, '0')}.jpg`;

    try {
      const blob = await fetch(url, {credentials: 'include'}).then(r => r.blob());
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(a.href);
      console.log(`✅ ${filename} (${i+1}/${urls.length})`);
    } catch (e) {
      console.warn(`⚠️ ${filename} selhalo: ${e.message} — zkuste přímý odkaz: ${url}`);
    }

    // Prodleva 600ms mezi stahováním (prohlížeč nestihne zablokovat)
    await new Promise(r => setTimeout(r, 600));
  }

  console.log(`\n✅ Hotovo! Uložte soubory do:\naukce_system\\20260601_AUK-003_VW_Passat_2023_Business\\img\\`);
})();
