CREATE TABLE IF NOT EXISTS messages (
  id SERIAL PRIMARY KEY,
  content VARCHAR(200) NOT NULL CHECK (length(trim(content)) > 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO messages (content) VALUES ('歡迎使用 Docker 微服務展示系統！');
