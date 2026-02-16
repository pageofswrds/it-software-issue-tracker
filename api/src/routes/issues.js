// api/src/routes/issues.js
import { Router } from 'express';
import { query, queryOne } from '../db.js';

const router = Router();

// Get single issue
router.get('/:id', async (req, res) => {
  try {
    const issue = await queryOne(
      `SELECT i.*, a.name as application_name, a.vendor
       FROM issues i
       JOIN applications a ON a.id = i.application_id
       WHERE i.id = $1`,
      [req.params.id]
    );
    if (!issue) {
      return res.status(404).json({ error: 'Issue not found' });
    }
    res.json(issue);
  } catch (err) {
    console.error('Error fetching issue:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new issue (manual entry)
router.post('/', async (req, res) => {
  try {
    const { application_id, title, summary, severity, issue_type, source_url } = req.body;
    if (!application_id || !title || !summary || !severity) {
      return res.status(400).json({ error: 'application_id, title, summary, and severity are required' });
    }
    if (!['critical', 'major', 'minor'].includes(severity)) {
      return res.status(400).json({ error: 'severity must be critical, major, or minor' });
    }

    const issue = await queryOne(
      `INSERT INTO issues (application_id, title, summary, severity, issue_type, source_type, source_url)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING *`,
      [application_id, title, summary, severity, issue_type || null, 'manual', source_url || `manual-${Date.now()}`]
    );
    res.status(201).json(issue);
  } catch (err) {
    console.error('Error creating issue:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
