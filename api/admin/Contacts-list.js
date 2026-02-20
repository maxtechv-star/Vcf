const db = require('../lib/db');

function isAdmin(req) {
  const cookieHeader = req.headers.cookie || '';
  return cookieHeader.split(';').some((c) => c.trim() === 'meta_admin=1');
}

module.exports = async (req, res) => {
  try {
    if (!isAdmin(req)) {
      res.statusCode = 401;
      res.setHeader('Content-Type', 'application/json');
      return res.end(JSON.stringify({ error: 'unauthorized' }));
    }

    if (!process.env.DATABASE_URL) {
      res.statusCode = 500;
      res.setHeader('Content-Type', 'application/json');
      return res.end(JSON.stringify({ error: 'DATABASE_URL not configured' }));
    }

    const rows = (await db.query('SELECT id, full_name, phone, created_at FROM contacts ORDER BY created_at DESC')).rows;
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.statusCode = 200;
    return res.end(JSON.stringify(rows));
  } catch (err) {
    console.error('api/admin/contacts-list error:', err);
    res.statusCode = 500;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'server error' }));
  }
};