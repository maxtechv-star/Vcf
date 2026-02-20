const db = require('../lib/db');

async function parseJsonBody(req) {
  return new Promise((resolve) => {
    let raw = '';
    req.on('data', (chunk) => (raw += chunk));
    req.on('end', () => {
      try { resolve(raw ? JSON.parse(raw) : {}); }
      catch (e) { resolve({}); }
    });
    req.on('error', () => resolve({}));
  });
}

function isAdmin(req) {
  const cookieHeader = req.headers.cookie || '';
  return cookieHeader.split(';').some((c) => c.trim() === 'meta_admin=1');
}

module.exports = async (req, res) => {
  if (!isAdmin(req)) {
    res.statusCode = 401;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'unauthorized' }));
  }
  if (req.method !== 'POST') {
    res.statusCode = 405;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'method not allowed' }));
  }
  try {
    const body = req.body || (await parseJsonBody(req));
    const { confirm_password } = body || {};
    const REQUIRED = process.env.RESET_CONFIRM || '1542';
    if (String(confirm_password) !== String(REQUIRED)) {
      res.statusCode = 400;
      res.setHeader('Content-Type', 'application/json');
      return res.end(JSON.stringify({ error: 'incorrect confirm password' }));
    }
    if (!process.env.DATABASE_URL) {
      res.statusCode = 500;
      res.setHeader('Content-Type', 'application/json');
      return res.end(JSON.stringify({ error: 'DATABASE_URL not configured' }));
    }
    await db.query('DELETE FROM contacts');
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ success: true }));
  } catch (err) {
    console.error('api/admin/reset error:', err);
    res.statusCode = 500;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'db error' }));
  }
};