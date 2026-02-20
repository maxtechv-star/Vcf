const { Pool } = require('pg');
require('dotenv').config();

let pool;

if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL env var is required');
}

pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

const MIGRATION_SQL = `
CREATE TABLE IF NOT EXISTS contacts (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  phone TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE (phone)
);

CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT INTO settings (key, value)
SELECT 'target_count', COALESCE(current_setting('app.target_count', true), '700')
WHERE NOT EXISTS (SELECT 1 FROM settings WHERE key = 'target_count');
`;

async function initDb() {
  try {
    await pool.query(MIGRATION_SQL);
    console.log('✅ DB migration completed (contacts & settings ready).');
  } catch (err) {
    console.error('❌ DB migration error:', err);
    throw err;
  }
}

async function query(text, params) {
  return pool.query(text, params);
}

async function getSetting(key) {
  const res = await pool.query('SELECT value FROM settings WHERE key = $1 LIMIT 1', [key]);
  if (res.rowCount === 0) return null;
  return res.rows[0].value;
}

async function setSetting(key, value) {
  await pool.query(
    `INSERT INTO settings (key, value)
     VALUES ($1, $2)
     ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value`,
    [key, value]
  );
}

async function getTargetCount() {
  const fromDb = await getSetting('target_count');
  if (fromDb) {
    const n = parseInt(fromDb, 10);
    if (!isNaN(n) && n > 0) return n;
  }
  const fromEnv = parseInt(process.env.TARGET_COUNT || '', 10);
  if (!isNaN(fromEnv) && fromEnv > 0) return fromEnv;
  return 700;
}

module.exports = {
  query,
  getSetting,
  setSetting,
  getTargetCount,
  initDb,
};
