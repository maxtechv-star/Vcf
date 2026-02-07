# api/add_contact.py
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse as urlparse
from urllib.parse import parse_qs
import base64
import os
import re

# Import database module
try:
    from database import get_connection, return_connection
except ImportError:
    import sys
    sys.path.append('..')
    from database import get_connection, return_connection

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve assets (logo) when requested
        if self.path.startswith('/assets/'):
            asset_path = self.path.lstrip('/')
            # For now only serve assets/logo.png to keep it simple
            if asset_path == 'assets/logo.png':
                try:
                    with open(asset_path, 'rb') as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(data)
                    return
                except FileNotFoundError:
                    # Fallback placeholder
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Logo not found. Upload assets/logo.png')
                    return

        # Serve main public HTML (dark / black theme)
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>STATUS VIEWS CENTRE - Contact Manager</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                /* Dark / black theme */
                :root{
                    --bg: #070707;
                    --card: #0f1111;
                    --muted: #b9b9bd;
                    --accent: #f0c000; /* gold accent */
                    --accent-2: #ff6b6b; /* red for danger */
                    --primary: #ffffff;
                    --input-bg: #111315;
                    --border: #222425;
                    --success: #26a69a;
                }
                html,body{height:100%}
                body {
                    margin: 0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(180deg, #000 0%, #070707 100%);
                    color: var(--primary);
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    padding:20px;
                }
                .container {
                    width:100%;
                    max-width:760px;
                    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
                    border-radius:12px;
                    box-shadow: 0 12px 40px rgba(0,0,0,0.8);
                    padding:20px;
                    border: 1px solid rgba(255,255,255,0.03);
                }
                .header { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:16px; }
                .logo { display:flex; align-items:center; gap:12px; }
                .logo img { width:56px; height:56px; border-radius:8px; object-fit:cover; border:1px solid rgba(255,255,255,0.04); background:linear-gradient(180deg,#0b0b0b,#141414); }
                h1 { margin:0; font-size:1.25rem; color:var(--primary); letter-spacing:0.3px; }
                .subtitle { color:var(--muted); font-size:0.9rem; margin-top:2px; }

                .admin-btn { background:transparent; color:var(--primary); padding:8px 12px; border-radius:8px; border:1px solid rgba(255,255,255,0.04); cursor:pointer; font-weight:600; }
                .form-container { background:var(--card); border-radius:10px; padding:18px; margin-bottom:16px; border:1px solid var(--border); }
                .input { width:100%; padding:12px; border-radius:10px; border:1px solid var(--border); margin-bottom:12px; background:var(--input-bg); color:var(--primary); }
                .input::placeholder { color: rgba(255,255,255,0.35); }
                .btn-primary { background: linear-gradient(90deg, var(--accent), #ffb84d); color:#0b0b0b; padding:12px; border-radius:10px; border:none; width:100%; cursor:pointer; font-weight:700; box-shadow: 0 6px 18px rgba(240,192,0,0.12); }
                .btn-primary:active{ transform: translateY(1px); }
                .join-btn { display:flex; align-items:center; gap:12px; background:transparent; border:1px solid rgba(255,255,255,0.03); padding:10px; border-radius:10px; text-decoration:none; color:var(--primary); width:100%; margin-top:10px; }
                .join-btn img { width:40px; height:40px; border-radius:8px; object-fit:cover; }
                .note { font-size:0.95rem; color:var(--muted); margin-top:8px; }
                .stats { display:flex; gap:8px; justify-content:space-between; margin-top:14px; padding-top:10px; border-top:1px solid rgba(255,255,255,0.02); }
                .stat { text-align:center; flex:1; }
                .stat .num { font-size:1.4rem; color:var(--accent); font-weight:800; }
                .message { padding:10px; border-radius:8px; display:none; margin-bottom:10px; }
                .message.success { background: rgba(38,166,154,0.08); color: var(--success); display:block; }
                .message.error { background: rgba(255,107,107,0.08); color: var(--accent-2); display:block; }

                footer { text-align:center; color:var(--muted); font-size:0.85rem; margin-top:12px; }

                @media (max-width:720px){
                    .container{ padding:14px }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">
                        <img src="/assets/logo.png" alt="logo" />
                        <div>
                            <h1>STATUS VIEWS CENTRE</h1>
                            <div class="subtitle">VCF Contact Management System</div>
                        </div>
                    </div>
                    <div>
                        <button id="adminPanelBtn" class="admin-btn">Admin</button>
                    </div>
                </div>

                <div id="message" class="message"></div>

                <div class="form-container">
                    <form id="contactForm">
                        <input id="name" class="input" type="text" placeholder="Full Name (e.g., John Doe)" required />
                        <input id="phone" class="input" type="tel" placeholder="Phone number (e.g., +256784670936 or +1234567890)" required />
                        <button type="submit" class="btn-primary">+ Add Contact</button>
                    </form>

                    <a class="join-btn" id="joinGroup" href="https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa" target="_blank" rel="noopener">
                        <img src="/assets/logo.png" alt="group" />
                        <div>
                            <div style="font-weight:700">Join WhatsApp Group</div>
                            <div style="font-size:0.85rem;color:var(--muted)">Tap to join — VCF will be dropped in this group</div>
                        </div>
                    </a>
                    <div class="note">Phone numbers from any country are accepted. Example: +256784670936, +1234567890, +442071838750</div>
                </div>

                <div class="stats">
                    <div class="stat">
                        <div class="num" id="contactCount">0</div>
                        <div>Contacts</div>
                    </div>
                    <div class="stat">
                        <div class="num" id="todayCount">0</div>
                        <div>Today</div>
                    </div>
                    <div class="stat">
                        <div class="num" id="remainingCount">1000</div>
                        <div>Remaining to 1000</div>
                    </div>
                </div>

                <footer>© 2026 STATUS VIEWS CENTRE. All rights reserved.</footer>
            </div>

            <script>
                const GOAL = 1000;

                document.getElementById('adminPanelBtn').addEventListener('click', function(){
                    window.location.href = '/admin_panel';
                });

                async function loadStats(){
                    try{
                        const r = await fetch('/contacts');
                        const data = await r.json();
                        if (data && data.success){
                            document.getElementById('contactCount').textContent = data.count;
                            const today = new Date().toISOString().split('T')[0];
                            const todayCount = data.contacts.filter(c => c.created_at && c.created_at.startsWith(today)).length;
                            document.getElementById('todayCount').textContent = todayCount;
                            document.getElementById('remainingCount').textContent = Math.max(GOAL - data.count, 0);
                        }
                    }catch(e){ console.error(e); }
                }

                document.getElementById('contactForm').addEventListener('submit', async function(e){
                    e.preventDefault();
                    const name = document.getElementById('name').value.trim();
                    const phoneRaw = document.getElementById('phone').value.trim();
                    if (!name || !phoneRaw){ showMessage('Fill all fields', 'error'); return; }
                    const phone = phoneRaw.replace(/\\D/g, '');
                    if (!phone){ showMessage('Phone number must contain digits', 'error'); return; }
                    try{
                        const res = await fetch('/add', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ name, phone })
                        });
                        const json = await res.json();
                        if (res.ok){ showMessage(json.message || 'Contact added', 'success'); document.getElementById('contactForm').reset(); loadStats(); }
                        else { showMessage(json.error || 'Error adding', 'error'); }
                    }catch(err){ console.error(err); showMessage('Network error', 'error'); }
                });

                function showMessage(text, type){
                    const el = document.getElementById('message');
                    el.textContent = text;
                    el.className = 'message ' + (type === 'success' ? 'success' : 'error');
                    setTimeout(()=>{ el.className = 'message'; el.textContent = ''; }, 6000);
                }

                loadStats();
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def do_POST(self):
        # Contact creation (server-side checks, no country restriction)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
        except Exception:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
            return

        name = (data.get('name', '') or '').strip()
        phone_raw = (data.get('phone', '') or '').strip()
        phone = re.sub(r'\\D', '', phone_raw)  # digits only

        if not name or not phone:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Name and phone are required'}).encode('utf-8'))
            return

        # No country restriction — accept any phone number with digits
        conn = get_connection()
        if conn:
            try:
                cur = conn.cursor()
                # Check duplicates by phone or name (case-insensitive)
                cur.execute("SELECT id, name FROM contacts WHERE phone = %s OR LOWER(name) = LOWER(%s)", (phone, name))
                existing = cur.fetchone()
                if existing:
                    self.send_response(409)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    msg = 'Duplicate contact: '
                    if existing[1] and existing[1].lower() == name.lower():
                        msg += 'A contact with this name already exists.'
                    else:
                        msg += 'A contact with this phone already exists.'
                    self.wfile.write(json.dumps({'error': msg}).encode('utf-8'))
                    cur.close()
                    return

                cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s) RETURNING id", (name, phone))
                contact_id = cur.fetchone()[0]
                conn.commit()
                cur.close()

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': f'Contact \"{name}\" added successfully!',
                    'contact_id': contact_id,
                    'contact': {'name': name, 'phone': phone}
                }).encode('utf-8'))

            except Exception as e:
                errstr = str(e)
                if 'uq_contacts_phone' in errstr or 'uq_contacts_name_lower' in errstr or 'duplicate key' in errstr.lower():
                    self.send_response(409)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Duplicate contact (phone or name)'}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'error': f'Database error: {str(e)}'}).encode('utf-8'))
            finally:
                return_connection(conn)
        else:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Database connection failed'}).encode('utf-8'))