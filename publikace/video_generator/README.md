# Generátor videí Auto pod lupou

Postup: HTML animace (slova naskakují, *klíčové slovo* v oranžovém rámečku) → snímky Playwright (30 fps) → ffmpeg MP4 + klidná syntetická hudba s jemnými zvonky na klíčová slova a změny scén. Bez mluveného hlasu.

## Použití (příště se mění jen texty)
1. Zkopírovat `ukazka_spec.json`, upravit `name`, `scenes` (klíčové slovo mezi hvězdičkami), `cta`; `watermark` nechat prázdné u ostrých videí.
2. `node scripts/publikace_video.js spec.json --out publikace/RRRRMMDD` (volitelně `--only 169` nebo `--only 916`)
3. Výstup: `<name>_169.mp4` (1920×1080, Facebook/LinkedIn) a `<name>_916.mp4` (1080×1920, Instagram Reel), plus hudba a timeline.
4. URL videí zapsat do VYSTUPY sloupce S a T.

Hudba: `scripts/publikace_hudba.py timeline.json out.wav [LUFS]` (výchozí −30, výsledné video ≈ −27 LUFS). Vyžaduje node + playwright, ffmpeg, python numpy/scipy.
Pravidla: veřejně jen „evropská aukce“, částky v Kč i €, odhady označit, videa se publikují až po schválení.
