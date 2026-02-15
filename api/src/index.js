import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import applicationsRouter from './routes/applications.js';
import issuesRouter from './routes/issues.js';
import searchRouter from './routes/search.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/applications', applicationsRouter);
app.use('/api/issues', issuesRouter);
app.use('/api/search', searchRouter);

app.listen(PORT, () => {
  console.log(`API server running on http://localhost:${PORT}`);
});
