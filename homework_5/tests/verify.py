"""Run after docker compose up. Uses Python standard library only."""
import json
import sys
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError

base = sys.argv[1].rstrip('/') if len(sys.argv) > 1 else 'http://localhost:8080'

def request(path, body=None):
    data = None if body is None else json.dumps(body).encode('utf-8')
    req = Request(base + path, data=data, headers={'Content-Type': 'application/json'})
    with urlopen(req, timeout=10) as response:
        return response.status, json.load(response)

with urlopen(base, timeout=10) as response:
    assert response.status == 200 and b'Docker' in response.read()
print('PASS: Nginx serves the web page')
for service in ('node', 'python'):
    _, health = request(f'/api/{service}/health')
    assert health['status'] == 'ok' and health['database'] == 'connected'
    print(f'PASS: {service} API and database connection')
_, before = request('/api/python/stats')
message = 'Docker verification ' + uuid.uuid4().hex[:8]
status, created = request('/api/node/messages', {'content': message})
assert status == 201 and created['content'] == message
_, messages = request('/api/node/messages')
assert any(m['id'] == created['id'] and m['content'] == message for m in messages)
_, after = request('/api/python/stats')
assert after['total_messages'] >= before['total_messages'] + 1
print('PASS: Node write -> PostgreSQL -> Python statistics')
for invalid in ('', '   ', 'x' * 201, 123):
    try:
        request('/api/node/messages', {'content': invalid})
        raise AssertionError('Invalid content was accepted')
    except HTTPError as error:
        assert error.code == 400
print('PASS: Invalid input rejected')
print(f'All checks passed. Test message retained: id={created["id"]}')
