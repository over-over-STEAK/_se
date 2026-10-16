const express = require('express');
const { Pool } = require('pg');
const app = express();
const pool = new Pool({ connectionTimeoutMillis: 3000, query_timeout: 5000 });
pool.on('error', err => console.error('Idle database connection:', err.message));
app.use(express.json({ limit: '8kb' }));
app.get('/health', async (req, res, next) => {
  try { await pool.query('SELECT 1'); res.json({service:'node-api', status:'ok', database:'connected'}); }
  catch (err) { next(err); }
});
app.get('/messages', async (req, res, next) => {
  try { const result = await pool.query('SELECT * FROM messages ORDER BY id DESC LIMIT 100'); res.json(result.rows); }
  catch (err) { next(err); }
});
app.post('/messages', async (req, res, next) => {
  const content = req.body?.content;
  if (typeof content !== 'string' || !content.trim() || [...content.trim()].length > 200)
    return res.status(400).json({error:'留言必須為 1～200 字的文字'});
  try {
    const result = await pool.query('INSERT INTO messages(content) VALUES ($1) RETURNING *', [content.trim()]);
    res.status(201).json(result.rows[0]);
  } catch (err) { next(err); }
});
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') return res.status(400).json({error:'JSON 格式錯誤'});
  if (err.type === 'entity.too.large') return res.status(413).json({error:'請求內容太大'});
  console.error(err.message);
  res.status(503).json({error:'資料庫暫時無法使用'});
});
app.listen(3000, '0.0.0.0', () => console.log('node-api listening on 3000'));
