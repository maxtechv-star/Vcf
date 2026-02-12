from http.server import BaseHTTPRequestHandler
import json

try:
    from database import get_connection, return_connection
except ImportError:
    import sys
    sys.path.append('..')
    from database import get_connection, return_connection

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
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
            # Normalize types
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