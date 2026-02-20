const db = require('./lib/db');

module.exports = async (req, res) => {
  try {
    let collected = 0;
    if (process.env.DATABASE_URL) {
      const result = await db.query('SELECT COUNT(*)::int AS count FROM contacts');
      collected = result.rows[0]?.count ?? 0;
    }
    const target = await db.getTargetCount();
    const remaining = Math.max(0, target - collected);
    const percent = target > 0 ? Math.round((collected / target) * 1000) / 10 : 0;
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.end(JSON.stringify({ collected, target, remaining, percent }));
  } catch (err) {
    console.error('api/count error:', err);
    res.statusCode = 500;
    res.end(JSON.stringify({ error: 'DB error' }));
  }
};