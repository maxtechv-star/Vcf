// Database helper for serverless functions
const { Pool } = require('pg');
require('dotenv').config();

let pool;

if (!process.env.DATABASE_URL) {
  // In serverless (Vercel) you must set DATABASE_URL in project env.
  // For local dev, copy .env.example to .env and fill.
  console.warn('Warning: DATABASE_URL not set. DB calls will fail until set.');
}

function createPool() {
  if (!process.env.DATABASE_URL) return null;
  return new Pool({
    connectionString: process.env.DATABASE_URL,
    // Many managed Postgres require SSL. If you need it, set PGSSLMODE=require or uncomment:
    ssl: { rejectUnauthorized: false }
  });
}

pool = createPool();

/**
 * SQL migration executed on first require.
 * This will try to create tables if they don't exist.
 * Will only run if database connection is available.
 */
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
  if (!pool) return;
  try {
    await pool.query(MIGRATION_SQL);
    console.log('DB migration completed (contacts & settings ready).');
  } catch (err) {
    console.error('DB migration error:', err);
    throw err;
  }
}

// Run migration if pool exists (do not throw if no DB configured)
if (pool) {
  initDb().catch((err) => {
    // Migration failure will be logged. For Vercel serverless this may surface in logs.
    console.error('initDb error:', err);
  });
}

async function query(text, params) {
  if (!pool) throw new Error('DATABASE_URL not configured');
  return pool.query(text, params);
}

async function getSetting(key) {
  if (!pool) return null;
  const res = await pool.query('SELECT value FROM settings WHERE key = $1 LIMIT 1', [key]);
  if (res.rowCount === 0) return null;
  return res.rows[0].value;
}

async function setSetting(key, value) {
  if (!pool) throw new Error('DATABASE_URL not configured');
  await pool.query(
    `INSERT INTO settings (key, value)
     VALUES ($1, $2)
     ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value`,
    [key, value]
  );
}

async function getTargetCount() {
  // Priority: DB setting -> env TARGET_COUNT -> default 700
  if (pool) {
    const fromDb = await getSetting('target_count');
    if (fromDb) {
      const n = parseInt(fromDb, 10);
      if (!isNaN(n) && n > 0) return n;
    }
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
  initDb
};