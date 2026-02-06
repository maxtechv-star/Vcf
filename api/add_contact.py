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
    # For local testing
    import sys
    sys.path.append('..')
    from database import get_connection, return_connection

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve HTML with public UI; admin login is a small button (no hard-coded password)
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>STATUS VIEWS CENTRE - Contact Manager</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                /* styles (same as before) */
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg,#2c3e50 0%,#3498db 100%); min-height:100vh; padding:20px; color:#2c3e50; display:flex; justify-content:center; align-items:center;}
                .container { background:white; border-radius:20px; padding:30px; width:100%; max-width:720px; box-shadow:0 20px 40px rgba(0,0,0,0.2);}
                .header { display:flex; justify-content:space-between; align-items:center; gap:10px; margin-bottom:20px;}
                .logo { display:flex; align-items:center; gap:12px;}
                .logo img { width:56px; height:56px; border-radius:8px; object-fit:cover; }
                h1 { font-size:1.4rem; margin:0; color:#2c3e50;}
                .admin-btn { background:#2c3e50; color:white; padding:8px 12px; border-radius:8px; border:none; cursor:pointer; }
                .form-container { background:#f3f6f8; padding:18px; border-radius:12px; margin-bottom:18px;}
                .input { width:100%; padding:12px; border-radius:8px; border:1px solid #e0e6ea; margin-bottom:12px; }
                .btn-primary { background:linear-gradient(135deg,#3498db,#2c3e50); color:white; padding:12px; border-radius:10px; border:none; width:100%; cursor:pointer; font-weight:600;}
                .join-btn { display:flex; align-items:center; gap:10px; background:#fff; border:1px solid #e0e6ea; padding:10px; border-radius:10px; text-decoration:none; color:#2c3e50; width:100%; }
                .join-btn img { width:36px; height:36px; border-radius:6px; }
                .note { font-size:0.95rem; color:#7f8c8d; margin-top:8px;}
                .stats { display:flex; gap:8px; justify-content:space-between; margin-top:14px; padding-top:10px; border-top:1px solid #e6eef5;}
                .stat { text-align:center; flex:1; }
                .stat .num { font-size:1.4rem; color:#3498db; font-weight:700; }
                .admin-panel { display:none; margin-top:12px; }
                .admin-panel .btn-danger { background:#c0392b; color:white; border:none; padding:10px; border-radius:8px; width:100%; cursor:pointer; }
                .message { padding:10px; border-radius:8px; display:none; margin-bottom:10px; }
                .message.success { background:#d5f4e6; color:#27ae60; display:block; }
                .message.error { background:#ffeaa7; color:#f39c12; display:block; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">
                        <img src="/assets/logo.png" alt="logo" />
                        <div>
                            <h1>STATUS VIEWS CENTRE</h1>
                            <div style="font-size:0.9rem;color:#7f8c8d;">VCF Contact Management System</div>
                        </div>
                    </div>
                    <div>
                        <button id="adminToggle" class="admin-btn">Admin</button>
                    </div>
                </div>

                <div id="message" class="message"></div>

                <div class="form-container">
                    <form id="contactForm">
                        <input id="name" class="input" type="text" placeholder="Full Name (e.g., Uthuman)" required />
                        <input id="phone" class="input" type="tel" placeholder="Phone number (e.g., 256784670936)" required />
                        <button type="submit" class="btn-primary">+ Add Contact</button>
                    </form>

                    <a class="join-btn" id="joinGroup" href="https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa" target="_blank" rel="noopener">
                        <img src="/assets/logo.png" alt="group" />
                        <div>
                            <div style="font-weight:600">Join WhatsApp Group</div>
                            <div style="font-size:0.85rem;color:#7f8c8d">Tap to join the group — VCF will be dropped in the group</div>
                        </div>
                    </a>
                    <div class="note">Only Ugandan numbers allowed (must start with <strong>256</strong>). Example: <code>256784670936</code></div>
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

                <div id="adminPanel" class="admin-panel">
                    <div style="margin-bottom:8px;">
                        <button id="downloadBtn" class="btn-primary" style="background:linear-gradient(135deg,#e74c3c,#c0392b);">⭳ Download VCF (Admin only)</button>
                    </div>
                    <div>
                        <button id="resetBtn" class="btn-danger">🗑 Reset / Delete All Contacts (Admin only)</button>
                    </div>
                </div>
            </div>

            <script>
                const GOAL = 1000;
                let ADMIN_AUTH = null; // Basic token (base64) stored in memory only
                const ADMIN_USER = 'admin'; // user label used when building Basic token on client side

                // Load stats
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
                    if (!phone.startsWith('256')){ showMessage('Only Ugandan numbers allowed (start with 256).', 'error'); return; }
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

                // Admin toggle: show password prompt and set ADMIN_AUTH (in-memory)
                document.getElementById('adminToggle').addEventListener('click', async function(){
                    const pwd = prompt('Enter admin password (server-side):');
                    if (!pwd) return;
                    // Build Basic auth value
                    try {
                        const token = btoa(ADMIN_USER + ':' + pwd);
                        // quick validation: call a small admin-only endpoint to verify (use /download HEAD or /admin/reset with OPTIONS? we'll use a lightweight /admin/validate endpoint if available)
                        // Here we attempt a harmless HEAD to /download to check auth (server will return 401 or 200). We use GET but we will not download content unless authorized.
                        const r = await fetch('/download', {
                            method: 'GET',
                            headers: { 'Authorization': 'Basic ' + token }
                        });
                        if (r.status === 200){
                            ADMIN_AUTH = token;
                            document.getElementById('adminPanel').style.display = 'block';
                            showMessage('Admin authenticated', 'success');
                        } else {
                            showMessage('Invalid admin credentials', 'error');
                        }
                    } catch(e){
                        console.error(e);
                        showMessage('Admin authentication failed', 'error');
                    }
                });

                // Download VCF (admin only)
                document.getElementById('downloadBtn').addEventListener('click', async function(){
                    if (!ADMIN_AUTH){ showMessage('Please authenticate as admin first', 'error'); return; }
                    try {
                        const r = await fetch('/download', {
                            method: 'GET',
                            headers: { 'Authorization': 'Basic ' + ADMIN_AUTH }
                        });
                        if (r.ok) {
                            const blob = await r.blob();
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = 'contacts.vcf';
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                            window.URL.revokeObjectURL(url);
                            showMessage('VCF downloaded (admin)', 'success');
                        } else {
                            const j = await r.json();
                            showMessage(j && j.error ? j.error : 'Download failed', 'error');
                        }
                    } catch (e) { console.error(e); showMessage('Download failed', 'error'); }
                });

                // Reset (admin only)
                document.getElementById('resetBtn').addEventListener('click', async function(){
                    if (!ADMIN_AUTH){ showMessage('Please authenticate as admin first', 'error'); return; }
                    if (!confirm('This will permanently delete ALL contacts and reset IDs. Are you sure?')) return;
                    try {
                        const r = await fetch('/admin/reset', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json', 'Authorization': 'Basic ' + ADMIN_AUTH },
                            body: JSON.stringify({})
                        });
                        const j = await r.json();
                        if (r.ok) { showMessage(j.message || 'Reset done', 'success'); loadStats(); }
                        else { showMessage(j.error || 'Reset failed', 'error'); }
                    } catch (e) { console.error(e); showMessage('Reset failed', 'error'); }
                });

                function showMessage(text, type){
                    const el = document.getElementById('message');
                    el.textContent = text;
                    el.className = 'message ' + (type === 'success' ? 'success' : 'error');
                    setTimeout(()=>{ el.className = 'message'; el.textContent = ''; }, 6000);
                }

                // init
                loadStats();
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
        return

    # do_POST unchanged (re-use previous server-side validation/duplicate checks)
    def do_POST(self):
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

        # Enforce Ugandan phone numbers (must start with 256)
        if not phone.startswith('256'):
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Only Ugandan numbers are allowed (must start with 256)'}).encode('utf-8'))
            return
        
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

                cur.execute(
                    "INSERT INTO contacts (name, phone) VALUES (%s, %s) RETURNING id",
                    (name, phone)
                )
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
                    self.wfile.write(json.dumps({
                        'success': False,
                        'error': f'Database error: {str(e)}'
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