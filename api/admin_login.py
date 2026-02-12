from http.server import BaseHTTPRequestHandler
import json
import base64
import os

# server-side config import
try:
    from config import ADMIN_USERNAME, ADMIN_PASSWORD
except Exception:
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1542')

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(content_length)
        try:
            creds = json.loads(data.decode('utf-8'))
        except Exception:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
            return

        username = (creds.get('username') or '').strip()
        password = creds.get('password') or ''

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            token = base64.b64encode(f"{username}:{password}".encode('utf-8')).decode('utf-8')
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'token': token}).encode('utf-8'))
        else:
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid credentials'}).encode('utf-8'))