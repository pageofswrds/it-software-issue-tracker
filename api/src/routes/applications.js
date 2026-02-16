// api/src/routes/applications.js
import { Router } from 'express';
import { query, queryOne } from '../db.js';

const router = Router();

// List all applications with issue counts
router.get('/', async (req, res) => {
  try {
    const apps = await query(`
      SELECT
        a.*,
        COALESCE(SUM(CASE WHEN i.severity = 'critical' THEN 1 ELSE 0 END), 0)::int as critical_count,
        COALESCE(SUM(CASE WHEN i.severity = 'major' THEN 1 ELSE 0 END), 0)::int as major_count,
        COALESCE(SUM(CASE WHEN i.severity = 'minor' THEN 1 ELSE 0 END), 0)::int as minor_count,
        COUNT(i.id)::int as total_issues
      FROM applications a
      LEFT JOIN issues i ON i.application_id = a.id
      GROUP BY a.id
      ORDER BY a.name
    `);
    res.json(apps);
  } catch (err) {
    console.error('Error fetching applications:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get single application
router.get('/:id', async (req, res) => {
  try {
    const app = await queryOne(
      'SELECT * FROM applications WHERE id = $1',
      [req.params.id]
    );
    if (!app) {
      return res.status(404).json({ error: 'Application not found' });
    }
    res.json(app);
  } catch (err) {
    console.error('Error fetching application:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get issues for application
router.get('/:id/issues', async (req, res) => {
  try {
    const { severity } = req.query;
    let queryText = `
      SELECT * FROM issues
      WHERE application_id = $1
    `;
    const params = [req.params.id];

    if (severity) {
      queryText += ' AND severity = $2';
      params.push(severity);
    }

    queryText += ' ORDER BY created_at DESC LIMIT 100';

    const issues = await query(queryText, params);
    res.json(issues);
  } catch (err) {
    console.error('Error fetching issues:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new application
router.post('/', async (req, res) => {
  try {
    const { name, vendor, keywords } = req.body;
    if (!name) {
      return res.status(400).json({ error: 'Application name is required' });
    }
    const keywordArray = keywords
      ? keywords.split(',').map(k => k.trim()).filter(Boolean)
      : [name.toLowerCase()];

    const app = await queryOne(
      `INSERT INTO applications (name, vendor, keywords)
       VALUES ($1, $2, $3)
       RETURNING *`,
      [name, vendor || null, keywordArray]
    );
    res.status(201).json(app);
  } catch (err) {
    console.error('Error creating application:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
