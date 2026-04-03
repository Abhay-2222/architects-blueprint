require('dotenv').config();
const express  = require('express');
const session  = require('express-session');
const path     = require('path');
const fs       = require('fs');

const app  = express();
const PORT = process.env.PORT || 3000;
const PERMALINK    = process.env.GUMROAD_PERMALINK || 'architects-blueprint';
const SESSION_SECRET = process.env.SESSION_SECRET || 'dev-secret-change-in-production';
const IS_PROD = process.env.NODE_ENV === 'production';

// ── Middleware ────────────────────────────────────────────────────────────────
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/static', express.static(path.join(__dirname, 'public')));

app.use(session({
  secret: SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,          // JS cannot read this cookie
    secure: IS_PROD,         // HTTPS only in production
    sameSite: 'lax',
    maxAge: 30 * 24 * 60 * 60 * 1000  // 30 days
  }
}));

// ── Auth check helper ─────────────────────────────────────────────────────────
function isVerified(req) {
  return req.session && req.session.verified === true;
}

// ── Routes ────────────────────────────────────────────────────────────────────

// GET / — lock screen or book
app.get('/', (req, res) => {
  if (isVerified(req)) {
    serveBook(req, res);
  } else {
    res.sendFile(path.join(__dirname, 'public', 'lock.html'));
  }
});

// POST /api/auth — verify Gumroad license key
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
      req.session.verified    = true;
      req.session.email       = data.purchase?.email || 'reader';
      req.session.licenseKey  = key;
      return res.json({ success: true });
    }

    // Gumroad returned success: false
    const msg = data.message || 'Invalid license key.';
    if (msg.toLowerCase().includes('disabled')) {
      return res.status(401).json({ error: 'This license key has been disabled. Please contact support.' });
    }
    return res.status(401).json({ error: 'Invalid license key. Check your purchase email and try again.' });

  } catch (err) {
    console.error('Gumroad verification failed:', err.message);
    return res.status(500).json({ error: 'Could not reach the verification server. Please try again.' });
  }
});

// POST /api/logout
app.post('/api/logout', (req, res) => {
  req.session.destroy(() => res.redirect('/'));
});

// ── Book server ───────────────────────────────────────────────────────────────
function serveBook(req, res) {
  const bookPath = path.join(__dirname, 'book.html');

  if (!fs.existsSync(bookPath)) {
    return res.status(500).send(`
      <h2>book.html not found</h2>
      <p>Run <code>cd ../html && python build_book.py</code> then copy
      <code>book.html</code> into the <code>backend/</code> folder.</p>
    `);
  }

  let html = fs.readFileSync(bookPath, 'utf8');
  const email = req.session.email || 'reader';

  // ── Watermark ────────────────────────────────────────────────────────────
  // Faint fixed watermark in the corner tied to the buyer's email.
  // Visible on screenshots — deters sharing.
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

  const wmEl  = `<div id="_wm">${escHtml(email)}</div>`;

  // ── Copy protection ───────────────────────────────────────────────────────
  const protectionCSS = `
<style>
/* Disable text selection on prose — code blocks are exempt so students
   can still copy lab commands */
section.chapter p,
section.chapter h1,
section.chapter h2,
section.chapter h3,
section.chapter h4,
section.chapter li,
section.chapter blockquote,
section.chapter td,
section.chapter th,
.front p, .front h1 {
  user-select: none;
  -webkit-user-select: none;
}
/* Block print-to-PDF — shows a message instead of book content */
@media print {
  body > *           { display: none !important; }
  body::after {
    content: "This book is licensed for screen reading only. Licensed to ${escHtml(email)}";
    display: block; font-size: 1.5rem;
    text-align: center; padding-top: 40vh;
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
#_logout:hover { color: var(--ink-950); border-color: var(--border-md); background: var(--bg-3); }
</style>`;

  // Inject logout button into topbar (before the closing </header>)
  const logoutBtn = `
  <form action="/api/logout" method="POST" style="display:contents">
    <button id="_logout" type="submit" title="Sign out">Sign out</button>
  </form>`;

  // ── Keyboard copy block (JS) ──────────────────────────────────────────────
  const protectionJS = `
<script>
(function() {
  // Block Ctrl+C on prose (allow in code blocks and inputs)
  document.addEventListener('copy', function(e) {
    var sel = window.getSelection();
    if (!sel || !sel.rangeCount) return;
    var node = sel.getRangeAt(0).commonAncestorContainer;
    // Walk up to see if we're inside a pre/code/input
    var el = node.nodeType === 3 ? node.parentElement : node;
    while (el) {
      if (['PRE','CODE','INPUT','TEXTAREA'].includes(el.tagName)) return;
      el = el.parentElement;
    }
    e.preventDefault();
  });

  // Block right-click on content (allow on code blocks)
  document.getElementById('main').addEventListener('contextmenu', function(e) {
    var el = e.target;
    while (el) {
      if (['PRE','CODE'].includes(el.tagName)) return;
      el = el.parentElement;
    }
    e.preventDefault();
  });
})();
</script>`;

  // Assemble final HTML
  html = html
    .replace('</head>', wmCSS + protectionCSS + logoutCSS + '</head>')
    .replace('</header>', logoutBtn + '</header>')
    .replace('</body>', wmEl + protectionJS + '</body>');

  res.send(html);
}

// Minimal HTML escaping for injected strings
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Start ─────────────────────────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`Gumroad permalink: ${PERMALINK}`);
  console.log(`Environment: ${IS_PROD ? 'production' : 'development'}`);
});
