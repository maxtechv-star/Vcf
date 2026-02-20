const ejs = require('ejs');
const path = require('path');
const db = require('./lib/db');

module.exports = async (req, res) => {
  try {
    let collected = 0;
    if (process.env.DATABASE_URL) {
      const countRes = await db.query('SELECT COUNT(*)::int AS count FROM contacts');
      collected = countRes.rows[0]?.count ?? 0;
    }
    const target = await db.getTargetCount();
    const remaining = Math.max(0, target - collected);
    const percent = target > 0 ? Math.round((collected / target) * 1000) / 10 : 0;

    const viewPath = path.join(__dirname, '../views/index.ejs');
    const html = await new Promise((resolve, reject) => {
      ejs.renderFile(
        viewPath,
        {
          collected,
          target,
          remaining,
          percent,
          whatsappLink: 'https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa?mode=gi_t',
          otherProject: 'https://aj-ibra.zone.id/',
          disclaimer: "⚠️ If you don't join the group or follow the channel, don't blame me if you miss the file! Make sure to join and stay active.",
          footerCredit: 'Built by Meta Team'
        },
        {},
        (err, str) => (err ? reject(err) : resolve(str))
      );
    });

    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.statusCode = 200;
    res.end(html);
  } catch (err) {
    console.error('api/index error:', err);
    res.statusCode = 500;
    res.end('Internal Server Error');
  }
};