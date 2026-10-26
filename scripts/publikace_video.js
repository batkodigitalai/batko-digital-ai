#!/usr/bin/env node
/**
 * Generátor videí Auto pod lupou (HTML animace -> snímky Playwright -> ffmpeg -> MP4 + hudba).
 * Použití: node scripts/publikace_video.js <spec.json> [--out publikace/RRRRMMDD] [--only 169|916] [--fps 30]
 * spec.json: { "name":"ukazka", "watermark":"UKÁZKA"|"", "scenes":["text s *klíčovým slovem*", ...],
 *              "cta":["řádek1","řádek2"], "brand":"Auto pod lupou" }
 * Mění se jen texty ve spec.json; vzhled, časování a hudba zůstávají stejné.
 */
const fs = require('fs'), path = require('path'), { execFileSync, spawnSync } = require('child_process');
const { chromium } = require('playwright');
const args = process.argv.slice(2);
const specFile = args[0];
if (!specFile) { console.error('Chybí spec.json'); process.exit(1); }
const opt = (k, d) => { const i = args.indexOf(k); return i > 0 ? args[i + 1] : d; };
const outDir = path.resolve(opt('--out', 'publikace/video_out'));
const only = opt('--only', ''); const FPS = +opt('--fps', 30);
const spec = JSON.parse(fs.readFileSync(specFile, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });

// ---- časová osa (stejná pro obě poměry stran, hudba se váže na ni) ----
const WORD = 0.32, HOLD = 1.3, FADE = 0.5, CTA_HOLD = 4.5, INTRO = 0.6;
const parse = s => s.split(/\s+/).filter(Boolean).map(w => { const k = /^\*.*\*[.,!?:;…]*$/.test(w) || /^\*/.test(w) && /\*[.,!?:;…]*$/.test(w); return { t: w.replace(/\*/g, ''), key: k }; });
// klíčová slova z více slov: *dvě slova* -> sloučit
function parseScene(s) {
  const out = []; const re = /\*([^*]+)\*([.,!?:;…]*)|(\S+)/g; let m;
  while ((m = re.exec(s))) {
    if (m[1] !== undefined) out.push({ t: m[1] + (m[2] || ''), key: true });
    else out.push({ t: m[3], key: false });
  }
  return out;
}
let t = INTRO; const scenes = [];
spec.scenes.forEach(s => {
  const words = parseScene(s); const start = t;
  words.forEach((w, i) => { w.at = start + i * WORD; });
  const end = start + words.length * WORD + HOLD;
  scenes.push({ start, end, words, kind: 'text' }); t = end + FADE * 0.5;
});
const ctaStart = t; scenes.push({ start: ctaStart, end: ctaStart + CTA_HOLD, lines: spec.cta || [], kind: 'cta' });
const DURATION = ctaStart + CTA_HOLD + 1.0;
const timeline = { duration: DURATION, fade: FADE, scenes: scenes.map(s => ({ kind: s.kind, start: s.start, end: s.end, keys: (s.words || []).filter(w => w.key).map(w => w.at) })) };
const tlFile = path.join(outDir, (spec.name || 'video') + '_timeline.json');
fs.writeFileSync(tlFile, JSON.stringify(timeline));

const html = (W, H) => `<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}html,body{margin:0;background:#0b1f3a;overflow:hidden}
#c{position:relative;width:${W}px;height:${H}px;overflow:hidden;font-family:Arial,Helvetica,sans-serif;color:#fff;background:radial-gradient(120% 90% at 30% 20%,#17386a 0%,#0b1f3a 60%,#08172c 100%)}
#glow{position:absolute;width:${W * 0.9}px;height:${W * 0.9}px;border-radius:50%;background:radial-gradient(circle,rgba(242,140,40,.13),transparent 65%)}
#brand{position:absolute;left:0;right:0;top:${H > W ? 150 : 40}px;text-align:center;font-size:${H > W ? 38 : 30}px;letter-spacing:6px;color:#f28c28;font-weight:bold}
#wm{position:absolute;left:0;right:0;bottom:${H > W ? 260 : 36}px;text-align:center;font-size:${H > W ? 34 : 26}px;letter-spacing:8px;color:rgba(255,255,255,.35)}
#bar{position:absolute;left:0;bottom:0;height:6px;background:#f28c28}
.sc{position:absolute;left:${H > W ? 70 : 160}px;right:${H > W ? 70 : 160}px;top:${H > W ? 330 : 120}px;bottom:${H > W ? 400 : 120}px;display:flex;flex-wrap:wrap;align-content:center;justify-content:center;text-align:center;gap:${H > W ? 18 : 12}px ${H > W ? 22 : 18}px;opacity:0}
.w{font-size:${H > W ? 92 : 84}px;font-weight:bold;line-height:1.15;opacity:0;display:inline-block;padding:4px 14px;border:6px solid transparent;border-radius:14px}
.w.k{color:#fff}
.cta{font-size:${H > W ? 70 : 64}px;font-weight:bold;line-height:1.3;width:100%}
.cta.s{font-size:${H > W ? 52 : 46}px;color:#f28c28;font-weight:bold}
</style></head><body><div id="c"><div id="glow"></div><div id="brand">${(spec.brand || 'AUTO POD LUPOU').toUpperCase()}</div>
<div id="stage"></div><div id="wm">${spec.watermark || ''}</div><div id="bar"></div></div>
<script>
const TL=${JSON.stringify(timeline)};const S=${JSON.stringify(scenes)};const FADE=${FADE};const W=${W},H=${H};
const stage=document.getElementById('stage');
S.forEach((s,i)=>{const d=document.createElement('div');d.className='sc';d.id='s'+i;
 if(s.kind==='text'){s.words.forEach((w,j)=>{const e=document.createElement('span');e.className='w'+(w.key?' k':'');e.id='w'+i+'_'+j;e.textContent=w.t;d.appendChild(e)})}
 else{s.lines.forEach((l,j)=>{const e=document.createElement('div');e.className='cta'+(j>=s.lines.length-2&&s.lines.length>2?' s':'');e.textContent=l;d.appendChild(e)})}
 stage.appendChild(d)});
const ease=x=>1-Math.pow(1-x,3), back=x=>{const c=1.7;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
window.render=function(t){
 document.getElementById('glow').style.transform='translate('+(W*0.05+Math.sin(t*0.25)*W*0.06)+'px,'+(H*0.1+Math.cos(t*0.2)*H*0.04)+'px)';
 document.getElementById('bar').style.width=(100*Math.min(1,t/TL.duration))+'%';
 S.forEach((s,i)=>{const d=document.getElementById('s'+i);
  const a=Math.max(0,Math.min(1,(t-(s.start-FADE*0.5))/(FADE*0.5)));
  const b=1-Math.max(0,Math.min(1,(t-s.end)/(FADE*0.5)));
  const op=(i===S.length-1)?Math.min(a,1):Math.min(a,b); d.style.opacity=op;
  if(s.kind==='text'){s.words.forEach((w,j)=>{const e=document.getElementById('w'+i+'_'+j);
    const p=Math.max(0,Math.min(1,(t-w.at)/0.28)); const sc=0.6+0.4*back(p);
    e.style.opacity=ease(p); e.style.transform='scale('+sc+') translateY('+(1-ease(p))*18+'px)';
    if(w.key){const q=Math.max(0,Math.min(1,(t-w.at-0.1)/0.35)); e.style.borderColor='rgba(242,140,40,'+ease(q)+')'; e.style.color=q>0.5?'#ffb15c':'#fff'; e.style.background='rgba(242,140,40,'+(0.12*ease(q))+')'}
  })} else {const kids=d.children;for(let j=0;j<kids.length;j++){const q=Math.max(0,Math.min(1,(t-s.start-j*0.35)/0.4));kids[j].style.opacity=ease(q);kids[j].style.transform='translateY('+(1-ease(q))*20+'px)'}}
 });
};
window.render(0);
</script></body></html>`;

async function renderOne(label, W, H) {
  const base = path.join(outDir, `${spec.name}_${label}`);
  const frames = path.join(outDir, `_frames_${label}`);
  fs.rmSync(frames, { recursive: true, force: true }); fs.mkdirSync(frames, { recursive: true });
  const N = Math.ceil(DURATION * FPS), PAR = 4;
  const browser = await chromium.launch();
  const htmlFile = path.join(frames, 'v.html'); fs.writeFileSync(htmlFile, html(W, H));
  await Promise.all([...Array(PAR).keys()].map(async k => {
    const page = await browser.newPage({ viewport: { width: W, height: H } });
    await page.goto('file://' + htmlFile);
    for (let f = k; f < N; f += PAR) {
      await page.evaluate(tt => window.render(tt), f / FPS);
      await page.screenshot({ path: path.join(frames, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 92 });
    }
  }));
  await browser.close();
  const wav = path.join(outDir, `${spec.name}_hudba.wav`);
  if (!fs.existsSync(wav)) execFileSync('python3', [path.join(__dirname, 'publikace_hudba.py'), tlFile, wav], { stdio: 'inherit' });
  const mp4 = base + '.mp4';
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(FPS), '-i', path.join(frames, 'f%05d.jpg'), '-i', wav,
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-ar', '48000', '-b:a', '192k',
    '-shortest', '-movflags', '+faststart', mp4], { stdio: 'inherit' });
  fs.rmSync(frames, { recursive: true, force: true });
  console.log('OK', mp4);
}
(async () => {
  if (only !== '916') await renderOne('169', 1920, 1080);
  if (only !== '169') await renderOne('916', 1080, 1920);
})();
