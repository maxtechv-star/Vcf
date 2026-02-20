require('dotenv').config();
const express = require('express');
const cookieParser = require('cookie-parser');
const path = require('path');
const { query, getTargetCount, getSetting, setSetting, initDb } = require('./lib/db');

const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, '../public')));

// View engine
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../views'));

// Initialize DB on startup
initDb().catch(err => {
  console.error('Failed to init DB:', err);
  process.exit(1);
});

// ============ PAGES ============

app.get('/', async (req, res) => {
  try {
    const countRes = await query('SELECT COUNT(*)::int AS count FROM contacts');
    const collected = countRes.rows[0]?.count ?? 0;
    const target = await getTargetCount();
    const remaining = Math.max(0, target - collected);
    const percent = target > 0 ? Math.round((collected / target) * 1000) / 10 : 0;

    res.render('index', {
      collected,
      target,
      remaining,
      percent,
      whatsappLink: 'https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa?mode=gi_t',
      disclaimer: '⚠️ If you don\'t join the group or follow the channel, don\'t blame me if you miss the file! Make sure to join and stay active.'
    });
  } catch (err) {
    console.error(err);
    res.status(500).render('error', { message: 'Server error' });
  }
});

app.get('/admin-login', (req, res) => {
  res.render('admin-login', { error: null });
});

app.get('/admin', (req, res) => {
  if (req.cookies.meta_admin !== '1') {
    return res.redirect('/admin-login');
  }
  res.render('admin', { whatsappLink: 'https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa?mode=gi_t' });
});

// ============ API ROUTES ============

// Submit contact
app.post('/api/contacts', async (req, res) => {
  const { full_name, phone } = req.body || {};

  if (!full_name || !phone) {
    return res.status(400).json({ success: false, message: 'full_name and phone are required' });
  }

  try {
    await query(
      `INSERT INTO contacts (full_name, phone) VALUES ($1, $2) ON CONFLICT DO NOTHING`,
      [full_name.trim(), phone.trim()]
    );
    return res.status(201).json({ success: true });
  } catch (err) {
    console.error('Error inserting contact', err);
    return res.status(500).json({ success: false, message: 'DB error' });
  }
});

// Get count
app.get('/api/count', async (req, res) => {
  try {
    const result = await query('SELECT COUNT(*)::int AS count FROM contacts');
    const collected = result.rows[0]?.count ?? 0;
    const target = await getTargetCount();
    const remaining = Math.max(0, target - collected);
    const percent = target > 0 ? Math.round((collected / target) * 1000) / 10 : 0;
    res.status(200).json({ collected, target, remaining, percent });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'DB error' });
  }
});

// Login
app.post('/api/admin/login', async (req, res) => {
  const { username, password } = req.body || {};

  const ADMIN_USER = process.env.ADMIN_USER || 'admin';
  const ADMIN_PASS = process.env.ADMIN_PASS || 'uthuman';

  if (!username || !password) {
    return res.status(400).json({ success: false, message: 'username and password required' });
  }

  if (username === ADMIN_USER && password === ADMIN_PASS) {
    const secureFlag = process.env.NODE_ENV === 'production' ? '; Secure; SameSite=Lax' : '; SameSite=Lax';
    res.setHeader(
      'Set-Cookie',
      `meta_admin=1; Path=/; HttpOnly${secureFlag}; Max-Age=${60 * 60 * 24}`
    );
    return res.status(200).json({ success: true });
  } else {
    return res.status(401).json({ success: false, message: 'Invalid credentials' });
  }
});

// Export VCF (admin only)
app.get('/api/admin/export-vcf', async (req, res) => {
  if (req.cookies.meta_admin !== '1') {
    return res.status(401).json({ error: 'unauthorized' });
  }

  try {
    const countRes = await query('SELECT COUNT(*)::int AS count FROM contacts');
    const collected = countRes.rows[0]?.count ?? 0;
    const target = await getTargetCount();

    if (collected < target) {
      return res.status(403).json({ error: 'Target not reached yet' });
    }

    const rows = (await query('SELECT full_name, phone FROM contacts ORDER BY id')).rows;
    const vcard = rows.map((r) => {
      const escapedName = (r.full_name || '').replace(/\n/g, ' ');
      return `BEGIN:VCARD
VERSION:3.0
FN:${escapedName}
TEL;TYPE=CELL:${r.phone}
END:VCARD
`;
    }).join('\n');

    const filename = 'meta-contacts.vcf';
    res.setHeader('Content-Type', 'text/vcard; charset=utf-8');
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    return res.status(200).send(vcard);
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'server error' });
  }
});

// Reset contacts (admin only)
app.post('/api/admin/reset', async (req, res) => {
  if (req.cookies.meta_admin !== '1') {
    return res.status(401).json({ error: 'unauthorized' });
  }

  const { confirm_password } = req.body || {};
  const REQUIRED = process.env.RESET_CONFIRM || '1542';

  if (confirm_password !== REQUIRED) {
    return res.status(400).json({ error: 'incorrect confirm password' });
  }

  try {
    await query('DELETE FROM contacts');
    return res.status(200).json({ success: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'db error' });
  }
});

// Set custom goal (admin only)
app.post('/api/admin/set-goal', async (req, res) => {
  if (req.cookies.meta_admin !== '1') {
    return res.status(401).json({ error: 'unauthorized' });
  }

  const { goal } = req.body || {};
  const n = parseInt(String(goal || ''), 10);
  if (isNaN(n) || n <= 0) {
    return res.status(400).json({ error: 'invalid goal' });
  }

  try {
    await setSetting('target_count', String(n));
    return res.status(200).json({ success: true, goal: n });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'db error' });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// 404
app.use((req, res) => {
  res.status(404).render('error', { message: 'Page not found' });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`✅ Meta VCF running on port ${PORT}`);
});

module.exports = app;
