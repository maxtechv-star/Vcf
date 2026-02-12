from http.server import BaseHTTPRequestHandler
import json
import base64
import os

try:
    from database import get_connection, return_connection
except ImportError:
    import sys
    sys.path.append('..')
    from database import get_connection, return_connection

# Load admin credentials
try:
    from config import ADMIN_USERNAME, ADMIN_PASSWORD
except Exception:
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1542')

def check_basic_auth(headers):
    auth = headers.get('Authorization', '')
    if not auth or not auth.startswith('Basic '):
        return False
    try:
        token = auth.split(' ', 1)[1]
        decoded = base64.b64decode(token).decode('utf-8')
        user, pwd = decoded.split(':', 1)
        return user == ADMIN_USERNAME and pwd == ADMIN_PASSWORD
    except Exception:
        return False

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Admin-only read settings
        if not check_basic_auth(self.headers):
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Unauthorized'}).encode('utf-8'))
            return

        conn = get_connection()
        if not conn:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Database connection failed'}).encode('utf-8'))
            return

        try:
            cur = conn.cursor()
            cur.execute("SELECT key, value FROM settings")
            rows = cur.fetchall()
            cur.close()
            settings = {k: v for k, v in rows}
            adding_enabled = settings.get('adding_enabled', 'true').lower() in ('1', 'true', 'yes')
            goal = int(settings.get('goal', '1000'))
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'adding_enabled': adding_enabled,
                'goal': goal
            }).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        finally:
            return_connection(conn)

    def do_POST(self):
        # Admin-only update settings
        if not check_basic_auth(self.headers):
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Unauthorized'}).encode('utf-8'))
            return

        content_length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(content_length)
        try:
            payload = json.loads(data.decode('utf-8'))
        except Exception:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Invalid JSON'}).encode('utf-8'))
            return

        conn = get_connection()
        if not conn:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Database connection failed'}).encode('utf-8'))
            return

        try:
            cur = conn.cursor()
            # Allowed updates: adding_enabled (bool) and goal (int)
            if 'adding_enabled' in payload:
                val = 'true' if bool(payload['adding_enabled']) else 'false'
                cur.execute("""
                    INSERT INTO settings (key, value) VALUES ('adding_enabled', %s)
                    ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                """, (val,))
            if 'goal' in payload:
                try:
                    g = int(payload['goal'])
                    cur.execute("""
                        INSERT INTO settings (key, value) VALUES ('goal', %s)
                        ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
                    """, (str(g),))
                except Exception:
                    pass
            conn.commit()
            cur.close()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Settings updated'}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
        finally:
            return_connection(conn)