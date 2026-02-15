// api/src/db.js
import pg from 'pg';
import pgvector from 'pgvector/pg';

const { Pool } = pg;

let pool = null;
let typesRegistered = false;

export async function getPool() {
  if (!pool) {
    pool = new Pool({
      connectionString: process.env.DATABASE_URL
    });
  }
  if (!typesRegistered) {
    const client = await pool.connect();
    try {
      await pgvector.registerTypes(client);
    } finally {
      client.release();
    }
    typesRegistered = true;
  }
  return pool;
}

export async function query(text, params) {
  const pool = await getPool();
  const result = await pool.query(text, params);
  return result.rows;
}

export async function queryOne(text, params) {
  const rows = await query(text, params);
  return rows[0] || null;
}
