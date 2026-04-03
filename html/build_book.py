"""
THE ARCHITECT'S BLUEPRINT — Build System
─────────────────────────────────────────
Outputs:  book.html   (single-file web book)
          manifest.json (PWA manifest)

Run:  python build_book.py
"""

import json
import re

FILES = [
    'ch01-05.html', 'ch06-10.html', 'ch11-15.html', 'ch16-20.html',
    'ch21-25.html', 'ch26-30.html', 'ch31-36.html', 'appendices.html',
]

def extract_sections(f):
    with open(f, encoding='utf-8') as fh:
        c = fh.read()
    i = c.find('</nav>')
    return c[i + 6:].strip().rsplit('</body>', 1)[0].strip()

combined = '\n\n'.join(extract_sections(f) for f in FILES)

# ── Strip em dashes from chapter content ──────────────────────────────────
# In headings (h1–h4): replace " — " with ": " (subtitle pattern)
combined = re.sub(r'(<h[1-4][^>]*>[^<]*?)\s*\u2014\s*', r'\1: ', combined)
# In all other prose: replace " — " with ", "
combined = combined.replace('\u2014', ',')

# ── PWA manifest ───────────────────────────────────────────────────────────
with open('manifest.json', 'w', encoding='utf-8') as f:
    json.dump({
        "name": "The Architect's Blueprint",
        "short_name": "Blueprint",
        "description": "Systems thinking, AI internals, and production infrastructure for curious minds.",
        "start_url": "./book.html",
        "display": "standalone",
        "background_color": "#0c1a2e",
        "theme_color": "#0071e3",
        "icons": [
            {"src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 192 192'><rect width='192' height='192' rx='20' fill='%230c1a2e'/><text x='96' y='128' font-size='96' text-anchor='middle' fill='white' font-family='system-ui' font-weight='700'>B</text></svg>", "sizes": "192x192", "type": "image/svg+xml"},
        ]
    }, f, indent=2)
print("manifest.json  OK")

# ── HTML ───────────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<!--
  THE ARCHITECT'S BLUEPRINT
  ──────────────────────────────────────────────────────────────────────────
  SHARE THIS BOOK
  ├─ GitHub Pages (free, permanent URL):
  │     1. github.com → New repository → upload book.html + manifest.json
  │     2. Settings → Pages → Source: main / root
  │     3. Share: https://YOUR-NAME.github.io/REPO/book.html
  │
  ├─ GitBook (polished platform, free tier):
  │     1. gitbook.com → New space → Import from GitHub
  │     2. Point to your repo with the SUMMARY.md + chapter folders
  │
  └─ EPUB (native phone reading — Apple Books / Play Books):
        Run: python build_epub.py
        Share the .epub via AirDrop, WhatsApp, or email
  ──────────────────────────────────────────────────────────────────────────
-->
<html lang="en" data-theme="light" data-fontsize="md">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>The Architect's Blueprint</title>
<meta name="description" content="36 chapters on systems thinking, AI internals, and production infrastructure. Written for curious minds.">
<meta property="og:title" content="The Architect's Blueprint">
<meta property="og:description" content="Systems thinking, AI internals, and production infrastructure. For curious minds.">

<!-- PWA -->
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#0c1a2e">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Blueprint">

<!-- Fonts: Inter as web fallback for non-Apple devices.
     On macOS/iOS, -apple-system resolves to SF Pro automatically — no download needed. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ══════════════════════════════════════════════════════════════════════════
   DESIGN TOKENS
   Font note: Apple devices → SF Pro (system). Windows/Android → Inter.
   The stack "-apple-system, BlinkMacSystemFont" = SF Pro on Apple.
══════════════════════════════════════════════════════════════════════════ */
:root {
  --font:      -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', ui-monospace, Menlo, monospace;

  /* Body scale — controlled by data-fontsize */
  --size-body: 16.5px;
  --lh-body:   1.85;

  /* Ink */
  --ink-950:  #09090b;
  --ink-900:  #18181b;
  --ink-800:  #27272a;
  --ink-600:  #52525b;
  --ink-400:  #a1a1aa;
  --ink-200:  #e4e4e7;

  /* Blue */
  --blue:     #0071e3;
  --blue-h:   #0077ed;
  --blue-tint:#e8f2fd;
  --blue-soft:#bfdbfe;

  /* Semantic callout colours */
  --green:       #16a34a;  --green-tint:  #f0fdf4;  --green-soft:  #bbf7d0;
  --amber:       #d97706;  --amber-tint:  #fffbeb;  --amber-soft:  #fde68a;
  --purple:      #7c3aed;  --purple-tint: #faf5ff;  --purple-soft: #ddd6fe;

  /* Surfaces */
  --bg:        #ffffff;
  --bg-2:      #fafafa;
  --bg-3:      #f4f4f5;
  --border:    rgba(0,0,0,0.07);
  --border-md: rgba(0,0,0,0.11);
  --divider:   rgba(0,0,0,0.055);

  /* Code */
  --code-bg:  #18181b;
  --code-fg:  #e4e4e7;

  /* Layout */
  --sidebar:  260px;
  --bar:      50px;
  --bot:      62px;
  --prose:    660px;      /* ≈ 68 chars — optimal reading measure */
  --r:        10px;
  --r-sm:     7px;
  --r-xs:     5px;

  /* Motion */
  --ease:   cubic-bezier(0.4, 0, 0.2, 1);
  --spring: cubic-bezier(0.34, 1.56, 0.64, 1);
  --out:    cubic-bezier(0, 0, 0.2, 1);

  /* Shadows */
  --s1: 0 1px 3px rgba(0,0,0,0.07);
  --s2: 0 2px 8px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04);
  --s3: 0 8px 24px rgba(0,0,0,0.10), 0 2px 6px rgba(0,0,0,0.04);
  --sb: 0 4px 18px rgba(0,113,227,0.28);
}

/* ── Font size presets ──────────────────────────────────────────────────── */
html[data-fontsize="sm"] { --size-body: 14.5px; --lh-body: 1.78; }
html[data-fontsize="md"] { --size-body: 16.5px; --lh-body: 1.85; }
html[data-fontsize="lg"] { --size-body: 19px;   --lh-body: 1.9;  }

/* ── Dark mode ──────────────────────────────────────────────────────────── */
[data-theme="dark"] {
  --ink-950:   #fafafa;
  --ink-900:   #f4f4f5;
  --ink-800:   #d4d4d8;
  --ink-600:   #a1a1aa;
  --ink-400:   #52525b;
  --ink-200:   #27272a;
  --bg:        #09090b;
  --bg-2:      #111113;
  --bg-3:      #18181b;
  --border:    rgba(255,255,255,0.07);
  --border-md: rgba(255,255,255,0.11);
  --divider:   rgba(255,255,255,0.055);
  --blue-tint:   rgba(0,113,227,0.14);
  --blue-soft:   rgba(0,113,227,0.4);
  --green-tint:  rgba(22,163,74,0.12);
  --green-soft:  rgba(22,163,74,0.35);
  --amber-tint:  rgba(217,119,6,0.12);
  --amber-soft:  rgba(217,119,6,0.35);
  --purple-tint: rgba(124,58,237,0.12);
  --purple-soft: rgba(124,58,237,0.35);
}
[data-theme="dark"] #topbar   { background: rgba(9,9,11,0.88); border-bottom-color: rgba(255,255,255,0.08); }
[data-theme="dark"] #sidebar  { background: var(--bg-2); border-right-color: var(--border-md); }
[data-theme="dark"] #bot-bar  { background: rgba(9,9,11,0.92); border-top-color: rgba(255,255,255,0.08); }
[data-theme="dark"] #sheet    { background: var(--bg); }
[data-theme="dark"] #back-to-top { background: rgba(24,24,27,0.92); color: var(--ink-900); }
[data-theme="dark"] .takeaway { background: linear-gradient(135deg, rgba(0,113,227,0.1), rgba(124,58,237,0.1)); }
[data-theme="dark"] :not(pre) > code { color: #60a5fa; }

/* ══════════════════════════════════════════════════════════════════════════
   RESET & BASE
══════════════════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: var(--font);
  font-size: var(--size-body);
  line-height: var(--lh-body);
  color: var(--ink-900);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  -webkit-text-size-adjust: 100%;
  transition: background 200ms var(--ease), color 200ms var(--ease);
}

/* ══════════════════════════════════════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════════════════════════════════════ */
#progress-bar {
  position: fixed; top: 0; left: 0;
  height: 2px; width: 0%;
  background: linear-gradient(90deg, #0071e3, #6366f1, #a855f7);
  z-index: 9999; border-radius: 0 2px 2px 0;
  transition: width 60ms linear;
}

/* ══════════════════════════════════════════════════════════════════════════
   TOP BAR
══════════════════════════════════════════════════════════════════════════ */
#topbar {
  position: fixed; top: 0; left: 0; right: 0;
  height: var(--bar);
  background: rgba(255,255,255,0.86);
  -webkit-backdrop-filter: saturate(200%) blur(20px);
  backdrop-filter: saturate(200%) blur(20px);
  border-bottom: 0.5px solid rgba(0,0,0,0.1);
  display: flex; align-items: center;
  padding: 0 0.75rem; gap: 0.4rem; z-index: 500;
  transition: background 200ms var(--ease);
}
.tb-title  { font-size: 13px; font-weight: 600; letter-spacing: -0.015em; color: var(--ink-900); flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.tb-crumb  { font-size: 11.5px; color: var(--ink-600); display: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 180px; }
@media (min-width: 680px) { .tb-crumb { display: block; } }

.tb-btn {
  flex-shrink: 0; width: 30px; height: 30px;
  border: none; border-radius: var(--r-xs);
  background: transparent; color: var(--ink-800);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: background 100ms var(--ease), transform 120ms var(--ease), color 150ms;
  font-family: var(--font);
}
.tb-btn:hover  { background: var(--bg-3); }
.tb-btn:active { transform: scale(0.9); }
.tb-font       { font-size: 11.5px; font-weight: 600; padding: 0 0.3rem; width: auto; letter-spacing: -0.01em; }
.tb-divider    { width: 0.5px; height: 16px; background: var(--border-md); flex-shrink: 0; margin: 0 0.1rem; }

/* Share popover */
#share-wrap { position: relative; }
#share-pop {
  position: absolute; top: calc(100% + 8px); right: 0;
  background: var(--bg); border: 1px solid var(--border-md);
  border-radius: var(--r); box-shadow: var(--s3);
  padding: 0.85rem 1rem; width: 235px; z-index: 700;
  opacity: 0; pointer-events: none;
  transform: translateY(-5px);
  transition: opacity 160ms var(--ease), transform 160ms var(--out);
}
#share-pop.open { opacity: 1; pointer-events: auto; transform: translateY(0); }
.sp-label  { font-size: 10.5px; font-weight: 600; color: var(--ink-600); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.55rem; }
.sp-url    { font-size: 11.5px; color: var(--ink-800); background: var(--bg-3); border-radius: var(--r-xs); padding: 0.38rem 0.6rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 0.5rem; font-family: var(--font-mono); display: block; }
.sp-copy   { width: 100%; padding: 0.48rem; background: var(--blue); color: #fff; border: none; border-radius: var(--r-xs); font-size: 13px; font-weight: 600; cursor: pointer; font-family: var(--font); transition: background 100ms; }
.sp-copy:hover { background: var(--blue-h); }

/* ══════════════════════════════════════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════════════════════════════════════ */
#sidebar {
  position: fixed; top: var(--bar); left: 0; bottom: 0;
  width: var(--sidebar); background: var(--bg-2);
  border-right: 0.5px solid var(--border-md);
  overflow-y: auto; z-index: 400;
  transition: transform 240ms var(--out), background 200ms var(--ease);
  padding: 0.5rem 0 5rem;
}
#sidebar.hidden { transform: translateX(calc(-1 * var(--sidebar))); }
#sidebar::-webkit-scrollbar { width: 3px; }
#sidebar::-webkit-scrollbar-thumb { background: var(--border-md); border-radius: 2px; }

.sb-group { padding: 0.6rem 0 0.2rem; }
.sb-group + .sb-group { border-top: 0.5px solid var(--divider); margin-top: 0.3rem; padding-top: 0.75rem; }
.sb-label { font-size: 9.5px; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; color: var(--ink-400); padding: 0 1rem 0.3rem; display: block; }
.sb-link  {
  display: flex; align-items: center;
  font-size: 12.5px; font-weight: 400; color: var(--ink-800);
  text-decoration: none; padding: 0.28rem 0.85rem;
  border-radius: var(--r-xs); margin: 0 0.35rem;
  transition: background 80ms var(--ease), color 80ms; line-height: 1.45;
  position: relative;
}
.sb-num { font-size: 9.5px; font-weight: 600; color: var(--ink-400); width: 20px; flex-shrink: 0; text-align: right; margin-right: 0.5rem; font-variant-numeric: tabular-nums; transition: color 80ms; }
.sb-link:hover { background: rgba(0,0,0,0.04); color: var(--ink-950); }
.sb-link.active { background: var(--blue-tint); color: var(--blue); font-weight: 500; }
.sb-link.active .sb-num { color: #60a5fa; }
.sb-link.active::before { content: ''; position: absolute; left: 0; top: 22%; bottom: 22%; width: 2px; background: var(--blue); border-radius: 0 2px 2px 0; }

/* ══════════════════════════════════════════════════════════════════════════
   BOTTOM NAV BAR (mobile ≤ 768px)
══════════════════════════════════════════════════════════════════════════ */
#bot-bar {
  display: none; position: fixed; bottom: 0; left: 0; right: 0;
  height: var(--bot); background: rgba(250,250,250,0.93);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  backdrop-filter: saturate(180%) blur(20px);
  border-top: 0.5px solid rgba(0,0,0,0.09);
  z-index: 450; padding-bottom: env(safe-area-inset-bottom);
  transition: background 200ms var(--ease);
}
.bot-inner { height: 62px; display: flex; align-items: center; }
.bot-btn {
  flex: 1; height: 100%; border: none; background: transparent;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 3px; cursor: pointer; color: var(--ink-600);
  font-family: var(--font);
  transition: color 100ms, transform 150ms var(--spring);
}
.bot-btn:active { transform: scale(0.88); }
.bot-icon  { font-size: 18px; line-height: 1; }
.bot-label { font-size: 9.5px; font-weight: 600; letter-spacing: 0.02em; }
@media (max-width: 768px) {
  #bot-bar { display: block; }
  #main    { padding-bottom: var(--bot); }
}

/* ══════════════════════════════════════════════════════════════════════════
   SLIDE-UP SHEET
══════════════════════════════════════════════════════════════════════════ */
#sheet-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4); z-index: 800;
  opacity: 0; pointer-events: none; transition: opacity 240ms var(--ease);
}
#sheet-overlay.open { opacity: 1; pointer-events: auto; }
#sheet {
  position: fixed; left: 0; right: 0; bottom: 0; max-height: 88vh;
  background: var(--bg); border-radius: 18px 18px 0 0; z-index: 850;
  overflow: hidden; display: flex; flex-direction: column;
  transform: translateY(100%); transition: transform 300ms var(--out), background 200ms var(--ease);
  padding-bottom: env(safe-area-inset-bottom);
}
#sheet.open { transform: translateY(0); }
.sheet-handle { width: 34px; height: 4px; background: var(--border-md); border-radius: 2px; margin: 10px auto 0; flex-shrink: 0; }
.sheet-head   { padding: 0.65rem 1.25rem 0.5rem; display: flex; align-items: center; justify-content: space-between; border-bottom: 0.5px solid var(--divider); flex-shrink: 0; }
.sheet-title  { font-size: 15px; font-weight: 700; color: var(--ink-950); letter-spacing: -0.02em; }
.sheet-close  { width: 26px; height: 26px; background: var(--bg-3); border: none; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; color: var(--ink-600); font-size: 13px; font-family: var(--font); }
.sheet-body   { overflow-y: auto; flex: 1; padding: 0.4rem 0 1rem; }
.sheet-body::-webkit-scrollbar { width: 3px; }
.sheet-body::-webkit-scrollbar-thumb { background: var(--border-md); }
.sheet-grp    { padding: 0.7rem 0 0.1rem; }
.sheet-grp + .sheet-grp { border-top: 0.5px solid var(--divider); margin-top: 0.2rem; }
.sheet-glabel { font-size: 9.5px; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; color: var(--ink-400); padding: 0 1.1rem 0.3rem; display: block; }
.sheet-link   { display: flex; align-items: center; padding: 0.48rem 1.1rem; font-size: 14px; font-weight: 400; color: var(--ink-800); text-decoration: none; gap: 0.6rem; transition: background 70ms; }
.sheet-link:active { background: var(--bg-3); }
.sheet-link.active { color: var(--blue); font-weight: 500; }
.sheet-num    { font-size: 10.5px; font-weight: 600; color: var(--ink-400); width: 20px; flex-shrink: 0; text-align: right; font-variant-numeric: tabular-nums; }
.sheet-link.active .sheet-num { color: #60a5fa; }

/* ══════════════════════════════════════════════════════════════════════════
   MAIN
══════════════════════════════════════════════════════════════════════════ */
#main { margin-left: var(--sidebar); margin-top: var(--bar); transition: margin-left 240ms var(--out); }
#main.full { margin-left: 0; }

/* ══════════════════════════════════════════════════════════════════════════
   COVER — Blueprint edition
══════════════════════════════════════════════════════════════════════════ */
#cover {
  min-height: 100vh;
  min-height: 100svh;  /* iOS 15.4+: excludes browser chrome */
  position: relative; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  padding: 5rem 2rem;
  background-color: #08111e;
  /* Blueprint grid — major + minor lines like a technical drawing */
  background-image:
    linear-gradient(rgba(0,100,200,0.18) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,100,200,0.18) 1px, transparent 1px),
    linear-gradient(rgba(0,100,200,0.07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,100,200,0.07) 1px, transparent 1px);
  background-size: 80px 80px, 80px 80px, 16px 16px, 16px 16px;
}

/* Radial glow centred on the title area */
#cover::before {
  content: '';
  position: absolute; inset: 0; z-index: 0;
  background: radial-gradient(ellipse 70% 55% at 50% 44%, rgba(0,90,200,0.22) 0%, transparent 72%);
  pointer-events: none;
}

/* Corner registration marks */
.cv-corner-tl, .cv-corner-tr, .cv-corner-bl, .cv-corner-br {
  position: absolute; width: 44px; height: 44px;
  border-color: rgba(0,113,227,0.5); border-style: solid;
  z-index: 2;
}
.cv-corner-tl { top: 1.75rem; left: 1.75rem; border-width: 1.5px 0 0 1.5px; }
.cv-corner-tr { top: 1.75rem; right: 1.75rem; border-width: 1.5px 1.5px 0 0; }
.cv-corner-bl { bottom: 1.75rem; left: 1.75rem; border-width: 0 0 1.5px 1.5px; }
.cv-corner-br { bottom: 1.75rem; right: 1.75rem; border-width: 0 1.5px 1.5px 0; }

/* Cover content */
.cv-content {
  position: relative; z-index: 2;
  text-align: center;
  max-width: 700px; width: 100%;
}
.cv-eyebrow {
  font-size: 11.5px; font-weight: 500; letter-spacing: 0.38em;
  text-transform: uppercase; color: rgba(255,255,255,0.62);
  margin-bottom: 1rem;
}
.cv-title {
  font-size: clamp(4.5rem, 16vw, 9.5rem);
  font-weight: 700; line-height: 0.9;
  letter-spacing: -0.035em;
  color: #ffffff;
  margin-bottom: 2.25rem;
}
/* "Blueprint" — lit up in blueprint blue with a soft luminous glow */
.cv-title em {
  font-style: normal;
  color: #5bb8ff;
  text-shadow:
    0 0 40px rgba(91,184,255,0.45),
    0 0 80px rgba(91,184,255,0.18);
}
.cv-rule {
  width: 100px; height: 1.5px;
  background: linear-gradient(90deg, transparent, #0071e3 30%, #0071e3 70%, transparent);
  margin: 0 auto 1.75rem;
}
.cv-sub {
  font-size: clamp(0.88rem, 2vw, 1rem);
  font-weight: 400; line-height: 1.7;
  color: rgba(255,255,255,0.62);
  max-width: 460px; margin: 0 auto 1rem;
  letter-spacing: -0.003em;
}
.cv-meta {
  font-size: 11px; font-weight: 500; letter-spacing: 0.1em;
  color: rgba(255,255,255,0.4);
  text-transform: uppercase; margin-bottom: 3rem;
}
.cv-cta {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: #0071e3; color: #fff;
  font-size: 14px; font-weight: 600; letter-spacing: -0.01em;
  padding: 0.8rem 2.25rem; border-radius: 100px;
  text-decoration: none;
  box-shadow: 0 4px 20px rgba(0,113,227,0.45), 0 1px 4px rgba(0,0,0,0.3);
  transition: background 160ms, transform 180ms var(--spring), box-shadow 180ms;
}
.cv-cta:hover { background: var(--blue-h); transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,113,227,0.55); }
.cv-cta:active { transform: scale(0.97); }

/* ══════════════════════════════════════════════════════════════════════════
   FRONT MATTER (Preface + TOC)
══════════════════════════════════════════════════════════════════════════ */
.front { max-width: var(--prose); margin: 0 auto; padding: 5.5rem 2rem; }
.front-rule { border: none; border-top: 0.5px solid var(--border-md); }

.front h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.025em; color: var(--ink-950); margin-bottom: 2.5rem; line-height: 1.1; }
.front p  { font-size: var(--size-body); line-height: var(--lh-body); color: var(--ink-800); margin-bottom: 1.15rem; }
.front p strong { font-weight: 700; color: var(--ink-950); }
.front p em     { font-style: italic; color: var(--ink-600); }

/* TOC */
.toc-part { font-size: 10px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--blue); margin: 3rem 0 0.6rem; }
.toc-list { list-style: none; }
.toc-list li { border-top: 0.5px solid var(--divider); }
.toc-list li:last-child { border-bottom: 0.5px solid var(--divider); }
.toc-list a {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.48rem 0; font-size: 14px; font-weight: 400;
  color: var(--ink-800); text-decoration: none;
  transition: color 80ms, padding-left 150ms var(--spring);
}
.toc-list a:hover { color: var(--blue); padding-left: 4px; }
.toc-num { font-size: 10px; font-weight: 600; color: var(--ink-400); width: 20px; flex-shrink: 0; text-align: right; font-variant-numeric: tabular-nums; transition: color 80ms; }
.toc-list a:hover .toc-num { color: var(--blue); }

/* ══════════════════════════════════════════════════════════════════════════
   PART DIVIDERS
══════════════════════════════════════════════════════════════════════════ */
.part-divider {
  padding: 5.5rem 2rem; text-align: center;
  background: var(--bg-2);
  border-top: 0.5px solid var(--border-md);
  border-bottom: 0.5px solid var(--border-md);
  position: relative; overflow: hidden;
  transition: background 200ms var(--ease);
}
.part-divider::before {
  content: ''; position: absolute;
  top: 0; left: 50%; transform: translateX(-50%);
  width: 180px; height: 1px;
  background: linear-gradient(90deg, transparent, var(--blue), transparent);
  opacity: 0.5;
}
.pd-eyebrow { font-size: 10px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--blue); margin-bottom: 0.85rem; }
.part-divider h2 { font-size: clamp(1.5rem, 4vw, 2.2rem); font-weight: 700; letter-spacing: -0.025em; color: var(--ink-950); margin-bottom: 0.75rem; border: none; padding: 0; }
.part-divider > p { font-size: 15px; line-height: 1.7; color: var(--ink-600); max-width: 460px; margin: 0 auto; }

/* ══════════════════════════════════════════════════════════════════════════
   CHAPTER LAYOUT
   Chapter opener shows a large decorative number behind the title —
   inspired by premium book design (chapter number as visual anchor).
══════════════════════════════════════════════════════════════════════════ */
section.chapter {
  max-width: var(--prose); margin: 0 auto;
  padding: 5rem 2rem 6rem;
  border-bottom: 0.5px solid var(--border-md);
  position: relative;
}
/* Decorative chapter number — visible behind the heading */
section.chapter[data-num]::before {
  content: attr(data-num);
  position: absolute;
  top: 3.5rem; right: 2rem;
  font-size: 8rem; font-weight: 700;
  letter-spacing: -0.05em; line-height: 1;
  color: var(--ink-200);
  pointer-events: none; user-select: none;
  transition: color 200ms var(--ease);
  font-variant-numeric: tabular-nums;
}
[data-theme="dark"] section.chapter[data-num]::before { color: rgba(255,255,255,0.04); }

.part-label {
  display: inline-block; font-size: 10px; font-weight: 600;
  letter-spacing: 0.1em; text-transform: uppercase; color: var(--blue);
  margin-bottom: 0.55rem;
}
.chapter-title {
  font-size: clamp(1.7rem, 4vw, 2.1rem); font-weight: 700;
  letter-spacing: -0.025em; line-height: 1.12; color: var(--ink-950);
  margin-bottom: 0.5rem; max-width: 540px;
}
.chapter-intro {
  font-size: 15.5px; font-weight: 400; line-height: 1.72;
  color: var(--ink-600); margin-bottom: 0.75rem;
}
/* Reading time badge */
.read-time {
  display: inline-flex; align-items: center; gap: 0.3rem;
  font-size: 11px; font-weight: 500; color: var(--ink-400);
  margin-bottom: 2.75rem; padding-bottom: 2rem;
  border-bottom: 0.5px solid var(--border-md); width: 100%;
}
.read-time::before { content: '◷'; font-size: 11px; }

/* ── Body elements ──────────────────────────────────────────────────────── */
p { margin-bottom: 1.1rem; }
ul, ol { margin: 0.5rem 0 1.1rem 1.5rem; }
li { margin-bottom: 0.4rem; line-height: var(--lh-body); }
strong { font-weight: 700; color: var(--ink-900); }
em     { font-style: italic; }
hr     { border: none; border-top: 0.5px solid var(--border-md); margin: 2.5rem 0; }
a      { color: var(--blue); text-decoration: none; transition: opacity 100ms; }
a:hover { opacity: 0.7; }

blockquote {
  border-left: 2px solid var(--blue-soft);
  padding: 0.5rem 0 0.5rem 1.25rem;
  margin: 1.75rem 0;
  color: var(--ink-600); font-style: italic;
}

h2 {
  font-size: 1.2rem; font-weight: 600; letter-spacing: -0.018em;
  color: var(--ink-950); margin: 3.25rem 0 0.75rem;
  padding: 0; border: none; line-height: 1.3;
}
h3 {
  font-size: 1.05rem; font-weight: 600; letter-spacing: -0.012em;
  color: var(--ink-900); margin: 2.25rem 0 0.5rem; line-height: 1.35;
}
h4 {
  font-size: 0.78rem; font-weight: 600; letter-spacing: 0.07em;
  text-transform: uppercase; color: var(--ink-600); margin: 1.75rem 0 0.45rem;
}

/* ── Tables ─────────────────────────────────────────────────────────────── */
.table-wrap { overflow-x: auto; margin: 1.75rem 0; border-radius: var(--r); border: 1px solid var(--border-md); box-shadow: var(--s1); }
table { border-collapse: collapse; width: 100%; }
th { background: var(--bg-3); font-size: 11px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: var(--ink-800); padding: 0.6rem 1rem; text-align: left; border-bottom: 1px solid var(--border-md); white-space: nowrap; }
td { padding: 0.58rem 1rem; font-size: 14px; color: var(--ink-800); border-bottom: 0.5px solid var(--divider); }
tr:last-child td { border-bottom: none; }
tbody tr { transition: background 60ms; }
tbody tr:hover td { background: rgba(0,113,227,0.02); }

/* ── Code ───────────────────────────────────────────────────────────────── */
/* Code blocks break out of the prose max-width constraint so they get
   full container width — avoids the horizontal scroll trap on mobile.     */
.code-block {
  margin: 1.75rem -1.4rem;   /* negative margin to escape prose padding */
  border-radius: var(--r); overflow: hidden;
  border: 1px solid rgba(255,255,255,0.05);
  box-shadow: var(--s3), 0 0 0 0.5px rgba(0,0,0,0.16);
}
@media (min-width: 720px) {
  .code-block { margin-left: 0; margin-right: 0; }
}
.code-bar   { background: #232326; padding: 0.5rem 1rem; display: flex; align-items: center; gap: 0.42rem; border-bottom: 0.5px solid rgba(255,255,255,0.06); }
.dot        { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
.dot-r { background: #ff5f57; } .dot-y { background: #febc2e; } .dot-g { background: #28c840; }
.code-copy {
  margin-left: auto; font-size: 11px; font-weight: 600;
  color: rgba(255,255,255,0.28); background: none;
  border: 0.5px solid rgba(255,255,255,0.1);
  border-radius: 4px; padding: 0.18rem 0.5rem;
  cursor: pointer; font-family: var(--font);
  transition: all 100ms;
}
.code-copy:hover  { color: rgba(255,255,255,0.72); border-color: rgba(255,255,255,0.28); }
.code-copy.copied { color: #28c840; border-color: #28c840; }
pre {
  background: var(--code-bg); color: var(--code-fg);
  padding: 1.25rem 1.4rem;
  /* Desktop: horizontal scroll for very wide code blocks */
  overflow-x: auto;
  font-family: var(--font-mono); font-size: 13px; line-height: 1.7;
  margin: 0; tab-size: 2;
  /* Wrap long lines so nothing is ever hidden off-screen on mobile */
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: break-word;
}
section.chapter > pre { border-radius: var(--r); border: 1px solid rgba(255,255,255,0.05); box-shadow: var(--s3); margin: 1.75rem 0; }
code { font-family: var(--font-mono); }
:not(pre) > code { background: var(--blue-tint); border: 0.5px solid var(--blue-soft); border-radius: var(--r-xs); padding: 0.12em 0.36em; font-size: 0.84em; color: #0058b8; font-weight: 500; }

/* ── Callout blocks ─────────────────────────────────────────────────────── */
.callout {
  display: flex; gap: 0.85rem;
  border-radius: var(--r); padding: 1.1rem 1.25rem;
  margin: 1.85rem 0; border: 0.5px solid transparent;
  transition: transform 180ms var(--spring), box-shadow 180ms, background 200ms;
}
.callout:hover { transform: translateY(-2px); box-shadow: var(--s2); }
.callout-icon { flex-shrink: 0; width: 28px; height: 28px; border-radius: var(--r-sm); display: flex; align-items: center; justify-content: center; font-size: 14px; align-self: flex-start; margin-top: 0.12rem; }
.callout-body { flex: 1; min-width: 0; }
.callout-body > :first-child { margin-top: 0; }
.callout-body > :last-child  { margin-bottom: 0; }
.callout-tag  { font-size: 10px; font-weight: 600; letter-spacing: 0.07em; text-transform: uppercase; display: block; margin-bottom: 0.35rem; }
.callout-body p, .callout-body li { color: var(--ink-800); margin-bottom: 0.4rem; font-size: calc(var(--size-body) * 0.96); }
.callout-body strong { font-weight: 700; }

/* Analogy */
.analogy    { background: var(--blue-tint);   border-color: rgba(0,113,227,0.16); }
.analogy    .callout-icon { background: #dbeafe; }
.analogy    .callout-tag  { color: var(--blue); }
.analogy    .callout-body strong { color: var(--blue); }
/* Real World */
.real-world { background: var(--amber-tint);  border-color: rgba(217,119,6,0.18); }
.real-world .callout-icon { background: var(--amber-soft); }
.real-world .callout-tag  { color: var(--amber); }
.real-world .callout-body strong { color: var(--amber); }
/* Research */
.research   { background: var(--purple-tint); border-color: rgba(124,58,237,0.18); }
.research   .callout-icon { background: var(--purple-soft); }
.research   .callout-tag  { color: var(--purple); }
.research   .callout-body strong { color: var(--purple); }
/* Lab */
.lab {
  background: var(--green-tint); border: 1px solid rgba(22,163,74,0.18);
  border-radius: var(--r); padding: 1.3rem 1.5rem; margin: 2.5rem 0;
  transition: transform 180ms var(--spring), box-shadow 180ms, background 200ms;
}
.lab:hover { transform: translateY(-2px); box-shadow: var(--s2); }
.lab-title { display: flex; align-items: center; gap: 0.5rem; font-size: 10px; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--green); margin-bottom: 0.8rem; }
.lab-title::before { content: '⚗️'; font-size: 13px; }
.lab p, .lab li { color: var(--ink-800); margin-bottom: 0.4rem; }
/* Takeaway — redesigned, clean gradient-border light card */
.takeaway {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, var(--blue-tint) 0%, var(--purple-tint) 100%);
  border: 1px solid rgba(0,113,227,0.12);
  border-radius: var(--r); padding: 1.4rem 1.6rem; margin: 2.5rem 0;
  transition: transform 180ms var(--spring), box-shadow 180ms, background 200ms;
}
.takeaway::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3.5px; background: linear-gradient(180deg, var(--blue) 0%, var(--purple) 100%); border-radius: 3px 0 0 3px; }
.takeaway:hover { transform: translateY(-2px); box-shadow: var(--s2); }
.takeaway p     { color: var(--ink-800); margin-bottom: 0.5rem; }
.takeaway p:last-child { margin-bottom: 0; }
.takeaway strong { color: var(--blue); font-weight: 700; }
.takeaway h3, .takeaway h4 { color: var(--ink-950); margin-top: 0; margin-bottom: 0.5rem; }

/* ── Glossary ───────────────────────────────────────────────────────────── */
dl { margin: 0.75rem 0 1.75rem; }
dt { font-size: 15.5px; font-weight: 600; color: var(--ink-900); margin-top: 1.3rem; letter-spacing: -0.01em; }
dd { margin-left: 1.25rem; font-size: 15px; color: var(--ink-800); margin-top: 0.1rem; line-height: 1.7; }

/* ── Chapter nav ────────────────────────────────────────────────────────── */
.chapter-nav { display: flex; justify-content: space-between; margin-top: 4rem; padding-top: 1.5rem; border-top: 0.5px solid var(--border-md); gap: 1rem; }
.chapter-nav a { font-size: 13.5px; font-weight: 600; color: var(--blue); text-decoration: none; padding: 0.45rem 0.85rem; border-radius: var(--r-sm); transition: background 100ms, transform 150ms var(--spring); display: flex; align-items: center; gap: 0.3rem; }
.chapter-nav a:hover { background: var(--blue-tint); opacity: 1; transform: scale(1.03); }

/* ── Back to top ────────────────────────────────────────────────────────── */
#back-to-top {
  position: fixed; bottom: 5.5rem; right: 1.5rem;
  height: 34px; padding: 0 1rem;
  background: rgba(255,255,255,0.92);
  -webkit-backdrop-filter: blur(16px); backdrop-filter: blur(16px);
  border: 0.5px solid var(--border-md); border-radius: 100px;
  cursor: pointer; font-size: 12px; font-weight: 600; color: var(--ink-900);
  display: flex; align-items: center; gap: 0.35rem;
  opacity: 0; pointer-events: none; z-index: 490; font-family: var(--font);
  transition: opacity 200ms, transform 220ms var(--spring), box-shadow 200ms, background 200ms;
  box-shadow: var(--s2);
}
#back-to-top.visible { opacity: 1; pointer-events: auto; }
#back-to-top:hover   { transform: translateY(-3px) scale(1.04); box-shadow: var(--s3); }
#back-to-top:active  { transform: scale(0.95); }
@media (min-width: 769px) { #back-to-top { bottom: 2rem; right: 2rem; } }

/* ── Resume toast ───────────────────────────────────────────────────────── */
#resume-toast {
  position: fixed; bottom: 5.5rem; left: 1rem;
  background: var(--ink-950); color: var(--bg);
  border-radius: 100px; padding: 0.52rem 1rem;
  font-size: 12.5px; font-weight: 500;
  display: flex; align-items: center; gap: 0.6rem;
  box-shadow: var(--s3); z-index: 600;
  opacity: 0; pointer-events: none; transform: translateY(8px);
  transition: opacity 250ms var(--ease), transform 250ms var(--out);
  max-width: calc(100vw - 2rem);
}
#resume-toast.show { opacity: 1; pointer-events: auto; transform: translateY(0); }
#resume-toast a    { color: #60a5fa; font-weight: 600; text-decoration: none; opacity: 1; white-space: nowrap; }
#toast-dismiss     { background: none; border: none; color: rgba(255,255,255,0.4); cursor: pointer; font-size: 15px; padding: 0; line-height: 1; font-family: var(--font); }
@media (min-width: 769px) { #resume-toast { bottom: 2rem; } }

/* ── Keyboard shortcuts overlay ─────────────────────────────────────────── */
#shortcuts-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 900; display: flex; align-items: center; justify-content: center; opacity: 0; pointer-events: none; transition: opacity 180ms; }
#shortcuts-overlay.open { opacity: 1; pointer-events: auto; }
#shortcuts-box { background: var(--bg); border-radius: var(--r); padding: 1.6rem 1.85rem; max-width: 350px; width: 90%; box-shadow: var(--s3); transition: background 200ms; }
#shortcuts-box h3 { font-size: 15px; font-weight: 700; color: var(--ink-950); margin-bottom: 1.15rem; margin-top: 0; letter-spacing: -0.018em; }
.sc-row { display: flex; align-items: center; justify-content: space-between; padding: 0.35rem 0; border-top: 0.5px solid var(--divider); font-size: 13.5px; color: var(--ink-800); }
.sc-row:first-of-type { border-top: none; }
.kbd { font-family: var(--font-mono); font-size: 11px; font-weight: 500; background: var(--bg-3); border: 0.5px solid var(--border-md); border-radius: 4px; padding: 0.15em 0.45em; color: var(--ink-800); transition: background 200ms; }
.sc-close { display: block; width: 100%; margin-top: 1.2rem; padding: 0.52rem; background: var(--bg-3); border: none; border-radius: var(--r-sm); font-size: 13.5px; font-weight: 600; color: var(--ink-800); cursor: pointer; font-family: var(--font); transition: background 100ms; }
.sc-close:hover { background: var(--border-md); }

/* ══════════════════════════════════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════════════════════════════════ */
@media (max-width: 900px) {
  #sidebar { transform: translateX(calc(-1 * var(--sidebar))); }
  #sidebar.visible { transform: translateX(0); }
  #main { margin-left: 0 !important; }
  section.chapter { padding: 3.5rem 1.25rem 4.5rem; }
  section.chapter[data-num]::before { font-size: 5rem; top: 2.5rem; right: 1.25rem; }
  .front { padding: 3.5rem 1.25rem; }
  .part-divider { padding: 4rem 1.25rem; }
}
@media (max-width: 768px) {
  #sidebar-toggle { display: none; }
}
@media (max-width: 560px) {
  .cv-title { font-size: 3.8rem; }
  pre { font-size: 11.5px; padding: 1rem 1rem; }
  .code-block { margin-left: -1rem; margin-right: -1rem; border-radius: 0; border-left: none; border-right: none; }
}

/* ══════════════════════════════════════════════════════════════════════════
   PRINT / PDF
══════════════════════════════════════════════════════════════════════════ */
@media print {
  #topbar, #sidebar, #back-to-top, #progress-bar,
  #bot-bar, #sheet, #sheet-overlay, #resume-toast,
  #shortcuts-overlay, .cv-cta { display: none !important; }
  #main { margin: 0 !important; }
  html, body { font-size: 11pt; line-height: 1.75; color: #000; }
  section.chapter { page-break-after: always; max-width: 100%; padding: 2rem 0; }
  section.chapter[data-num]::before { color: #eee; font-size: 4rem; top: 2rem; right: 0; }
  .part-divider { page-break-before: always; background: none; }
  pre { white-space: pre-wrap; font-size: 9pt; }
  a { color: #000; }
  orphans: 3; widows: 3;
}
</style>
</head>
<body>

<div id="progress-bar"></div>

<button id="back-to-top">
  <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
    <path d="M5 8.5V1.5M5 1.5L2 4.5M5 1.5L8 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  Top
</button>

<!-- Resume toast -->
<div id="resume-toast" role="status">
  <span id="toast-text">Continue reading:</span>
  <a href="#" id="toast-link">Chapter</a>
  <button id="toast-dismiss" aria-label="Dismiss">&#x2715;</button>
</div>

<!-- Keyboard shortcuts -->
<div id="shortcuts-overlay" role="dialog" aria-modal="true">
  <div id="shortcuts-box">
    <h3>Keyboard Shortcuts</h3>
    <div class="sc-row"><span>Next chapter</span><span class="kbd">→ / J</span></div>
    <div class="sc-row"><span>Previous chapter</span><span class="kbd">← / K</span></div>
    <div class="sc-row"><span>Toggle dark mode</span><span class="kbd">D</span></div>
    <div class="sc-row"><span>Back to top</span><span class="kbd">T</span></div>
    <div class="sc-row"><span>Toggle sidebar</span><span class="kbd">S</span></div>
    <div class="sc-row"><span>Show shortcuts</span><span class="kbd">?</span></div>
    <div class="sc-row"><span>Close</span><span class="kbd">Esc</span></div>
    <button class="sc-close" id="sc-close">Close</button>
  </div>
</div>

<!-- TOP BAR -->
<header id="topbar">
  <button class="tb-btn" id="sidebar-toggle" aria-label="Toggle sidebar">
    <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
      <path d="M1.5 3h12M1.5 7.5h12M1.5 12h12" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
    </svg>
  </button>
  <div class="tb-divider"></div>
  <span class="tb-title">The Architect's Blueprint</span>
  <span class="tb-crumb" id="tb-crumb"></span>
  <div class="tb-divider"></div>
  <button class="tb-btn tb-font" id="font-sm" title="Smaller text" aria-label="Decrease font size">A−</button>
  <button class="tb-btn tb-font" id="font-lg" title="Larger text"  aria-label="Increase font size">A+</button>
  <div class="tb-divider"></div>
  <button class="tb-btn" id="dark-toggle" title="Toggle dark mode" aria-label="Toggle dark mode">
    <svg id="icon-moon" width="14" height="14" viewBox="0 0 15 15" fill="none">
      <path d="M4 7.5a3.5 3.5 0 003.5 3.5c.5 0 1-.1 1.5-.3A6.5 6.5 0 014.3 4 6.5 6.5 0 107.5 14a6.5 6.5 0 000-13z" fill="currentColor" opacity=".9"/>
    </svg>
    <svg id="icon-sun" width="14" height="14" viewBox="0 0 15 15" fill="none" style="display:none">
      <circle cx="7.5" cy="7.5" r="2.5" stroke="currentColor" stroke-width="1.3"/>
      <path d="M7.5 1v1.5M7.5 12.5V14M1 7.5h1.5M12.5 7.5H14M3 3l1 1M11 11l1 1M3 12l1-1M11 4l1-1" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
  </button>
  <div class="tb-divider"></div>
  <div id="share-wrap">
    <button class="tb-btn" id="share-btn" title="Share" aria-label="Share this book">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <circle cx="11" cy="2.5" r="1.5" stroke="currentColor" stroke-width="1.3"/>
        <circle cx="11" cy="11.5" r="1.5" stroke="currentColor" stroke-width="1.3"/>
        <circle cx="3" cy="7" r="1.5" stroke="currentColor" stroke-width="1.3"/>
        <path d="M9.5 3.5l-5 2.5M9.5 10.5l-5-2.5" stroke="currentColor" stroke-width="1.3"/>
      </svg>
    </button>
    <div id="share-pop">
      <div class="sp-label">Copy chapter link</div>
      <code class="sp-url" id="sp-url"></code>
      <button class="sp-copy" id="sp-copy">Copy link</button>
    </div>
  </div>
</header>

<!-- SIDEBAR -->
<nav id="sidebar" aria-label="Chapters">
  <div class="sb-group">
    <span class="sb-label">Front Matter</span>
    <a class="sb-link" href="#cover"><span class="sb-num"></span>Cover</a>
    <a class="sb-link" href="#preface"><span class="sb-num"></span>Preface</a>
    <a class="sb-link" href="#toc"><span class="sb-num"></span>Contents</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Part 1: What Is a System?</span>
    <a class="sb-link" href="#ch01"><span class="sb-num">01</span>The City Analogy</a>
    <a class="sb-link" href="#ch02"><span class="sb-num">02</span>Clients and Servers</a>
    <a class="sb-link" href="#ch03"><span class="sb-num">03</span>Protocols</a>
    <a class="sb-link" href="#ch04"><span class="sb-num">04</span>APIs</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Part 2: Data and Storage</span>
    <a class="sb-link" href="#ch05"><span class="sb-num">05</span>What Is a Registry?</a>
    <a class="sb-link" href="#ch06"><span class="sb-num">06</span>The Database</a>
    <a class="sb-link" href="#ch07"><span class="sb-num">07</span>Authentication</a>
    <a class="sb-link" href="#ch08"><span class="sb-num">08</span>Routing</a>
    <a class="sb-link" href="#ch09"><span class="sb-num">09</span>Validation</a>
    <a class="sb-link" href="#ch10"><span class="sb-num">10</span>The Publisher</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Part 3: The AI Agent</span>
    <a class="sb-link" href="#ch11"><span class="sb-num">11</span>What Is an AI Agent?</a>
    <a class="sb-link" href="#ch12"><span class="sb-num">12</span>Tools</a>
    <a class="sb-link" href="#ch13"><span class="sb-num">13</span>Sessions</a>
    <a class="sb-link" href="#ch14"><span class="sb-num">14</span>Hooks</a>
    <a class="sb-link" href="#ch15"><span class="sb-num">15</span>Permissions &amp; Sandboxing</a>
    <a class="sb-link" href="#ch16"><span class="sb-num">16</span>The AI Client</a>
    <a class="sb-link" href="#ch17"><span class="sb-num">17</span>Skills</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Part 4: Shipping It</span>
    <a class="sb-link" href="#ch18"><span class="sb-num">18</span>Docker</a>
    <a class="sb-link" href="#ch19"><span class="sb-num">19</span>Kubernetes</a>
    <a class="sb-link" href="#ch20"><span class="sb-num">20</span>CI/CD</a>
    <a class="sb-link" href="#ch21"><span class="sb-num">21</span>Monitoring</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Part 5: AI and the Real World</span>
    <a class="sb-link" href="#ch22"><span class="sb-num">22</span>What AI Actually Is</a>
    <a class="sb-link" href="#ch23"><span class="sb-num">23</span>How AI Gets Hands</a>
    <a class="sb-link" href="#ch24"><span class="sb-num">24</span>Build Your Own AI Server</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Part 6: The Home Architect</span>
    <a class="sb-link" href="#ch25"><span class="sb-num">25</span>The Home Lab</a>
    <a class="sb-link" href="#ch26"><span class="sb-num">26</span>Smart Home Architecture</a>
    <a class="sb-link" href="#ch27"><span class="sb-num">27</span>Thinking Like an Architect</a>
    <a class="sb-link" href="#ch28"><span class="sb-num">28</span>Design Before You Build</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Part 7: Hands Applied</span>
    <a class="sb-link" href="#ch29"><span class="sb-num">29</span>Your First Architecture</a>
    <a class="sb-link" href="#ch30"><span class="sb-num">30</span>Product Thinking</a>
    <a class="sb-link" href="#ch31"><span class="sb-num">31</span>Product Strategy</a>
    <a class="sb-link" href="#ch32"><span class="sb-num">32</span>The Product Designer</a>
    <a class="sb-link" href="#ch33"><span class="sb-num">33</span>Teaching Others</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Part 8: Under the Hood</span>
    <a class="sb-link" href="#ch34"><span class="sb-num">34</span>Networking Internals</a>
    <a class="sb-link" href="#ch35"><span class="sb-num">35</span>Security &amp; Threat Models</a>
    <a class="sb-link" href="#ch36"><span class="sb-num">36</span>Prompt Engineering &amp; RAG</a>
  </div>
  <div class="sb-group">
    <span class="sb-label">Reference</span>
    <a class="sb-link" href="#appendix-a"><span class="sb-num">A</span>Glossary</a>
    <a class="sb-link" href="#appendix-b"><span class="sb-num">B</span>Cheat Sheet</a>
    <a class="sb-link" href="#appendix-c"><span class="sb-num">C</span>What to Learn Next</a>
    <a class="sb-link" href="#appendix-d"><span class="sb-num">D</span>Codebase Map</a>
  </div>
</nav>

<!-- BOTTOM BAR (mobile) -->
<div id="bot-bar">
  <div class="bot-inner">
    <button class="bot-btn" id="bot-contents" aria-label="Table of contents">
      <span class="bot-icon">☰</span><span class="bot-label">Contents</span>
    </button>
    <button class="bot-btn" id="bot-dark" aria-label="Toggle dark mode">
      <span class="bot-icon" id="bot-dark-icon">☾</span><span class="bot-label">Appearance</span>
    </button>
    <button class="bot-btn" id="bot-share" aria-label="Share">
      <span class="bot-icon">⬆</span><span class="bot-label">Share</span>
    </button>
  </div>
</div>

<!-- SLIDE-UP SHEET -->
<div id="sheet-overlay" aria-hidden="true"></div>
<div id="sheet" role="dialog" aria-modal="true" aria-label="Table of contents">
  <div class="sheet-handle" aria-hidden="true"></div>
  <div class="sheet-head">
    <span class="sheet-title">Chapters</span>
    <button class="sheet-close" id="sheet-close" aria-label="Close">&#x2715;</button>
  </div>
  <div class="sheet-body">
    <div class="sheet-grp"><span class="sheet-glabel">Front Matter</span>
      <a class="sheet-link" href="#cover"><span class="sheet-num"></span>Cover</a>
      <a class="sheet-link" href="#preface"><span class="sheet-num"></span>Preface</a>
      <a class="sheet-link" href="#toc"><span class="sheet-num"></span>Contents</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Part 1</span>
      <a class="sheet-link" href="#ch01"><span class="sheet-num">01</span>The City Analogy</a>
      <a class="sheet-link" href="#ch02"><span class="sheet-num">02</span>Clients and Servers</a>
      <a class="sheet-link" href="#ch03"><span class="sheet-num">03</span>Protocols</a>
      <a class="sheet-link" href="#ch04"><span class="sheet-num">04</span>APIs</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Part 2</span>
      <a class="sheet-link" href="#ch05"><span class="sheet-num">05</span>What Is a Registry?</a>
      <a class="sheet-link" href="#ch06"><span class="sheet-num">06</span>The Database</a>
      <a class="sheet-link" href="#ch07"><span class="sheet-num">07</span>Authentication</a>
      <a class="sheet-link" href="#ch08"><span class="sheet-num">08</span>Routing</a>
      <a class="sheet-link" href="#ch09"><span class="sheet-num">09</span>Validation</a>
      <a class="sheet-link" href="#ch10"><span class="sheet-num">10</span>The Publisher</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Part 3</span>
      <a class="sheet-link" href="#ch11"><span class="sheet-num">11</span>What Is an AI Agent?</a>
      <a class="sheet-link" href="#ch12"><span class="sheet-num">12</span>Tools</a>
      <a class="sheet-link" href="#ch13"><span class="sheet-num">13</span>Sessions</a>
      <a class="sheet-link" href="#ch14"><span class="sheet-num">14</span>Hooks</a>
      <a class="sheet-link" href="#ch15"><span class="sheet-num">15</span>Permissions &amp; Sandboxing</a>
      <a class="sheet-link" href="#ch16"><span class="sheet-num">16</span>The AI Client</a>
      <a class="sheet-link" href="#ch17"><span class="sheet-num">17</span>Skills</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Part 4</span>
      <a class="sheet-link" href="#ch18"><span class="sheet-num">18</span>Docker</a>
      <a class="sheet-link" href="#ch19"><span class="sheet-num">19</span>Kubernetes</a>
      <a class="sheet-link" href="#ch20"><span class="sheet-num">20</span>CI/CD</a>
      <a class="sheet-link" href="#ch21"><span class="sheet-num">21</span>Monitoring</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Part 5</span>
      <a class="sheet-link" href="#ch22"><span class="sheet-num">22</span>What AI Actually Is</a>
      <a class="sheet-link" href="#ch23"><span class="sheet-num">23</span>How AI Gets Hands</a>
      <a class="sheet-link" href="#ch24"><span class="sheet-num">24</span>Build Your Own AI Server</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Part 6</span>
      <a class="sheet-link" href="#ch25"><span class="sheet-num">25</span>The Home Lab</a>
      <a class="sheet-link" href="#ch26"><span class="sheet-num">26</span>Smart Home Architecture</a>
      <a class="sheet-link" href="#ch27"><span class="sheet-num">27</span>Thinking Like an Architect</a>
      <a class="sheet-link" href="#ch28"><span class="sheet-num">28</span>Design Before You Build</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Part 7</span>
      <a class="sheet-link" href="#ch29"><span class="sheet-num">29</span>Your First Architecture</a>
      <a class="sheet-link" href="#ch30"><span class="sheet-num">30</span>Product Thinking</a>
      <a class="sheet-link" href="#ch31"><span class="sheet-num">31</span>Product Strategy</a>
      <a class="sheet-link" href="#ch32"><span class="sheet-num">32</span>The Product Designer</a>
      <a class="sheet-link" href="#ch33"><span class="sheet-num">33</span>Teaching Others</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Part 8</span>
      <a class="sheet-link" href="#ch34"><span class="sheet-num">34</span>Networking Internals</a>
      <a class="sheet-link" href="#ch35"><span class="sheet-num">35</span>Security &amp; Threat Models</a>
      <a class="sheet-link" href="#ch36"><span class="sheet-num">36</span>Prompt Engineering &amp; RAG</a>
    </div>
    <div class="sheet-grp"><span class="sheet-glabel">Reference</span>
      <a class="sheet-link" href="#appendix-a"><span class="sheet-num">A</span>Glossary</a>
      <a class="sheet-link" href="#appendix-b"><span class="sheet-num">B</span>Cheat Sheet</a>
      <a class="sheet-link" href="#appendix-c"><span class="sheet-num">C</span>What to Learn Next</a>
      <a class="sheet-link" href="#appendix-d"><span class="sheet-num">D</span>Codebase Map</a>
    </div>
  </div>
</div>

<div id="main">

<!-- ══ COVER ═══════════════════════════════════════════════════════════════ -->
<section id="cover">
  <div class="cv-corner-tl" aria-hidden="true"></div>
  <div class="cv-corner-tr" aria-hidden="true"></div>
  <div class="cv-corner-bl" aria-hidden="true"></div>
  <div class="cv-corner-br" aria-hidden="true"></div>
  <div class="cv-content">
    <div class="cv-eyebrow">The Architect's</div>
    <h1 class="cv-title"><em>Blueprint</em></h1>
    <div class="cv-rule" aria-hidden="true"></div>
    <p class="cv-sub">Systems thinking, AI internals, and production infrastructure. Explained simply, grounded in real code.</p>
    <p class="cv-meta">36 Chapters &nbsp;·&nbsp; 8 Parts &nbsp;·&nbsp; 36+ Labs &nbsp;·&nbsp; 4 Appendices</p>
    <a href="#preface" class="cv-cta">Start Reading &#8595;</a>
  </div>
</section>

<hr class="front-rule">

<!-- ══ PREFACE ══════════════════════════════════════════════════════════════ -->
<section id="preface">
  <div class="front">
    <h1>Preface</h1>
    <p>This book started with a question: <em>Why is this so hard to explain?</em> Not hard to build. Hard to explain. The code was all there. The patterns were clear. But every time I tried to point someone at a real codebase and say "look, this is how an AI agent works," I watched their eyes glaze over at line three.</p>
    <p>The problem was not the complexity. Every explanation started in the middle. It assumed you already knew what a server was, what a database did, why anyone would care about authentication. Most books for beginners avoid real systems entirely. Most books for practitioners assume you are already a practitioner.</p>
    <p>This book is the one I wanted to read when I was starting out. It teaches real systems using the simplest possible language and the most direct possible analogies. Every chapter starts with something you already understand and ends with something running on your machine.</p>
    <p><strong>What you will find here:</strong> Thirty-six chapters covering systems thinking, backend architecture, AI internals, deployment infrastructure, smart home design, product strategy, networking, and security. Each chapter includes a hands-on lab, a real-world connection, and a research spotlight linking concepts to the papers that shaped modern computing.</p>
    <p><strong>What you will not find here:</strong> Hype. Oversimplification. Toy examples. Every concept is grounded in real, running systems. The code you read about is the code that runs in production.</p>
    <p>This book is for anyone who looks at a software system and wants to truly understand it.</p>
    <p><em>Every expert was once a beginner who refused to stop asking questions.</em></p>
  </div>
</section>

<hr class="front-rule">

<!-- ══ TABLE OF CONTENTS ════════════════════════════════════════════════════ -->
<section id="toc">
  <div class="front">
    <h1>Table of Contents</h1>
    <div class="toc-part">Part 1: What Is a System?</div>
    <ul class="toc-list">
      <li><a href="#ch01"><span class="toc-num">01</span>The City Analogy</a></li>
      <li><a href="#ch02"><span class="toc-num">02</span>Clients and Servers</a></li>
      <li><a href="#ch03"><span class="toc-num">03</span>Protocols</a></li>
      <li><a href="#ch04"><span class="toc-num">04</span>APIs</a></li>
    </ul>
    <div class="toc-part">Part 2: Data and Storage</div>
    <ul class="toc-list">
      <li><a href="#ch05"><span class="toc-num">05</span>What Is a Registry?</a></li>
      <li><a href="#ch06"><span class="toc-num">06</span>The Database: Your Filing Cabinet</a></li>
      <li><a href="#ch07"><span class="toc-num">07</span>Authentication: Proving Who You Are</a></li>
      <li><a href="#ch08"><span class="toc-num">08</span>Routing: The Postal Sorting Office</a></li>
      <li><a href="#ch09"><span class="toc-num">09</span>Validation: The Building Inspector</a></li>
      <li><a href="#ch10"><span class="toc-num">10</span>The Publisher: Getting Your Tool into the World</a></li>
    </ul>
    <div class="toc-part">Part 3: The AI Agent</div>
    <ul class="toc-list">
      <li><a href="#ch11"><span class="toc-num">11</span>What Is an AI Agent?</a></li>
      <li><a href="#ch12"><span class="toc-num">12</span>Tools: The Agent's Hands</a></li>
      <li><a href="#ch13"><span class="toc-num">13</span>Sessions and Conversations</a></li>
      <li><a href="#ch14"><span class="toc-num">14</span>Hooks: Safety Checkpoints</a></li>
      <li><a href="#ch15"><span class="toc-num">15</span>Permissions and Sandboxing</a></li>
      <li><a href="#ch16"><span class="toc-num">16</span>The AI Client</a></li>
      <li><a href="#ch17"><span class="toc-num">17</span>Skills: Pre-Packaged Intelligence</a></li>
    </ul>
    <div class="toc-part">Part 4: Shipping It</div>
    <ul class="toc-list">
      <li><a href="#ch18"><span class="toc-num">18</span>Docker: The Shipping Container</a></li>
      <li><a href="#ch19"><span class="toc-num">19</span>Kubernetes: The Orchestra Conductor</a></li>
      <li><a href="#ch20"><span class="toc-num">20</span>CI/CD: The Assembly Line</a></li>
      <li><a href="#ch21"><span class="toc-num">21</span>Monitoring: The Control Room Dashboard</a></li>
    </ul>
    <div class="toc-part">Part 5: AI and the Real World</div>
    <ul class="toc-list">
      <li><a href="#ch22"><span class="toc-num">22</span>What AI Actually Is (No Hype)</a></li>
      <li><a href="#ch23"><span class="toc-num">23</span>How AI Gets Hands</a></li>
      <li><a href="#ch24"><span class="toc-num">24</span>Building Your Own AI Server</a></li>
    </ul>
    <div class="toc-part">Part 6: The Home Architect</div>
    <ul class="toc-list">
      <li><a href="#ch25"><span class="toc-num">25</span>The Home Lab: Your Personal Data Center</a></li>
      <li><a href="#ch26"><span class="toc-num">26</span>Smart Home Architecture</a></li>
      <li><a href="#ch27"><span class="toc-num">27</span>Thinking Like an Architect</a></li>
      <li><a href="#ch28"><span class="toc-num">28</span>Design Before You Build</a></li>
    </ul>
    <div class="toc-part">Part 7: Hands Applied</div>
    <ul class="toc-list">
      <li><a href="#ch29"><span class="toc-num">29</span>Your First Architecture</a></li>
      <li><a href="#ch30"><span class="toc-num">30</span>Product Thinking: Seeing Problems as Systems</a></li>
      <li><a href="#ch31"><span class="toc-num">31</span>Product Strategy: From Idea to Architecture</a></li>
      <li><a href="#ch32"><span class="toc-num">32</span>The Product Designer's Chapter</a></li>
      <li><a href="#ch33"><span class="toc-num">33</span>Teaching Others</a></li>
    </ul>
    <div class="toc-part">Part 8: Under the Hood</div>
    <ul class="toc-list">
      <li><a href="#ch34"><span class="toc-num">34</span>Networking Internals</a></li>
      <li><a href="#ch35"><span class="toc-num">35</span>Security &amp; Threat Models</a></li>
      <li><a href="#ch36"><span class="toc-num">36</span>Prompt Engineering &amp; RAG</a></li>
    </ul>
    <div class="toc-part">Reference</div>
    <ul class="toc-list">
      <li><a href="#appendix-a"><span class="toc-num">A</span>Glossary</a></li>
      <li><a href="#appendix-b"><span class="toc-num">B</span>Cheat Sheet</a></li>
      <li><a href="#appendix-c"><span class="toc-num">C</span>What to Learn Next</a></li>
      <li><a href="#appendix-d"><span class="toc-num">D</span>Codebase Map</a></li>
    </ul>
  </div>
</section>

<div class="part-divider" id="part1">
  <div class="pd-eyebrow">Part One</div>
  <h2>What Is a System?</h2>
  <p>Before you can build anything, you need to see how things connect. Every digital product, every AI tool, every service you use: they are all cities you have not yet learned to read.</p>
</div>

CONTENT_PLACEHOLDER

</div><!-- #main -->

<script>
const $ = id => document.getElementById(id);
const LS = { get: k => localStorage.getItem(k), set: (k,v) => localStorage.setItem(k,v) };

// ── Theme ──────────────────────────────────────────────────────────────────
function getTheme() { return LS.get('book_dark') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'); }
function setTheme(t) {
  document.documentElement.dataset.theme = t; LS.set('book_dark', t);
  const d = t === 'dark';
  $('icon-moon').style.display = d ? 'none' : ''; $('icon-sun').style.display = d ? '' : 'none';
  $('bot-dark-icon').textContent = d ? '☀' : '☾';
}
setTheme(getTheme());
$('dark-toggle').addEventListener('click', () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'));
$('bot-dark').addEventListener('click',    () => setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark'));

// ── Font size ──────────────────────────────────────────────────────────────
const SIZES = ['sm','md','lg'];
function setSize(s) { document.documentElement.dataset.fontsize = s; LS.set('book_fontsize', s); }
setSize(LS.get('book_fontsize') || 'md');
$('font-sm').addEventListener('click', () => { const i = SIZES.indexOf(document.documentElement.dataset.fontsize); if (i > 0) setSize(SIZES[i-1]); });
$('font-lg').addEventListener('click', () => { const i = SIZES.indexOf(document.documentElement.dataset.fontsize); if (i < 2) setSize(SIZES[i+1]); });

// ── Progress ───────────────────────────────────────────────────────────────
const bar = $('progress-bar');
addEventListener('scroll', () => {
  const h = document.documentElement;
  bar.style.width = Math.min(h.scrollTop / (h.scrollHeight - h.clientHeight) * 100, 100) + '%';
}, { passive: true });

// ── Back to top ────────────────────────────────────────────────────────────
const btt = $('back-to-top');
addEventListener('scroll', () => btt.classList.toggle('visible', scrollY > 700), { passive: true });
btt.addEventListener('click', () => scrollTo({ top: 0, behavior: 'smooth' }));

// ── Sidebar ────────────────────────────────────────────────────────────────
const sidebar = $('sidebar'), mainEl = $('main'), sbBtn = $('sidebar-toggle');
const mob = () => innerWidth <= 900;
document.addEventListener('click', e => { if (mob() && sidebar.classList.contains('visible') && !sidebar.contains(e.target) && !sbBtn.contains(e.target)) sidebar.classList.remove('visible'); });
addEventListener('resize', () => { if (!mob()) sidebar.classList.remove('visible'); }, { passive: true });
sbBtn.addEventListener('click', () => { if (mob()) sidebar.classList.toggle('visible'); else { const h = sidebar.classList.toggle('hidden'); mainEl.classList.toggle('full', h); } });

// ── Sheet ──────────────────────────────────────────────────────────────────
const shOverlay = $('sheet-overlay'), shEl = $('sheet');
const openSheet  = () => { shOverlay.classList.add('open'); shEl.classList.add('open'); document.body.style.overflow = 'hidden'; };
const closeSheet = () => { shOverlay.classList.remove('open'); shEl.classList.remove('open'); document.body.style.overflow = ''; };
$('bot-contents').addEventListener('click', openSheet);
$('sheet-close').addEventListener('click',  closeSheet);
shOverlay.addEventListener('click', closeSheet);
shEl.querySelectorAll('.sheet-link').forEach(l => l.addEventListener('click', closeSheet));

// ── Active chapter tracking ────────────────────────────────────────────────
const sbLinks  = document.querySelectorAll('.sb-link[href^="#"]');
const shLinks  = document.querySelectorAll('.sheet-link[href^="#"]');
const crumb    = $('tb-crumb');
const sbMap = {}, shMap = {};
sbLinks.forEach(l => sbMap[l.getAttribute('href').slice(1)] = l);
shLinks.forEach(l => shMap[l.getAttribute('href').slice(1)] = l);
let curId = null;

new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    const id = e.target.id; if (id === curId) return; curId = id;
    sbLinks.forEach(l => l.classList.remove('active'));
    shLinks.forEach(l => l.classList.remove('active'));
    const sa = sbMap[id], sh = shMap[id];
    if (sa) { sa.classList.add('active'); sa.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
    if (sh) sh.classList.add('active');
    if (crumb) crumb.textContent = sa ? sa.textContent.trim().replace(/^\d+\s*/,'') : '';
    LS.set('book_chapter', id);
    LS.set('book_chapter_label', crumb ? crumb.textContent : id);
  });
}, { rootMargin: '-6% 0px -78% 0px' }).observe && document.querySelectorAll('section[id]').forEach(s => {
  new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      const id = e.target.id; if (id === curId) return; curId = id;
      sbLinks.forEach(l => l.classList.remove('active'));
      shLinks.forEach(l => l.classList.remove('active'));
      const sa = sbMap[id], sh = shMap[id];
      if (sa) { sa.classList.add('active'); sa.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
      if (sh) sh.classList.add('active');
      if (crumb) crumb.textContent = sa ? sa.textContent.trim().replace(/^\d+\s*/,'') : '';
      LS.set('book_chapter', id);
      LS.set('book_chapter_label', crumb ? crumb.textContent : id);
    });
  }, { rootMargin: '-6% 0px -78% 0px' }).observe(s);
});

// Better IntersectionObserver — just one
const io = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (!e.isIntersecting) return;
    const id = e.target.id; if (id === curId) return; curId = id;
    sbLinks.forEach(l => l.classList.remove('active'));
    shLinks.forEach(l => l.classList.remove('active'));
    const sa = sbMap[id], sh = shMap[id];
    if (sa) { sa.classList.add('active'); sa.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
    if (sh) sh.classList.add('active');
    if (crumb) crumb.textContent = sa ? sa.textContent.trim().replace(/^\d+\s*/,'') : '';
    LS.set('book_chapter', id);
    LS.set('book_chapter_label', crumb ? crumb.textContent : id);
  });
}, { rootMargin: '-6% 0px -78% 0px' });
document.querySelectorAll('section[id]').forEach(s => io.observe(s));

// ── Resume toast ───────────────────────────────────────────────────────────
const savedCh = LS.get('book_chapter'), savedLbl = LS.get('book_chapter_label');
const toast = $('resume-toast');
if (savedCh && savedCh !== 'cover' && !location.hash) {
  $('toast-link').textContent = savedLbl || savedCh;
  $('toast-link').href = '#' + savedCh;
  $('toast-link').addEventListener('click', () => toast.classList.remove('show'));
  setTimeout(() => toast.classList.add('show'), 900);
  setTimeout(() => toast.classList.remove('show'), 7000);
}
$('toast-dismiss').addEventListener('click', () => toast.classList.remove('show'));

// ── Share ──────────────────────────────────────────────────────────────────
const sharePop = $('share-pop'), shareBtn = $('share-btn');
function chapterHref() { return location.href.split('#')[0] + (curId ? '#' + curId : ''); }
shareBtn.addEventListener('click', async e => {
  e.stopPropagation();
  if (navigator.share) { try { await navigator.share({ title: document.title, text: "The Architect's Blueprint", url: chapterHref() }); return; } catch(_){} }
  $('sp-url').textContent = chapterHref().replace(location.origin,'').slice(0,55);
  sharePop.classList.toggle('open');
});
document.addEventListener('click', e => { if (!$('share-wrap').contains(e.target)) sharePop.classList.remove('open'); });
$('sp-copy').addEventListener('click', () => {
  navigator.clipboard.writeText(chapterHref()).then(() => { $('sp-copy').textContent = 'Copied!'; setTimeout(() => $('sp-copy').textContent = 'Copy link', 1800); });
});
$('bot-share').addEventListener('click', async () => {
  if (navigator.share) { try { await navigator.share({ title: document.title, url: chapterHref() }); return; } catch(_){} }
  navigator.clipboard.writeText(chapterHref()).then(() => { $('bot-share').querySelector('.bot-label').textContent = 'Copied!'; setTimeout(() => $('bot-share').querySelector('.bot-label').textContent = 'Share', 1800); });
});

// ── Keyboard shortcuts ─────────────────────────────────────────────────────
const scOverlay = $('shortcuts-overlay');
const chIds = [...document.querySelectorAll('section.chapter[id]')].map(s => s.id);
addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (scOverlay.classList.contains('open')) { if (e.key === 'Escape') scOverlay.classList.remove('open'); return; }
  const idx = chIds.indexOf(curId);
  if (e.key === 'ArrowRight' || e.key === 'j' || e.key === 'J') { if (idx < chIds.length-1) document.getElementById(chIds[idx+1])?.scrollIntoView({ behavior: 'smooth' }); }
  else if (e.key === 'ArrowLeft' || e.key === 'k' || e.key === 'K') { if (idx > 0) document.getElementById(chIds[idx-1])?.scrollIntoView({ behavior: 'smooth' }); }
  else if (e.key === 'd' || e.key === 'D') setTheme(document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark');
  else if (e.key === 't' || e.key === 'T') scrollTo({ top: 0, behavior: 'smooth' });
  else if (e.key === 's' || e.key === 'S') { if (!mob()) { const h = sidebar.classList.toggle('hidden'); mainEl.classList.toggle('full', h); } }
  else if (e.key === '?') scOverlay.classList.add('open');
  else if (e.key === 'Escape') { closeSheet(); sharePop.classList.remove('open'); }
});
$('sc-close').addEventListener('click', () => scOverlay.classList.remove('open'));
scOverlay.addEventListener('click', e => { if (e.target === scOverlay) scOverlay.classList.remove('open'); });

// ── Reading time ───────────────────────────────────────────────────────────
document.querySelectorAll('section.chapter').forEach(sec => {
  const words = sec.innerText.trim().split(/\s+/).length;
  const mins  = Math.max(1, Math.round(words / 200));
  const badge = document.createElement('div');
  badge.className = 'read-time'; badge.textContent = `${mins} min read`;
  const intro = sec.querySelector('.chapter-intro');
  if (intro) intro.after(badge); else sec.querySelector('.chapter-title')?.after(badge);
});

// ── Add chapter number data attribute ─────────────────────────────────────
document.querySelectorAll('section.chapter[id]').forEach(sec => {
  const m = sec.id.match(/ch(\d+)/);
  if (m) sec.setAttribute('data-num', m[1].padStart(2,'0'));
});

// ── Code blocks → macOS window ─────────────────────────────────────────────
document.querySelectorAll('section.chapter > pre, .front pre').forEach(pre => {
  const wrap = document.createElement('div'); wrap.className = 'code-block';
  const barEl = document.createElement('div'); barEl.className = 'code-bar';
  barEl.innerHTML = '<span class="dot dot-r"></span><span class="dot dot-y"></span><span class="dot dot-g"></span>';
  const cp = document.createElement('button'); cp.className = 'code-copy'; cp.textContent = 'Copy';
  cp.addEventListener('click', () => { navigator.clipboard.writeText(pre.textContent).then(() => { cp.textContent = 'Copied!'; cp.classList.add('copied'); setTimeout(() => { cp.textContent = 'Copy'; cp.classList.remove('copied'); }, 1800); }); });
  barEl.appendChild(cp);
  pre.parentNode.insertBefore(wrap, pre); wrap.appendChild(barEl); wrap.appendChild(pre);
});

// ── Tables ─────────────────────────────────────────────────────────────────
document.querySelectorAll('section.chapter table, .front table').forEach(t => {
  if (t.closest('.table-wrap')) return;
  const w = document.createElement('div'); w.className = 'table-wrap';
  t.parentNode.insertBefore(w, t); w.appendChild(t);
});

// ── Callout blocks ─────────────────────────────────────────────────────────
function upgradeCallout(sel, icon, label) {
  document.querySelectorAll(sel).forEach(el => {
    if (el.querySelector('.callout-icon')) return;
    el.classList.add('callout');
    const chip = document.createElement('div'); chip.className = 'callout-icon'; chip.textContent = icon;
    const body = document.createElement('div'); body.className = 'callout-body';
    const tag  = document.createElement('span'); tag.className = 'callout-tag'; tag.textContent = label;
    body.appendChild(tag);
    while (el.firstChild) body.appendChild(el.firstChild);
    el.appendChild(chip); el.appendChild(body);
  });
}
upgradeCallout('.analogy',    '💡', 'Analogy');
upgradeCallout('.real-world', '🌍', 'Real World');
upgradeCallout('.research',   '🔬', 'Research Spotlight');

// ── Part dividers ──────────────────────────────────────────────────────────
const parts = {
  ch05: ['Part Two',   'Data and Storage',      'How information is stored, protected, and routed. Chapters 5 through 10 walk through databases, authentication, routing, validation, and publishing.'],
  ch11: ['Part Three', 'The AI Agent',          'What actually runs when you talk to an AI assistant. The loop, the tools, the hooks, the sessions. All of it, explained from the ground up.'],
  ch18: ['Part Four',  'Shipping It',           'Getting from a working program to a production service. Docker, Kubernetes, CI/CD, and monitoring: the four pillars of deployment.'],
  ch22: ['Part Five',  'AI and the Real World', 'What AI actually is (no hype), how it gets the ability to take action, and how to build your own tool-enabled AI server from scratch.'],
  ch25: ['Part Six',   'The Home Architect',    "Your bedroom as a data center. Your home as a system. The architect's lens applied to the physical world around you."],
  ch29: ['Part Seven', 'Hands Applied',         'Everything converges. Build a real architecture, think like a product manager, design like a professional, and teach it to others.'],
  ch34: ['Part Eight', 'Under the Hood',        'The three topics every builder eventually needs: how data actually travels, how systems get attacked, and how to talk to AI effectively.'],
};
Object.entries(parts).forEach(([id, [num, title, desc]]) => {
  const sec = document.getElementById(id); if (!sec) return;
  const div = document.createElement('div'); div.className = 'part-divider';
  div.innerHTML = `<div class="pd-eyebrow">${num}</div><h2>${title}</h2><p>${desc}</p>`;
  sec.parentNode.insertBefore(div, sec);
});
</script>
</body>
</html>
"""

HTML = HTML.replace('CONTENT_PLACEHOLDER', combined)
with open('book.html', 'w', encoding='utf-8') as f:
    f.write(HTML)

kb = len(HTML.encode()) // 1024
print(f"book.html       OK  {kb} KB")
