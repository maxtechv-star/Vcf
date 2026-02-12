from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        html = """
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width,initial-scale=1">
          <title>Admin Panel - STATUS VIEWS CENTRE</title>
          <style>
            :root{--bg:#070707;--card:#0f1111;--muted:#b9b9bd;--accent:#f0c000;--danger:#ff6b6b;--primary:#fff;--input:#111315;--border:#222425}
            body{margin:0;background:linear-gradient(180deg,#000,#070707);font-family:Arial,Helvetica,sans-serif;display:flex;align-items:flex-start;justify-content:center;padding:24px;color:var(--primary)}
            .card{width:100%;max-width:980px;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));padding:18px;border-radius:12px;border:1px solid rgba(255,255,255,0.03)}
            .top {display:flex;align-items:center;justify-content:space-between;gap:12px}
            .logo {display:flex;align-items:center;gap:12px}
            .logo img{width:56px;height:56px;border-radius:8px}
            .controls {margin-top:12px;display:flex;gap:12px;align-items:center}
            .btn{padding:10px 12px;border-radius:8px;border:none;cursor:pointer;font-weight:700}
            .btn.primary{background:linear-gradient(90deg,var(--accent),#ffb84d);color:#0b0b0b}
            .btn.danger{background:var(--danger);color:#0b0b0b}
            .field {display:flex;gap:8px;align-items:center}
            .input{padding:8px;border-radius:8px;background:var(--input);border:1px solid var(--border);color:var(--primary)}
            .section{margin-top:14px}
            table{width:100%;border-collapse:collapse;margin-top:10px}
            th,td{padding:8px;border-bottom:1px solid rgba(255,255,255,0.03);text-align:left}
            th{color:var(--muted);font-size:0.9rem}
            .toggle {display:inline-flex;align-items:center;gap:8px}
            .small-note{color:var(--muted);font-size:0.9rem;margin-top:6px}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="top">
              <div class="logo">
                <img src="/assets/logo.png" alt="logo" onerror="this.style.display='none'"/>
                <div>
                  <div style="font-weight:800">ADMIN PANEL</div>
                  <div class="small-note">Manage contacts, settings and the add-number availability</div>
                </div>
              </div>
              <div>
                <input id="username" placeholder="admin" class="input" />
                <input id="password" type="password" placeholder="password" class="input" />
                <button id="loginBtn" class="btn primary">Login</button>
              </div>
            </div>

            <div id="adminArea" style="display:none">
              <div class="section">
                <div style="display:flex;align-items:center;justify-content:space-between;gap:12px">
                  <div class="field">
                    <label class="toggle">
                      <input type="checkbox" id="addingToggle" /> <span style="margin-left:6px">Allow users to add numbers</span>
                    </label>
                  </div>
                  <div class="field">
                    <label style="margin-right:8px">Goal</label>
                    <input id="goalInput" class="input" style="width:110px" />
                    <button id="saveSettingsBtn" class="btn primary">Save</button>
                  </div>
                </div>
                <div class="small-note">When adding is turned OFF, users who press "Add" will see the message and cannot add numbers.</div>
              </div>

              <div class="section">
                <div style="display:flex;align-items:center;justify-content:space-between">
                  <div style="font-weight:700">Contacts</div>
                  <div style="color:var(--muted)">Click Delete to remove a contact</div>
                </div>
                <table id="contactsTable">
                  <thead><tr><th>ID</th><th>Name</th><th>Phone</th><th>Created At</th><th>Action</th></tr></thead>
                  <tbody></tbody>
                </table>
              </div>

              <div class="section" style="margin-top:12px">
                <button id="downloadBtn" class="btn primary">⭳ Download VCF</button>
                <button id="resetBtn" class="btn danger">🗑 Reset All Contacts</button>
                <button id="logoutBtn" class="btn" style="background:transparent;border:1px solid rgba(255,255,255,0.04)">Logout</button>
              </div>
            </div>
          </div>

          <audio id="wrongAudio" preload="none"></audio>

          <script>
            const ADMIN_USER = 'admin'; // used only to build basic token client-side
            function getAuthToken(username, password) {
              return btoa(username + ':' + password);
            }
            function setAdminAreaVisible(visible) {
              document.getElementById('adminArea').style.display = visible ? 'block' : 'none';
            }
            async function fetchSettings(token) {
              const r = await fetch('/admin/settings', { method:'GET', headers: {'Authorization':'Basic ' + token} });
              return r;
            }
            async function fetchContacts() {
              const r = await fetch('/contacts');
              return r.json();
            }
            async function loadContactsIntoTable() {
              const data = await fetchContacts();
              if (!data || !data.success) return;
              const tbody = document.querySelector('#contactsTable tbody');
              tbody.innerHTML = '';
              for (const c of data.contacts) {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${c.id}</td><td>${escapeHtml(c.name)}</td><td>${escapeHtml(c.phone)}</td><td>${c.created_at || ''}</td>
                  <td><button data-id="${c.id}" class="btn deleteBtn" style="background:#ff6b6b">Delete</button></td>`;
                tbody.appendChild(tr);
              }
              document.querySelectorAll('.deleteBtn').forEach(btn=>{
                btn.addEventListener('click', async (e)=>{
                  const id = e.currentTarget.getAttribute('data-id');
                  if (!confirm('Delete contact #' + id + '?')) return;
                  const token = localStorage.getItem('ADMIN_AUTH');
                  if (!token) { alert('Login first'); return; }
                  const res = await fetch('/admin/delete_contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'Authorization':'Basic ' + token },
                    body: JSON.stringify({ id: id })
                  });
                  const j = await res.json();
                  if (res.ok) {
                    alert(j.message || 'Deleted');
                    loadContactsIntoTable();
                  } else {
                    alert(j.error || 'Delete failed');
                  }
                });
              });
            }
            function escapeHtml(s){ if(!s) return ''; return s.replace(/[&<>"']/g, function(m){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',\"'\":\"&#39;\"}[m];}); }
            async function playWrongAudio() {
              try {
                const a = document.getElementById('wrongAudio');
                a.src = '/assets/dom.mp3';
                a.currentTime = 0;
                await a.play().catch(()=>{});
              } catch(e){ console.warn(e); }
            }
            document.getElementById('loginBtn').addEventListener('click', async ()=>{
              const u = document.getElementById('username').value.trim();
              const p = document.getElementById('password').value || '';
              if (!u || !p) { alert('Provide credentials'); return; }
              const token = getAuthToken(u, p);
              const r = await fetchSettings(token);
              if (r.status === 200) {
                const j = await r.json();
                localStorage.setItem('ADMIN_AUTH', token);
                setAdminAreaVisible(true);
                document.getElementById('addingToggle').checked = j.adding_enabled;
                document.getElementById('goalInput').value = j.goal;
                await loadContactsIntoTable();
              } else {
                playWrongAudio();
                alert('Invalid admin credentials');
              }
            });
            document.getElementById('saveSettingsBtn').addEventListener('click', async ()=>{
              const token = localStorage.getItem('ADMIN_AUTH');
              if (!token) { alert('Login first'); return; }
              const adding_enabled = document.getElementById('addingToggle').checked;
              const goal = parseInt(document.getElementById('goalInput').value) || 1000;
              const r = await fetch('/admin/settings', {
                method: 'POST',
                headers: { 'Content-Type':'application/json', 'Authorization':'Basic ' + token },
                body: JSON.stringify({ adding_enabled: adding_enabled, goal: goal })
              });
              const j = await r.json();
              if (r.ok) {
                alert('Settings saved');
              } else {
                alert(j.error || 'Save failed');
              }
            });
            document.getElementById('downloadBtn').addEventListener('click', async ()=>{
              const token = localStorage.getItem('ADMIN_AUTH');
              if (!token) { alert('Login first'); return; }
              const r = await fetch('/download', { method:'GET', headers:{ 'Authorization':'Basic ' + token }});
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
              } else {
                const j = await r.json();
                alert(j.error || 'Download failed');
              }
            });
            document.getElementById('resetBtn').addEventListener('click', async ()=>{
              if (!confirm('This will permanently delete ALL contacts. Continue?')) return;
              const token = localStorage.getItem('ADMIN_AUTH');
              if (!token) { alert('Login first'); return; }
              const r = await fetch('/admin/reset', { method:'POST', headers:{ 'Content-Type':'application/json', 'Authorization':'Basic ' + token }, body: JSON.stringify({}) });
              const j = await r.json();
              if (r.ok) {
                alert(j.message || 'Reset completed');
                await loadContactsIntoTable();
              } else {
                alert(j.error || 'Reset failed');
              }
            });
            document.getElementById('logoutBtn').addEventListener('click', ()=>{
              localStorage.removeItem('ADMIN_AUTH');
              setAdminAreaVisible(false);
            });
            (async function(){
              const token = localStorage.getItem('ADMIN_AUTH');
              if (token) {
                const r = await fetchSettings(token);
                if (r.status === 200) {
                  const j = await r.json();
                  setAdminAreaVisible(true);
                  document.getElementById('addingToggle').checked = j.adding_enabled;
                  document.getElementById('goalInput').value = j.goal;
                  await loadContactsIntoTable();
                } else {
                  localStorage.removeItem('ADMIN_AUTH');
                }
              }
            })();
          </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))