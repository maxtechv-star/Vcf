const db = require('../lib/db');

function isAdmin(req) {
  const cookieHeader = req.headers.cookie || '';
  return cookieHeader.split(';').some((c) => c.trim() === 'meta_admin=1');
}

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
    const id = body?.id;
    if (!id || isNaN(parseInt(id, 10))) {
      res.statusCode = 400;
      res.setHeader('Content-Type', 'application/json');
      return res.end(JSON.stringify({ error: 'invalid id' }));
    }
    await db.query('DELETE FROM contacts WHERE id = $1', [parseInt(id, 10)]);
    res.statusCode = 200;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ success: true }));
  } catch (err) {
    console.error('api/admin/delete-contact error:', err);
    res.statusCode = 500;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'db error' }));
  }
};