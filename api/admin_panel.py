from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve admin login + controls page
        html = """
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width,initial-scale=1">
          <title>Admin Panel - STATUS VIEWS CENTRE</title>
          <style>
            body{font-family:Arial,Helvetica,sans-serif;background:#f3f6f8;padding:20px;display:flex;justify-content:center;align-items:center;min-height:100vh}
            .card{background:#ffffff;padding:20px;border-radius:12px;max-width:520px;width:100%;box-shadow:0 10px 30px rgba(0,0,0,0.08)}
            .logo{display:flex;align-items:center;gap:12px;margin-bottom:12px}
            .logo img{width:56px;height:56px;border-radius:8px;object-fit:cover}
            h2{margin:0 0 6px 0}
            .input{width:100%;padding:10px;border-radius:8px;border:1px solid #e6eef5;margin-bottom:10px}
            .btn{display:inline-block;padding:10px 14px;border-radius:8px;border:none;background:#2c3e50;color:#fff;cursor:pointer;width:100%}
            .btn.secondary{background:#3498db}
            .btn.danger{background:#c0392b}
            .row{display:flex;gap:10px}
            .note{font-size:0.95rem;color:#7f8c8d;margin-top:8px}
            .message{padding:8px;border-radius:8px;margin-bottom:10px;display:none}
            .message.error{background:#ffeaa7;color:#f39c12}
            .message.success{background:#d5f4e6;color:#27ae60}
            .group-link{display:flex;gap:12px;align-items:center;padding:10px;border-radius:10px;border:1px solid #e6eef5;text-decoration:none;color:inherit;margin-top:10px}
            .group-link img{width:40px;height:40px;border-radius:8px;object-fit:cover}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="logo">
              <img src="/assets/logo.png" alt="logo" onerror="this.style.display='none'"/>
              <div>
                <h2>Admin Panel</h2>
                <div style="font-size:0.9rem;color:#7f8c8d">Login to download VCF or reset contacts</div>
              </div>
            </div>

            <div id="message" class="message"></div>

            <input id="username" class="input" placeholder="Username" value="admin" />
            <input id="password" type="password" class="input" placeholder="Password" />
            <button id="loginBtn" class="btn">Login</button>

            <div id="controls" style="display:none;margin-top:14px;">
              <div style="margin-bottom:10px;">
                <button id="downloadBtn" class="btn secondary">⭳ Download VCF</button>
              </div>
              <div>
                <button id="resetBtn" class="btn danger">🗑 Reset / Delete All Contacts</button>
              </div>
              <div style="margin-top:10px;">
                <button id="logoutBtn" class="btn" style="background:#7f8c8d">Logout</button>
              </div>
            </div>

            <a id="joinGroup" class="group-link" href="https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa" target="_blank" rel="noopener">
              <img src="/assets/logo.png" alt="group" onerror="this.style.display='none'"/>
              <div>
                <div style="font-weight:600">Join WhatsApp Group</div>
                <div style="font-size:0.9rem;color:#7f8c8d">VCF will be dropped in this group</div>
              </div>
            </a>

            <div class="note">Admin actions are server-side authenticated. For security set ADMIN_PASSWORD via environment variables in production.</div>
          </div>

          <script>
            async function apiLogin(username, password) {
              const res = await fetch('/admin/login', {
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify({ username, password })
              });
              return res;
            }

            document.getElementById('loginBtn').addEventListener('click', async () => {
              const u = document.getElementById('username').value.trim();
              const p = document.getElementById('password').value;
              const msg = document.getElementById('message');
              msg.style.display = 'none';

              if (!u || !p) {
                msg.textContent = 'Provide username and password';
                msg.className = 'message error';
                msg.style.display = 'block';
                return;
              }

              try {
                const r = await apiLogin(u, p);
                const j = await r.json();
                if (r.ok && j && j.token) {
                  // store token (base64) in localStorage
                  localStorage.setItem('ADMIN_AUTH', j.token);
                  msg.textContent = 'Login successful';
                  msg.className = 'message success';
                  msg.style.display = 'block';
                  showControls();
                } else {
                  msg.textContent = (j && j.error) || 'Login failed';
                  msg.className = 'message error';
                  msg.style.display = 'block';
                }
              } catch (e) {
                msg.textContent = 'Network or server error';
                msg.className = 'message error';
                msg.style.display = 'block';
              }
            });

            function showControls() {
              document.getElementById('controls').style.display = 'block';
            }

            function hideControls() {
              document.getElementById('controls').style.display = 'none';
            }

            async function downloadVCF() {
              const token = localStorage.getItem('ADMIN_AUTH');
              if (!token) { alert('Login first'); return; }
              try {
                const r = await fetch('/download', {
                  method: 'GET',
                  headers: { 'Authorization': 'Basic ' + token }
                });
                if (r.ok) {
                  const blob = await r.blob();
                  const url = window.URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  // use filename from content-disposition?
                  a.download = 'contacts.vcf';
                  document.body.appendChild(a);
                  a.click();
                  a.remove();
                  window.URL.revokeObjectURL(url);
                  alert('VCF download started');
                } else {
                  const j = await r.json();
                  alert(j && j.error ? j.error : 'Download failed');
                }
              } catch (e) {
                alert('Download failed');
              }
            }

            async function resetContacts() {
              const token = localStorage.getItem('ADMIN_AUTH');
              if (!token) { alert('Login first'); return; }
              if (!confirm('This will permanently delete ALL contacts and reset IDs. Continue?')) return;
              try {
                const r = await fetch('/admin/reset', {
                  method: 'POST',
                  headers: { 'Content-Type':'application/json', 'Authorization':'Basic ' + token },
                  body: JSON.stringify({})
                });
                const j = await r.json();
                if (r.ok) {
                  alert(j.message || 'Reset completed');
                } else {
                  alert(j.error || 'Reset failed');
                }
              } catch (e) {
                alert('Reset failed');
              }
            }

            document.getElementById('downloadBtn').addEventListener('click', downloadVCF);
            document.getElementById('resetBtn').addEventListener('click', resetContacts);
            document.getElementById('logoutBtn').addEventListener('click', () => {
              localStorage.removeItem('ADMIN_AUTH');
              hideControls();
              alert('Logged out');
            });

            // If token present, reveal controls
            if (localStorage.getItem('ADMIN_AUTH')) {
              showControls();
            }
          </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))