require('dotenv').config();
const express = require('express');
const jwt     = require('jsonwebtoken');
const path    = require('path');
const fs      = require('fs');

const app  = express();
const PORT = process.env.PORT || 3000;

const PERMALINK    = process.env.GUMROAD_PERMALINK || 'architects-blueprint';
const JWT_SECRET   = process.env.JWT_SECRET || 'dev-secret-change-before-deploying';
const IS_PROD      = process.env.NODE_ENV === 'production';
const COOKIE_NAME  = 'bp_auth';
const COOKIE_TTL   = 30 * 24 * 60 * 60;   // 30 days in seconds

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/static', express.static(path.join(__dirname, 'public')));

// ── Cookie helpers ────────────────────────────────────────────────────────────
function setAuthCookie(res, payload) {
  const token = jwt.sign(payload, JWT_SECRET, { expiresIn: COOKIE_TTL });
  res.cookie(COOKIE_NAME, token, {
    httpOnly: true,          // JS in browser cannot read this
    secure:   IS_PROD,       // HTTPS only in production
    sameSite: 'lax',
    maxAge:   COOKIE_TTL * 1000
  });
}

function getAuthPayload(req) {
  try {
    const token = req.cookies?.[COOKIE_NAME]
                  || req.headers.cookie?.match(new RegExp(`${COOKIE_NAME}=([^;]+)`))?.[1];
    if (!token) return null;
    return jwt.verify(token, JWT_SECRET);
  } catch {
    return null;
  }
}

// Parse cookies manually (no cookie-parser dependency needed)
app.use((req, _res, next) => {
  req.cookies = {};
  const raw = req.headers.cookie || '';
  raw.split(';').forEach(pair => {
    const [k, ...v] = pair.trim().split('=');
    if (k) req.cookies[k.trim()] = decodeURIComponent(v.join('='));
  });
  next();
});

// ── Routes ────────────────────────────────────────────────────────────────────

// GET / — lock screen or book
app.get('/', (req, res) => {
  const auth = getAuthPayload(req);
  if (auth?.verified) {
    serveBook(req, res, auth);
  } else {
    res.sendFile(path.join(__dirname, 'public', 'lock.html'));
  }
});

// POST /api/auth — verify Gumroad license key, set JWT cookie
app.post('/api/auth', async (req, res) => {
  const key = (req.body.license_key || '').trim();

  if (!key) {
    return res.status(400).json({ error: 'Please enter your license key.' });
  }

  try {
    const response = await fetch('https://api.gumroad.com/v2/licenses/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        product_permalink:    PERMALINK,
        license_key:          key,
        increment_uses_count: 'false'
      })
    });

    const data = await response.json();

    if (data.success) {
      const payload = {
        verified:   true,
        email:      data.purchase?.email || 'reader',
        licenseKey: key
      };
      setAuthCookie(res, payload);
      return res.json({ success: true });
    }

    // Gumroad returned success: false
    const msg = (data.message || '').toLowerCase();
    if (msg.includes('disabled')) {
      return res.status(401).json({
        error: 'This license key has been disabled. Please contact support.'
      });
    }
    return res.status(401).json({
      error: 'Invalid license key. Check your purchase email and try again.'
    });

  } catch (err) {
    console.error('Gumroad verification error:', err.message);
    return res.status(500).json({
      error: 'Could not reach the verification server. Please try again.'
    });
  }
});

// POST /api/logout — clear JWT cookie
app.post('/api/logout', (_req, res) => {
  res.clearCookie(COOKIE_NAME);
  res.redirect('/');
});

// ── Book server ───────────────────────────────────────────────────────────────
function serveBook(req, res, auth) {
  const bookPath = path.join(__dirname, 'book.html');

  if (!fs.existsSync(bookPath)) {
    return res.status(500).send(`
      <h2 style="font-family:sans-serif;padding:2rem">book.html not found</h2>
      <p style="font-family:sans-serif;padding:0 2rem">
        Copy <code>html/book.html</code> into the <code>backend/</code> folder.
      </p>
    `);
  }

  let html = fs.readFileSync(bookPath, 'utf8');
  const email = auth.email || 'reader';

  // ── Watermark ────────────────────────────────────────────────────────────
  const wmCSS = `
<style>
#_wm {
  position: fixed; bottom: 0.9rem; right: 1.1rem;
  font-size: 10px; color: rgba(0,0,0,0.09);
  font-family: monospace; letter-spacing: 0.03em;
  z-index: 9998; pointer-events: none;
  user-select: none; -webkit-user-select: none;
}
[data-theme="dark"] #_wm { color: rgba(255,255,255,0.07); }
</style>`;
  const wmEl = `<div id="_wm">${escHtml(email)}</div>`;

  // ── Copy protection ───────────────────────────────────────────────────────
  const protectionCSS = `
<style>
section.chapter p,
section.chapter h1, section.chapter h2,
section.chapter h3, section.chapter h4,
section.chapter li, section.chapter blockquote,
section.chapter td, section.chapter th,
.front p, .front h1 {
  user-select: none;
  -webkit-user-select: none;
}
@media print {
  body > * { display: none !important; }
  body::after {
    content: "Licensed to ${escHtml(email)}. Screen reading only.";
    display: block; font-size: 1.4rem;
    text-align: center; padding-top: 40vh;
    font-family: sans-serif;
  }
}
</style>`;

  // ── Logout button ─────────────────────────────────────────────────────────
  const logoutCSS = `
<style>
#_logout {
  font-size: 11px; color: var(--ink-600);
  background: none; border: 0.5px solid var(--border-md);
  border-radius: var(--r-xs); cursor: pointer;
  font-family: var(--font); padding: 0.18rem 0.55rem;
  transition: all 100ms; flex-shrink: 0;
}
#_logout:hover { color: var(--ink-950); background: var(--bg-3); }
</style>`;
  const logoutBtn = `
  <form action="/api/logout" method="POST" style="display:contents">
    <button id="_logout" type="submit">Sign out</button>
  </form>`;

  // ── Copy / right-click block ──────────────────────────────────────────────
  const protectionJS = `
<script>
(function() {
  document.addEventListener('copy', function(e) {
    var node = (window.getSelection()?.getRangeAt(0)
                .commonAncestorContainer);
    var el = node?.nodeType === 3 ? node.parentElement : node;
    while (el) {
      if (['PRE','CODE','INPUT','TEXTAREA'].includes(el.tagName)) return;
      el = el.parentElement;
    }
    e.preventDefault();
  });
  var main = document.getElementById('main');
  if (main) main.addEventListener('contextmenu', function(e) {
    var el = e.target;
    while (el) {
      if (['PRE','CODE'].includes(el.tagName)) return;
      el = el.parentElement;
    }
    e.preventDefault();
  });
})();
</script>`;

  html = html
    .replace('</head>', wmCSS + protectionCSS + logoutCSS + '</head>')
    .replace('</header>', logoutBtn + '</header>')
    .replace('</body>', wmEl + protectionJS + '</body>');

  res.send(html);
}

function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ── Start (local dev only — Vercel uses module.exports) ───────────────────────
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Running on http://localhost:${PORT}`);
    console.log(`Gumroad permalink: ${PERMALINK}`);
  });
}

module.exports = app;
