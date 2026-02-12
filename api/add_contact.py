# api/add_contact.py
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import mimetypes

# Import database module
try:
    from database import get_connection, return_connection
except ImportError:
    import sys
    sys.path.append('..')
    from database import get_connection, return_connection

ASSETS_DIR = 'assets'

def safe_asset_path(request_path):
    p = request_path.lstrip('/')
    norm = os.path.normpath(p)
    if not norm.startswith(ASSETS_DIR + os.sep) and norm != ASSETS_DIR:
        return None
    full = os.path.abspath(norm)
    assets_root = os.path.abspath(ASSETS_DIR)
    if not full.startswith(assets_root):
        return None
    return full

def get_setting(conn, key, default=None):
    cur = conn.cursor()
    try:
        cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
        row = cur.fetchone()
        return row[0] if row else default
    finally:
        cur.close()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve asset files under /assets/
        if self.path.startswith('/assets/'):
            full = safe_asset_path(self.path)
            if not full or not os.path.exists(full):
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Asset not found')
                return
            mimetype, _ = mimetypes.guess_type(full)
            if mimetype is None:
                mimetype = 'application/octet-stream'
            try:
                with open(full, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.send_header('Cache-Control', 'public, max-age=86400')
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Error reading asset')
                return

        # Serve main public HTML (dark / black theme with join & settings enforcement)
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>STATUS VIEWS CENTRE - Contact Manager</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root{--bg:#070707;--card:#0f1111;--muted:#b9b9bd;--accent:#f0c000;--accent-2:#ff6b6b;--primary:#ffffff;--input-bg:#111315;--border:#222425;--success:#26a69a}
html,body{height:100%}body{margin:0;font-family:'Segoe UI',Tahoma, Geneva, Verdana, sans-serif;background:linear-gradient(180deg,#000,#070707);color:var(--primary);display:flex;align-items:center;justify-content:center;padding:20px}
.container{width:100%;max-width:760px;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));border-radius:12px;box-shadow:0 12px 40px rgba(0,0,0,0.8);padding:20px;border:1px solid rgba(255,255,255,0.03)}
.header{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:16px}
.logo{display:flex;align-items:center;gap:12px}.logo img{width:56px;height:56px;border-radius:8px}
.subtitle{color:var(--muted);font-size:0.9rem;margin-top:2px}
.admin-btn{background:transparent;color:var(--primary);padding:8px 12px;border-radius:8px;border:1px solid rgba(255,255,255,0.04);cursor:pointer;font-weight:600}
.form-container{background:var(--card);border-radius:10px;padding:18px;margin-bottom:16px;border:1px solid var(--border)}
.input{width:100%;padding:12px;border-radius:10px;border:1px solid var(--border);margin-bottom:12px;background:var(--input-bg);color:var(--primary)}
.input::placeholder{color:rgba(255,255,255,0.35)}
.btn-primary{background:linear-gradient(90deg,var(--accent),#ffb84d);color:#0b0b0b;padding:12px;border-radius:10px;border:none;width:100%;cursor:pointer;font-weight:700;box-shadow:0 6px 18px rgba(240,192,0,0.12)}
.btn-primary:disabled{opacity:0.5;cursor:not-allowed}
.join-btn{display:flex;align-items:center;gap:12px;background:transparent;border:1px solid rgba(255,255,255,0.03);padding:10px;border-radius:10px;text-decoration:none;color:var(--primary);width:100%;margin-top:10px}
.join-btn img{width:40px;height:40px;border-radius:8px;object-fit:cover}
.note{font-size:0.95rem;color:var(--muted);margin-top:8px}
.stats{display:flex;gap:8px;justify-content:space-between;margin-top:14px;padding-top:10px;border-top:1px solid rgba(255,255,255,0.02)}
.stat{text-align:center;flex:1}.stat .num{font-size:1.4rem;color:var(--accent);font-weight:800}
.message{padding:10px;border-radius:8px;display:none;margin-bottom:10px}
.message.success{background:rgba(38,166,154,0.08);color:var(--success);display:block}
.message.error{background:rgba(255,107,107,0.08);color:var(--accent-2);display:block}
.message.warning{background:rgba(240,192,0,0.08);color:var(--accent);display:block}
.join-screen{display:none;text-align:center;padding:20px 0}.join-screen.active{display:block}
.join-icon{font-size:3rem;color:var(--accent);margin-bottom:10px}.join-heading{font-size:1.1rem;font-weight:700;margin-bottom:8px}
.join-text{color:var(--muted);margin-bottom:16px}
.form-section{display:none}.form-section.active{display:block}
footer{text-align:center;color:var(--muted);font-size:0.85rem;margin-top:12px}
@media (max-width:720px){.container{padding:14px}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="logo">
      <img src="/assets/logo.png" alt="logo" />
      <div>
        <div style="font-weight:800">STATUS VIEWS CENTRE</div>
        <div class="subtitle">VCF Contact Management System</div>
      </div>
    </div>
    <div>
      <button id="adminPanelBtn" class="admin-btn">Admin</button>
    </div>
  </div>

  <div id="message" class="message"></div>

  <div id="joinScreen" class="form-container join-screen active">
    <div class="join-icon"><i class="fas fa-lock"></i></div>
    <div class="join-heading">Join Our Community</div>
    <div class="join-text">To add contacts and download the VCF file, you must first join our WhatsApp group.</div>

    <a id="joinGroupBtn" class="join-btn" href="https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa" target="_blank" rel="noopener">
      <img src="/assets/logo.png" alt="group" />
      <div>
        <div style="font-weight:700">Join WhatsApp Group</div>
        <div style="font-size:0.85rem;color:var(--muted)">Click to join the group</div>
      </div>
    </a>

    <div style="margin-top:20px;padding:12px;background:rgba(38,166,154,0.08);border-radius:8px;">
      <div style="font-size:0.9rem;color:var(--muted);margin-bottom:6px;">After joining:</div>
      <button id="confirmedJoinBtn" class="btn-primary" style="background:linear-gradient(90deg,var(--success),#2a9d8f)">✓ I've Joined the Group</button>
    </div>

    <div class="note">Once you join the group, come back and click "I've Joined" to unlock the form.</div>
  </div>

  <div id="formSection" class="form-section">
    <div class="form-container">
      <form id="contactForm">
        <input id="name" class="input" type="text" placeholder="Full Name (e.g., John Doe)" required />
        <input id="phone" class="input" type="tel" placeholder="Phone with country code (e.g., +256784670936)" required />
        <button id="addBtn" type="submit" class="btn-primary">+ Add Contact</button>
      </form>

      <a id="joinGroupLink" class="join-btn" href="https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa" target="_blank" rel="noopener">
        <img src="/assets/logo.png" alt="group" />
        <div>
          <div style="font-weight:700">Join WhatsApp Group</div>
          <div style="font-size:0.85rem;color:var(--muted)">Tap to join — VCF will be dropped in this group</div>
        </div>
      </a>
      <div class="note">Phone numbers must include country code. Examples: <strong>+256784670936</strong>, <strong>+1234567890</strong>, <strong>+442071838750</strong></div>
    </div>

    <div class="stats">
      <div class="stat"><div class="num" id="contactCount">0</div><div>Contacts</div></div>
      <div class="stat"><div class="num" id="todayCount">0</div><div>Today</div></div>
      <div class="stat"><div class="num" id="remainingCount">1000</div><div>Remaining to goal</div></div>
    </div>
  </div>

  <footer>© 2026 STATUS VIEWS CENTRE. All rights reserved.</footer>
</div>

<!-- audio element -->
<audio id="contractAudio" preload="none"></audio>

<script>
const GOAL_KEY = 'STATUS_VIEWS_GOAL';
const GROUP_JOINED_KEY = 'STATUS_VIEWS_GROUP_JOINED';
let ADDING_ENABLED = true;
let GOAL = 1000;

async function loadSettingsPublic() {
  try {
    const r = await fetch('/settings');
    if (r.ok) {
      const j = await r.json();
      ADDING_ENABLED = !!j.adding_enabled;
      GOAL = j.goal || 1000;
      document.getElementById('remainingCount').textContent = Math.max(GOAL - (document.getElementById('contactCount').textContent || 0), 0);
      const addBtn = document.getElementById('addBtn');
      if (!ADDING_ENABLED) {
        addBtn.disabled = true;
        showMessage('Adding numbers is currently unavailable as for now join the group for further information. Also if you leave the group you will not get views', 'warning');
      } else {
        addBtn.disabled = false;
      }
    }
  } catch (e) {
    console.warn('Could not load settings', e);
  }
}

function hasJoinedGroup() {
  return localStorage.getItem(GROUP_JOINED_KEY) === 'true';
}

async function playJoinAudio() {
  const audio = document.getElementById('contractAudio');
  audio.src = '/assets/sign_the_contract.mp3';
  audio.volume = 1.0;
  try {
    audio.currentTime = 0;
    const p = audio.play();
    if (p && p.then) { await p; }
  } catch (err) {
    console.warn('Join audio failed:', err);
  }
}

async function markAsJoined() {
  await playJoinAudio().catch(()=>{});
  localStorage.setItem(GROUP_JOINED_KEY, 'true');
  showFormSection();
  showMessage('✅ Welcome! You can now add contacts.', 'success');
}

function showFormSection() {
  document.getElementById('joinScreen').classList.remove('active');
  document.getElementById('formSection').classList.add('active');
  loadStats();
  loadSettingsPublic();
}

function showJoinScreen() {
  document.getElementById('formSection').classList.remove('active');
  document.getElementById('joinScreen').classList.add('active');
}

if (hasJoinedGroup()) {
  showFormSection();
} else {
  showJoinScreen();
}

document.getElementById('confirmedJoinBtn').addEventListener('click', markAsJoined);
document.getElementById('adminPanelBtn').addEventListener('click', ()=>{ window.location.href = '/admin_panel'; });

async function loadStats(){
  try{
    const r = await fetch('/contacts');
    const data = await r.json();
    if (data && data.success){
      document.getElementById('contactCount').textContent = data.count;
      const today = new Date().toISOString().split('T')[0];
      const todayCount = data.contacts.filter(c => c.created_at && c.created_at.startsWith(today)).length;
      document.getElementById('todayCount').textContent = todayCount;
      const remaining = Math.max(GOAL - data.count, 0);
      document.getElementById('remainingCount').textContent = remaining;
      // enforce adding status fetched earlier
      await loadSettingsPublic();
    }
  }catch(e){ console.error(e); }
}

document.getElementById('contactForm').addEventListener('submit', async function(e){
  e.preventDefault();
  if (!ADDING_ENABLED) {
    showMessage('Adding numbers is currently unavailable as for now join the group for further information. Also if you leave the group you will not get views', 'warning');
    return;
  }

  const name = document.getElementById('name').value.trim();
  const phoneRaw = document.getElementById('phone').value.trim();

  if (!name || !phoneRaw){ showMessage('Fill all fields', 'error'); return; }

  if (!phoneRaw.startsWith('+')) {
    showMessage('Phone number must start with + and include country code (e.g., +256...)', 'error');
    return;
  }

  const phone = phoneRaw.replace(/\D/g, '');
  if (!phone || phone.length < 2) {
    showMessage('Phone number must include country code and at least one digit', 'error');
    return;
  }

  try{
    const res = await fetch('/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, phone })
    });
    const json = await res.json();
    if (res.ok){ showMessage(json.message || '✅ Contact added', 'success'); document.getElementById('contactForm').reset(); loadStats(); }
    else { showMessage(json.error || 'Error adding', 'error'); }
  }catch(err){ console.error(err); showMessage('Network error', 'error'); }
});

function showMessage(text, type){
  const el = document.getElementById('message');
  el.textContent = text;
  el.className = 'message ' + (type === 'success' ? 'success' : (type === 'error' ? 'error' : 'warning'));
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

    def do_POST(self):
        # Contact creation with server-side adding_enabled enforcement
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
        phone = re.sub(r'\D', '', phone_raw)

        if not name or not phone:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Name and phone are required'}).encode('utf-8'))
            return

        if len(phone) < 2:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Phone number must include a valid country code and number'}).encode('utf-8'))
            return

        conn = get_connection()
        if not conn:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': 'Database connection failed'}).encode('utf-8'))
            return

        try:
            # Server-side check: is adding enabled?
            adding_val = get_setting(conn, 'adding_enabled', 'true')
            if str(adding_val).lower() not in ('1', 'true', 'yes'):
                self.send_response(403)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'Adding numbers is currently unavailable as for now join the group for further information. Also if you leave the group you will not get views'
                }).encode('utf-8'))
                return

            cur = conn.cursor()
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