from http.server import BaseHTTPRequestHandler
import json
import base64
import os

try:
    from database import get_connection, return_connection
    from config import ADMIN_USERNAME, ADMIN_PASSWORD
except ImportError:
    import sys
    sys.path.append('..')
    from database import get_connection, return_connection
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
    def do_POST(self):
        if not check_basic_auth(self.headers):
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Unauthorized: admin credentials required'}).encode('utf-8'))
            return

        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("TRUNCATE TABLE contacts RESTART IDENTITY CASCADE")
                conn.commit()
                cur.close()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'message': 'All contacts deleted and reset successfully'}).encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': f'Error truncating contacts: {str(e)}'}).encode('utf-8'))
            finally:
                return_connection(conn)
        else:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Database connection failed'}).encode('utf-8'))