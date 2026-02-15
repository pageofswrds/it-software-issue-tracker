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

export default router;
