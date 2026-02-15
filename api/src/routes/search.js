// api/src/routes/search.js
import { Router } from 'express';
import { query } from '../db.js';
import OpenAI from 'openai';

const router = Router();

let openai = null;

function getOpenAIClient() {
  if (!openai) {
    openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }
  return openai;
}

// Search issues (semantic + keyword)
router.get('/', async (req, res) => {
  try {
    const { q, limit = 20 } = req.query;

    if (!q) {
      return res.status(400).json({ error: 'Query parameter q is required' });
    }

    // Generate embedding for query
    const embeddingResponse = await getOpenAIClient().embeddings.create({
      model: 'text-embedding-3-small',
      input: q
    });
    const queryEmbedding = embeddingResponse.data[0].embedding;

    // Semantic search with cosine similarity
    const parsedLimit = Math.min(Math.max(parseInt(limit) || 20, 1), 100);

    const issues = await query(`
      SELECT
        i.*,
        a.name as application_name,
        a.vendor,
        1 - (i.embedding <=> $1::vector) as similarity
      FROM issues i
      JOIN applications a ON a.id = i.application_id
      WHERE i.embedding IS NOT NULL
      ORDER BY i.embedding <=> $1::vector
      LIMIT $2
    `, [`[${queryEmbedding.join(',')}]`, parsedLimit]);

    res.json(issues);
  } catch (err) {
    console.error('Error searching:', err);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
