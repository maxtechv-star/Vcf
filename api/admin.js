const ejs = require('ejs');
const path = require('path');
const db = require('./lib/db');

function isAdminCookie(req) {
  const cookieHeader = req.headers.cookie || '';
  return cookieHeader.split(';').some((c) => c.trim() === 'meta_admin=1');
}

module.exports = async (req, res) => {
  if (!isAdminCookie(req)) {
    res.statusCode = 302;
    res.setHeader('Location', '/admin-login');
    return res.end();
  }

  try {
    let collected = 0;
    let target = await db.getTargetCount();
    if (process.env.DATABASE_URL) {
      const countRes = await db.query('SELECT COUNT(*)::int AS count FROM contacts');
      collected = countRes.rows[0]?.count ?? 0;
    }

    const viewPath = path.join(__dirname, '../views/admin.ejs');
    const html = await new Promise((resolve, reject) => {
      ejs.renderFile(
        viewPath,
        { collected, target, whatsappLink: 'https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa?mode=gi_t' },
        {},
        (err, str) => (err ? reject(err) : resolve(str))
      );
    });

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.statusCode = 200;
    res.end(html);
  } catch (err) {
    console.error('api/admin error:', err);
    res.statusCode = 500;
    res.end('Internal Server Error');
  }
};