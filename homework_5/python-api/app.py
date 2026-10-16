import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException

app = FastAPI(title='Docker Statistics Service')

def query(sql):
    try:
        with psycopg.connect(connect_timeout=3, row_factory=dict_row,
                             options='-c statement_timeout=5000') as conn:
            return conn.execute(sql).fetchone()
    except psycopg.Error as exc:
        print(f'Database error: {type(exc).__name__}', flush=True)
        raise HTTPException(status_code=503, detail='資料庫暫時無法使用') from exc

@app.get('/health')
def health():
    query('SELECT 1')
    return {'service': 'python-api', 'status': 'ok', 'database': 'connected'}

@app.get('/stats')
def stats():
    return {'service': 'python-api', **query(
        'SELECT COUNT(*) AS total_messages, MAX(created_at) AS latest_message_at FROM messages')}
