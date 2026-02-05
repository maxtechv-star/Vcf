from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta

try:
    from database import get_connection, return_connection
except ImportError:
    import sys
    sys.path.append('..')
    from database import get_connection, return_connection

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    SELECT id, name, phone, created_at 
                    FROM contacts 
                    ORDER BY created_at DESC
                """)
                contacts = cur.fetchall()
                cur.close()
                
                # Convert to list of dictionaries
                contacts_list = []
                for contact in contacts:
                    contacts_list.append({
                        'id': contact[0],
                        'name': contact[1],
                        'phone': contact[2],
                        'created_at': contact[3].isoformat() if contact[3] else None,
                        'date': contact[3].strftime('%Y-%m-%d') if contact[3] else None,
                        'time': contact[3].strftime('%H:%M:%S') if contact[3] else None
                    })
                
                # Calculate statistics
                today = datetime.now().date()
                today_str = today.isoformat()
                today_count = sum(1 for c in contacts_list if c.get('date') == today_str)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'count': len(contacts_list),
                    'today_count': today_count,
                    'contacts': contacts_list,
                    'generated_at': datetime.now().isoformat(),
                    'system': 'STATUS VIEWS CENTRE VCF Manager'
                }).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }).encode('utf-8'))
            finally:
                return_connection(conn)
        else:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Database connection failed'
            }).encode('utf-8'))