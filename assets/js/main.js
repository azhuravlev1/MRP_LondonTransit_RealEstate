import * as pdfjsLib from '../../pdfjs/build/pdf.mjs';

pdfjsLib.GlobalWorkerOptions.workerSrc = new URL('../../pdfjs/build/pdf.worker.mjs', import.meta.url).href;

const PDF_URL = new URL('../../paper/MRP_Report_Andrey_Zhuravlev.pdf', import.meta.url).href;
const VIEWER_URL = new URL('../../pdfjs/web/viewer.html', import.meta.url).href +
  '?file=' + encodeURIComponent(PDF_URL) + '#zoom=page-width&pagemode=none';

const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const DURATION = reduceMotion ? 1 : 680;
const EASE = 'cubic-bezier(0.22, 1, 0.36, 1)';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Configure the embedded PDF.js viewer before it starts: a reader, not an editor.
document.addEventListener('webviewerloaded', (e) => {
  try {
    const opts = e.detail.source.PDFViewerApplicationOptions;
    opts.set('disablePreferences', true);
    opts.set('annotationEditorMode', -1);
    opts.set('sidebarViewOnLoad', 0);
  } catch (err) { /* keep defaults */ }
});

/* ============================================================
   Small scrollable preview of the paper (PDF.js canvases)
   ============================================================ */
const preview = document.getElementById('paperPreview');
const pageBadge = document.getElementById('previewPage');
let pdfDoc = null;
let pageEls = [];
let currentPage = 1;

async function initPreview() {
  try {
    pdfDoc = await pdfjsLib.getDocument({ url: PDF_URL }).promise;
  } catch (err) {
    preview.innerHTML = '<div class="preview-loading">Preview unavailable. Use the buttons to open or download the paper.</div>';
    return;
  }
  const first = await pdfDoc.getPage(1);
  const vp = first.getViewport({ scale: 1 });
  preview.innerHTML = '';
  for (let i = 1; i <= pdfDoc.numPages; i++) {
    const el = document.createElement('div');
    el.className = 'pdf-page';
    el.dataset.page = String(i);
    el.style.aspectRatio = `${vp.width} / ${vp.height}`;
    preview.appendChild(el);
    pageEls.push(el);
  }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) renderPage(e.target); });
  }, { root: preview, rootMargin: '500px 0px' });
  pageEls.forEach((el) => io.observe(el));
  preview.addEventListener('scroll', () => { updateBadge(); scheduleHiRes(); }, { passive: true });
  updateBadge();
  scheduleHiRes();
  const meta = document.getElementById('paperMeta');
  if (meta) meta.textContent = `PDF · ${pdfDoc.numPages} pages · 1.9 MB`;
}

function renderPage(el) {
  if (!pdfDoc) return Promise.resolve();
  if (el._rendering) return el._rendering;
  el._rendering = (async () => {
    const page = await pdfDoc.getPage(Number(el.dataset.page));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const base = page.getViewport({ scale: 1 });
    const scale = (el.clientWidth * dpr * 1.25) / base.width;
    const viewport = page.getViewport({ scale });
    const canvas = document.createElement('canvas');
    canvas.width = Math.floor(viewport.width);
    canvas.height = Math.floor(viewport.height);
    await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
    el.appendChild(canvas);
  })();
  return el._rendering;
}

function updateBadge() {
  if (!pageEls.length) return;
  const probe = preview.scrollTop + preview.clientHeight * 0.35;
  let p = 1;
  for (const el of pageEls) { if (el.offsetTop <= probe) p = Number(el.dataset.page); else break; }
  currentPage = p;
  pageBadge.textContent = `${p} / ${pageEls.length}`;
}

/* Draw what is currently visible in the preview into one image,
   so the reader can start its animation from exactly that picture. */
function snapshotPreview() {
  const w = preview.clientWidth;
  const h = preview.clientHeight;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const c = document.createElement('canvas');
  c.width = Math.round(w * dpr);
  c.height = Math.round(h * dpr);
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#DDE1EE';
  ctx.fillRect(0, 0, c.width, c.height);
  const st = preview.scrollTop;
  for (const el of pageEls) {
    const top = el.offsetTop - st;
    if (top > h || top + el.offsetHeight < 0) continue;
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, top * dpr, el.offsetWidth * dpr, el.offsetHeight * dpr);
    const cv = el.querySelector('canvas');
    if (cv) ctx.drawImage(cv, 0, top * dpr, el.offsetWidth * dpr, el.offsetHeight * dpr);
  }
  return c.toDataURL('image/jpeg', 0.9);
}

/* A sharp version of the same picture, rendered at the reader's
   width, so the expanding panel never looks blurry. Built in the
   background whenever the preview stops scrolling. */
const hiPages = new Map();
let hiCache = null;
let hiTimer = null;

function scheduleHiRes() {
  clearTimeout(hiTimer);
  hiTimer = setTimeout(() => { buildHiResSnapshot().catch(() => {}); }, 260);
}

async function hiResPage(n, widthPx) {
  const key = `${n}@${Math.round(widthPx)}`;
  if (hiPages.has(key)) return hiPages.get(key);
  const page = await pdfDoc.getPage(n);
  const base = page.getViewport({ scale: 1 });
  const viewport = page.getViewport({ scale: widthPx / base.width });
  const canvas = document.createElement('canvas');
  canvas.width = Math.floor(viewport.width);
  canvas.height = Math.floor(viewport.height);
  await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
  hiPages.set(key, canvas);
  if (hiPages.size > 6) hiPages.delete(hiPages.keys().next().value);
  return canvas;
}

async function buildHiResSnapshot() {
  if (!pdfDoc || !pageEls.length) return null;
  const st = preview.scrollTop;
  const w = preview.clientWidth;
  const h = preview.clientHeight;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const panelW = isOpen ? panel.getBoundingClientRect().width : panel.offsetWidth;
  const K = Math.max(1, (panelW * dpr) / w);
  const c = document.createElement('canvas');
  c.width = Math.round(w * K);
  c.height = Math.round(h * K);
  const ctx = c.getContext('2d');
  ctx.fillStyle = '#DDE1EE';
  ctx.fillRect(0, 0, c.width, c.height);
  for (const el of pageEls) {
    const top = el.offsetTop - st;
    if (top > h || top + el.offsetHeight < 0) continue;
    const pc = await hiResPage(Number(el.dataset.page), el.offsetWidth * K);
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, top * K, el.offsetWidth * K, el.offsetHeight * K);
    ctx.drawImage(pc, 0, top * K, el.offsetWidth * K, el.offsetHeight * K);
  }
  if (preview.scrollTop !== st) return null;
  hiCache = { st, w, url: c.toDataURL('image/jpeg', 0.9) };
  return hiCache.url;
}

async function bestSnapshot() {
  if (hiCache && hiCache.st === preview.scrollTop && hiCache.w === preview.clientWidth) return hiCache.url;
  try {
    const url = await Promise.race([buildHiResSnapshot(), sleep(450).then(() => null)]);
    if (url) return url;
  } catch (e) { /* fall back below */ }
  return snapshotPreview();
}

/* ============================================================
   Full reader: PDF.js viewer in an overlay that grows out of
   the small preview (FLIP animation with transform + clip-path)
   ============================================================ */
const reader = document.getElementById('reader');
const panel = document.getElementById('readerPanel');
const frame = document.getElementById('readerFrame');
const cover = document.getElementById('readerCover');
let frameReady = null;
let isOpen = false;
let busy = false;

function viewerApp() {
  try { return frame.contentWindow && frame.contentWindow.PDFViewerApplication; } catch (e) { return null; }
}

function ensureFrame() {
  if (frameReady) return frameReady;
  frameReady = new Promise((resolve) => {
    frame.addEventListener('load', async () => {
      const app = viewerApp();
      if (!app) return resolve();
      try {
        await app.initializedPromise;
        frame.contentWindow.addEventListener('keydown', (e) => {
          if (e.key === 'Escape' && !(app.findBar && app.findBar.opened)) { e.preventDefault(); closeReader(); }
        });
        if (app.pdfViewer && app.pdfViewer.pagesCount) resolve();
        else app.eventBus.on('pagesinit', () => resolve(), { once: true });
      } catch (e) { resolve(); }
    }, { once: true });
    frame.src = VIEWER_URL;
  });
  return frameReady;
}

function goToPage(n) {
  const app = viewerApp();
  if (app && app.pdfViewer && app.pdfViewer.pagesCount) {
    try { app.page = n; } catch (e) { /* ignore */ }
  }
}

function collapsedState() {
  const from = preview.getBoundingClientRect();
  const to = panel.getBoundingClientRect();
  const s = from.width / to.width;
  const visibleH = from.height / s;
  const clipBottom = Math.max(0, to.height - visibleH);
  return {
    transform: `translate(${from.left - to.left}px, ${from.top - to.top}px) scale(${s})`,
    clip: `inset(0px 0px ${clipBottom}px 0px round ${10 / s}px)`,
  };
}

function waitForTransition(el, ms) {
  return new Promise((resolve) => {
    let done = false;
    const finish = () => { if (!done) { done = true; el.removeEventListener('transitionend', onEnd); resolve(); } };
    const onEnd = (e) => { if (e.target === el && e.propertyName === 'transform') finish(); };
    el.addEventListener('transitionend', onEnd);
    setTimeout(finish, ms + 80);
  });
}

function lockScroll(lock) {
  if (lock) {
    const sb = window.innerWidth - document.documentElement.clientWidth;
    document.body.style.paddingRight = sb > 0 ? `${sb}px` : '';
    document.body.classList.add('reader-open');
  } else {
    document.body.classList.remove('reader-open');
    document.body.style.paddingRight = '';
  }
}

async function openReader() {
  if (isOpen || busy) return;
  busy = true;
  const ready = ensureFrame();

  // keep the preview in view so the animation starts from a visible spot
  const pr = preview.getBoundingClientRect();
  if (pr.top < 60 || pr.bottom > window.innerHeight) {
    preview.scrollIntoView({ block: 'center', behavior: reduceMotion ? 'auto' : 'smooth' });
    await sleep(reduceMotion ? 0 : 450);
  }

  cover.src = await bestSnapshot();
  try { await cover.decode(); } catch (e) { /* ignore */ }

  lockScroll(true);
  panel.style.transition = 'none';
  panel.style.transform = 'none';
  panel.style.clipPath = 'none';
  const start = collapsedState();
  panel.style.transform = start.transform;
  panel.style.clipPath = start.clip;
  cover.style.transition = 'none';
  cover.style.opacity = '1';
  frame.style.transition = 'none';
  frame.style.opacity = '0';

  reader.classList.add('open', 'animating');
  reader.setAttribute('aria-hidden', 'false');
  panel.getBoundingClientRect(); // commit the start state

  requestAnimationFrame(() => {
    panel.style.transition = `transform ${DURATION}ms ${EASE}, clip-path ${DURATION}ms ${EASE}`;
    panel.style.transform = 'none';
    panel.style.clipPath = 'inset(0px 0px 0px 0px round 16px)';
  });
  await waitForTransition(panel, DURATION);
  reader.classList.remove('animating');

  await Promise.race([ready, sleep(6000)]);
  goToPage(currentPage);
  await sleep(120);
  frame.style.transition = 'opacity 0.35s ease';
  cover.style.transition = 'opacity 0.35s ease';
  frame.style.opacity = '1';
  cover.style.opacity = '0';
  frame.focus();
  isOpen = true;
  busy = false;
}

async function closeReader() {
  if (!isOpen || busy) return;
  busy = true;

  const app = viewerApp();
  const page = (app && app.page) || currentPage;
  const el = pageEls[page - 1];
  if (el) {
    preview.style.scrollBehavior = 'auto';
    preview.scrollTop = el.offsetTop;
    preview.style.scrollBehavior = '';
    await Promise.all([renderPage(el), pageEls[page] ? renderPage(pageEls[page]) : null]);
    updateBadge();
  }
  cover.src = await bestSnapshot();
  try { await cover.decode(); } catch (e) { /* ignore */ }

  cover.style.transition = 'opacity 0.22s ease';
  frame.style.transition = 'opacity 0.22s ease';
  cover.style.opacity = '1';
  frame.style.opacity = '0';
  await sleep(reduceMotion ? 0 : 220);

  reader.classList.add('animating', 'closing');
  const end = collapsedState();
  panel.style.transition = `transform ${DURATION}ms ${EASE}, clip-path ${DURATION}ms ${EASE}`;
  panel.style.transform = end.transform;
  panel.style.clipPath = end.clip;
  await waitForTransition(panel, DURATION);

  reader.classList.remove('open', 'animating', 'closing');
  reader.setAttribute('aria-hidden', 'true');
  panel.style.transition = 'none';
  panel.style.transform = 'none';
  panel.style.clipPath = 'none';
  cover.style.opacity = '0';
  lockScroll(false);
  preview.focus({ preventScroll: true });
  isOpen = false;
  busy = false;
}

document.getElementById('openReader').addEventListener('click', openReader);
document.querySelectorAll('[data-open-reader]').forEach((b) => b.addEventListener('click', openReader));
preview.addEventListener('click', openReader);
preview.addEventListener('keydown', (e) => { if (e.key === 'Enter') openReader(); });
document.querySelectorAll('[data-close-reader]').forEach((b) => b.addEventListener('click', closeReader));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && isOpen) closeReader(); });

// Load the viewer quietly in the background so "Open in reader" is instant.
window.addEventListener('load', () => {
  const idle = window.requestIdleCallback || ((fn) => setTimeout(fn, 1500));
  idle(() => ensureFrame());
});

/* ============================================================
   Figure 3: data coverage as a tube-style line diagram
   ============================================================ */
function buildTimeline() {
  const host = document.getElementById('timeline');
  if (!host) return;
  const W = 760, H = 230, x0 = 150, x1 = 740, y0 = 1995, y1 = 2024;
  const x = (yr) => x0 + ((yr - y0) / (y1 - y0)) * (x1 - x0);
  const rows = [
    { name: 'House prices', sub: 'UK HPI', y: 52, c: '#EE7C0E', from: 1995, to: 2024 },
    { name: 'RODS', sub: 'survey', y: 112, c: '#DC241F', from: 2000, to: 2017 },
    { name: 'NUMBAT', sub: 'smartcard model', y: 172, c: '#6950A1', from: 2017, to: 2023 },
  ];
  const portal = [2019, 2022];
  const foi = [2017, 2018, 2020, 2021, 2023];
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
  s += `<rect x="${x(2000)}" y="18" width="${x(2023) - x(2000)}" height="176" rx="10" fill="#EAF0FF"/>`;
  s += `<text x="${x(2000) + 8}" y="34" font-size="12" fill="#3B4573" font-weight="600">Analysis window 2000–2023</text>`;
  rows.forEach((r) => {
    s += `<text x="8" y="${r.y + 4}" font-size="14" font-weight="700" fill="#0F1A4A">${r.name}</text>`;
    s += `<text x="8" y="${r.y + 20}" font-size="11" fill="#3B4573">${r.sub}</text>`;
    s += `<line x1="${x(r.from)}" y1="${r.y}" x2="${x(r.to)}" y2="${r.y}" stroke="${r.c}" stroke-width="10" stroke-linecap="round"/>`;
  });
  // RODS stations: one tick per year
  for (let yr = 2000; yr <= 2016; yr++) s += `<rect x="${x(yr) - 2.5}" y="98" width="5" height="10" fill="#DC241F"/>`;
  // HPI ticks every 5 years
  for (let yr = 1995; yr <= 2020; yr += 5) s += `<rect x="${x(yr) - 2.5}" y="38" width="5" height="10" fill="#EE7C0E"/>`;
  // interchange RODS / NUMBAT in 2017
  s += `<rect x="${x(2017) - 11}" y="101" width="22" height="82" rx="11" fill="#fff" stroke="#0F1A4A" stroke-width="4"/>`;
  // NUMBAT stations
  portal.forEach((yr) => { s += `<circle cx="${x(yr)}" cy="172" r="9" fill="#6950A1" stroke="#fff" stroke-width="3"/>`; });
  foi.filter((yr) => yr !== 2017).forEach((yr) => { s += `<circle cx="${x(yr)}" cy="172" r="9" fill="#fff" stroke="#6950A1" stroke-width="4"/>`; });
  s += `<text x="${x(2020)}" y="${172 - 18}" font-size="11.5" text-anchor="middle" fill="#6950A1" font-weight="700">FOI request</text>`;
  // axis
  [1995, 2000, 2005, 2010, 2015, 2020, 2023].forEach((yr) => {
    s += `<text x="${x(yr)}" y="218" font-size="12" text-anchor="middle" fill="#3B4573">${yr}</text>`;
  });
  s += '</svg>';
  host.innerHTML = s;
}

/* ============================================================
   Figure 4: borough names matched between the two sources
   (redrawn from Figure 2 of the paper)
   ============================================================ */
function buildVenn() {
  const host = document.getElementById('venn');
  if (!host) return;
  const s = `<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg">
    <circle cx="300" cy="150" r="118" fill="#EE7C0E" fill-opacity="0.22" stroke="#EE7C0E" stroke-width="5"/>
    <circle cx="460" cy="150" r="118" fill="#6950A1" fill-opacity="0.22" stroke="#6950A1" stroke-width="5"/>
    <text x="236" y="162" font-size="44" font-weight="700" text-anchor="middle" fill="#B35A06">3</text>
    <text x="380" y="164" font-size="58" font-weight="700" text-anchor="middle" fill="#0F1A4A">30</text>
    <text x="526" y="162" font-size="44" font-weight="700" text-anchor="middle" fill="#4B3580">9</text>
    <text x="380" y="192" font-size="14" text-anchor="middle" fill="#3B4573">boroughs in both</text>
    <text x="170" y="292" font-size="15" font-weight="700" text-anchor="middle" fill="#0F1A4A">House price index</text>
    <text x="590" y="292" font-size="15" font-weight="700" text-anchor="middle" fill="#0F1A4A">Station data, all systems</text>
  </svg>`;
  host.innerHTML = s;
}

/* ============================================================
   Figure 9: regression estimates with 95% confidence intervals
   (coefficients and standard errors from Table 4 of the paper)
   ============================================================ */
function buildForest() {
  const host = document.getElementById('forest');
  if (!host) return;
  const data = [
    { name: 'Passenger arrivals', coef: 1.28, se: 0.3, p: 'p < 0.001', c: '#00782A' },
    { name: 'Betweenness', coef: -0.69, se: 0.4, p: 'p = 0.052', c: '#EE7C0E' },
    { name: 'Closeness', coef: 0.22, se: 0.2, p: 'p = 0.354', c: '#A0A5A9' },
    { name: 'Eigenvector', coef: -0.67, se: 1.4, p: 'p = 0.632', c: '#A0A5A9' },
  ];
  const W = 760, rowH = 54, top = 20, H = top + data.length * rowH + 44;
  const lo = -3.6, hi = 2.4, px0 = 190, px1 = 610;
  const x = (v) => px0 + ((v - lo) / (hi - lo)) * (px1 - px0);
  let s = `<svg viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">`;
  for (let t = -3; t <= 2; t++) {
    s += `<line x1="${x(t)}" y1="${top - 6}" x2="${x(t)}" y2="${top + data.length * rowH}" stroke="${t === 0 ? '#0F1A4A' : '#E3E6F0'}" stroke-width="${t === 0 ? 2 : 1}" ${t === 0 ? 'stroke-dasharray="5 5"' : ''}/>`;
    s += `<text x="${x(t)}" y="${top + data.length * rowH + 20}" font-size="12" text-anchor="middle" fill="#3B4573">${t > 0 ? '+' : ''}${t}%</text>`;
  }
  s += `<text x="${(px0 + px1) / 2}" y="${H - 4}" font-size="12" text-anchor="middle" fill="#3B4573">Change in house prices per 1 SD increase in the score (previous year)</text>`;
  data.forEach((d, i) => {
    const y = top + i * rowH + rowH / 2;
    const a = Math.max(lo, d.coef - 1.96 * d.se);
    const b = Math.min(hi, d.coef + 1.96 * d.se);
    s += `<text x="10" y="${y + 5}" font-size="15" font-weight="600" fill="#0F1A4A">${d.name}</text>`;
    s += `<line class="ci" x1="${x(a)}" y1="${y}" x2="${x(b)}" y2="${y}" stroke="${d.c}" stroke-width="8" stroke-linecap="round" style="--len:${x(b) - x(a)}"/>`;
    s += `<circle cx="${x(d.coef)}" cy="${y}" r="10" fill="#fff" stroke="#0F1A4A" stroke-width="4"/>`;
    s += `<text x="${px1 + 22}" y="${y - 2}" font-size="15" font-weight="700" fill="#0F1A4A">${d.coef > 0 ? '+' : '−'}${Math.abs(d.coef).toFixed(2)}%</text>`;
    s += `<text x="${px1 + 22}" y="${y + 15}" font-size="12" fill="#3B4573">${d.p}</text>`;
  });
  s += '</svg>';
  host.innerHTML = s;
}

/* ============================================================
   Scroll reveal and counters
   ============================================================ */
function initReveal() {
  const els = document.querySelectorAll('.reveal');
  if (reduceMotion || !('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -10% 0px' });
  els.forEach((e) => io.observe(e));
}

function initCounters() {
  const nums = document.querySelectorAll('.stat-num[data-count]');
  if (reduceMotion) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      const target = Number(e.target.dataset.count);
      const t0 = performance.now();
      const dur = 1200;
      const tick = (t) => {
        const k = Math.min(1, (t - t0) / dur);
        const eased = 1 - Math.pow(1 - k, 3);
        e.target.textContent = Math.round(target * eased).toLocaleString('en-US');
        if (k < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  nums.forEach((n) => io.observe(n));
}

buildTimeline();
buildVenn();
buildForest();
initReveal();
initCounters();
initPreview();
