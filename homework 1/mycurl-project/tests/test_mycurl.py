import base64
import http.server
import pathlib
import subprocess
import sys
import tempfile
import threading
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'mycurl.py'


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/redirect':
            self.send_response(302)
            self.send_header('Location', '/ok')
            self.end_headers()
            return
        self.send_response(200 if self.path == '/ok' else 404)
        self.send_header('Content-Length', '2')
        self.end_headers()
        self.wfile.write(b'OK')

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Length', '2')
        self.end_headers()

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        auth = self.headers.get('Authorization', '')
        self.send_response(200)
        self.end_headers()
        self.wfile.write(data + b'|' + auth.encode())

    def log_message(self, *args):
        pass


class ClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def run_client(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True)

    def test_get_and_http_error(self):
        self.assertEqual(self.run_client(self.base + '/ok').stdout, b'OK')
        self.assertEqual(self.run_client(self.base + '/missing').returncode, 0)

    def test_redirect_and_head(self):
        self.assertIn(b'302', self.run_client('-i', self.base + '/redirect').stdout)
        self.assertEqual(self.run_client('-L', self.base + '/redirect').stdout, b'OK')
        response = self.run_client('-I', self.base + '/ok')
        self.assertIn(b'Content-Length: 2', response.stdout)
        self.assertTrue(response.stdout.endswith(b'\r\n\r\n'))

    def test_post_auth_and_output(self):
        token = base64.b64encode(b'a:b')
        response = self.run_client('-d', 'x=1', '-u', 'a:b', self.base + '/post')
        self.assertEqual(response.stdout, b'x=1|Basic ' + token)
        with tempfile.TemporaryDirectory() as directory:
            output = str(pathlib.Path(directory) / 'out.bin')
            response = self.run_client('-o', output, self.base + '/ok')
            self.assertEqual(response.returncode, 0)
            self.assertEqual(pathlib.Path(output).read_bytes(), b'OK')


if __name__ == '__main__':
    unittest.main()
