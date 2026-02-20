const db = require('../lib/db');

function isAdmin(req) {
  const cookieHeader = req.headers.cookie || '';
  return cookieHeader.split(';').some((c) => c.trim() === 'meta_admin=1');
}

function makeVCard(name, phone) {
  const escapedName = (name || '').replace(/\n/g, ' ');
  return `BEGIN:VCARD
VERSION:3.0
FN:${escapedName}
TEL;TYPE=CELL:${phone}
END:VCARD
`;
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

    const countRes = await db.query('SELECT COUNT(*)::int AS count FROM contacts');
    const collected = countRes.rows[0]?.count ?? 0;
    const target = await db.getTargetCount();

    if (collected < target) {
      res.statusCode = 403;
      res.setHeader('Content-Type', 'application/json');
      return res.end(JSON.stringify({ error: 'Target not reached yet' }));
    }

    const rows = (await db.query('SELECT full_name, phone FROM contacts ORDER BY id')).rows;
    const vcard = rows.map((r) => makeVCard(r.full_name, r.phone)).join('\n');

    res.setHeader('Content-Type', 'text/vcard; charset=utf-8');
    res.setHeader('Content-Disposition', 'attachment; filename="meta-contacts.vcf"');
    res.statusCode = 200;
    return res.end(vcard);
  } catch (err) {
    console.error('api/admin/export-vcf error:', err);
    res.statusCode = 500;
    res.setHeader('Content-Type', 'application/json');
    return res.end(JSON.stringify({ error: 'server error' }));
  }
};