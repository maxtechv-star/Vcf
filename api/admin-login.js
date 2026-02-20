const ejs = require('ejs');
const path = require('path');

module.exports = async (req, res) => {
  try {
    const viewPath = path.join(__dirname, '../views/admin-login.ejs');
    const html = await new Promise((resolve, reject) => {
      ejs.renderFile(viewPath, {}, {}, (err, str) => (err ? reject(err) : resolve(str)));
    });
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    res.statusCode = 200;
    res.end(html);
  } catch (err) {
    console.error('api/admin-login error:', err);
    res.statusCode = 500;
    res.end('Internal Server Error');
  }
};