from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve admin login + controls page (dark / black theme)
        html = """
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width,initial-scale=1">
          <title>Admin Panel - STATUS VIEWS CENTRE</title>
          <style>
            :root{
                --bg:#070707;
                --card:#0f1111;
                --muted:#b9b9bd;
                --accent:#f0c000;
                --danger:#ff6b6b;
                --primary:#ffffff;
                --input:#111315;
                --border:#222425;
            }
            body{margin:0;background:linear-gradient(180deg,#000,#070707);font-family:Arial,Helvetica,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;color:var(--primary);}
            .card{width:100%;max-width:520px;background:linear-gradient(180deg,rgba(255,255,255,0.02),rgba(255,255,255,0.01));padding:20px;border-radius:12px;border:1px solid rgba(255,255,255,0.03);box-shadow:0 12px 40px rgba(0,0,0,0.8)}
            .logo{display:flex;gap:12px;align-items:center;margin-bottom:10px}
            .logo img{width:56px;height:56px;border-radius:8px;object-fit:cover;border:1px solid rgba(255,255,255,0.04)}
            h2{margin:0;color:var(--primary)}
            .input{width:100%;padding:10px;border-radius:8px;border:1px solid var(--border);background:var(--input);color:var(--primary);margin-bottom:10px;box-sizing:border-box}
            .btn{padding:10px;border-radius:8px;border:none;cursor:pointer;width:100%;font-weight:700}
            .btn.primary{background:linear-gradient(90deg,var(--accent),#ffb84d);color:#0b0b0b}
            .btn.danger{background:var(--danger);color:#0b0b0b}
            .controls{display:none;margin-top:12px}
            .group-link{display:flex;gap:12px;align-items:center;padding:10px;border-radius:10px;border:1px solid rgba(255,255,255,0.03);margin-top:12px;text-decoration:none;color:inherit}
            .group-link img{width:40px;height:40px;border-radius:8px;object-fit:cover}
            .message{display:none;padding:8px;border-radius:8px;margin-bottom:8px}
            .message.success{background:rgba(38,166,154,0.08);color:#26a69a;display:block}
            .message.error{background:rgba(255,107,107,0.08);color:var(--danger);display:block}
            .note{font-size:0.9rem;color:var(--muted);margin-top:10px}
            .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);z-index:999;align-items:center;justify-content:center}
            .modal.active{display:flex}
            .modal-content{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;max-width:400px;width:100%;box-shadow:0 20px 40px rgba(0,0,0,0.9)}
            .modal-heading{font-size:1.1rem;font-weight:700;margin-bottom:10px;color:var(--primary)}
            .modal-text{color:var(--muted);margin-bottom:10px;font-size:0.95rem}
            .modal-password{width:100%;padding:10px;border-radius:8px;border:1px solid var(--border);background:var(--input);color:var(--primary);margin-bottom:10px;box-sizing:border-box}
            .modal-buttons{display:flex;gap:8px}
            .modal-buttons button{flex:1;padding:10px;border-radius:8px;border:none;font-weight:700;cursor:pointer}
            .modal-buttons .btn-confirm{background:var(--danger);color:#0b0b0b}
            .modal-buttons .btn-cancel{background:transparent;border:1px solid var(--border);color:var(--primary)}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="logo">
              <img src="/assets/logo.png" alt="logo" onerror="this.style.display='none'"/>
              <div>
                <h2>Admin Panel</h2>
                <div style="font-size:0.9rem;color:var(--muted)">Login to download VCF or reset contacts</div>
              </div>
            </div>

            <div id="message" class="message"></div>

            <input id="username" class="input" placeholder="Username" value="admin" />
            <input id="password" type="password" class="input" placeholder="Password" />
            <button id="loginBtn" class="btn primary">Login</button>

            <div id="controls" class="controls">
              <div style="margin-bottom:10px;">
                <button id="downloadBtn" class="btn primary">⭳ Download VCF</button>
              </div>
              <div style="margin-bottom:10px;">
                <button id="resetBtn" class="btn danger">🗑 Reset / Delete All Contacts</button>
              </div>
              <div>
                <button id="logoutBtn" class="btn" style="background:transparent;border:1px solid rgba(255,255,255,0.03);color:var(--primary)">Logout</button>
              </div>
            </div>

            <a id="joinGroup" class="group-link" href="https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa" target="_blank" rel="noopener">
              <img src="/assets/logo.png" alt="group" onerror="this.style.display='none'"/>
              <div>
                <div style="font-weight:700">Join WhatsApp Group</div>
                <div style="font-size:0.9rem;color:var(--muted)">VCF will be dropped in this group</div>
              </div>
            </a>

            <div class="note">For security set ADMIN_PASSWORD via environment variables in production. Logout removes local token only.</div>
          </div>

          <!-- Reset Confirmation Modal -->
          <div id="resetModal" class="modal">
            <div class="modal-content">
              <div class="modal-heading">Confirm Reset</div>
              <div class="modal-text">This will permanently delete ALL contacts. Enter the reset password to confirm:</div>
              <input id="resetPassword" type="password" class="modal-password" placeholder="Reset password" />
              <div class="modal-buttons">
                <button class="btn-confirm" id="confirmResetBtn">Confirm Reset</button>
                <button class="btn-cancel" id="cancelResetBtn">Cancel</button>
              </div>
            </div>
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

            function showControls() { document.getElementById('controls').style.display = 'block'; }
            function hideControls() { document.getElementById('controls').style.display = 'none'; }

            async function downloadVCF() {
              const token = localStorage.getItem('ADMIN_AUTH');
              if (!token) { alert('Login first'); return; }
              try {
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
                  alert('VCF download started');
                } else {
                  const j = await r.json();
                  alert(j && j.error ? j.error : 'Download failed');
                }
              } catch (e) {
                alert('Download failed');
              }
            }

            // Show reset confirmation modal
            document.getElementById('resetBtn').addEventListener('click', () => {
              document.getElementById('resetModal').classList.add('active');
              document.getElementById('resetPassword').value = '';
              document.getElementById('resetPassword').focus();
            });

            // Cancel reset
            document.getElementById('cancelResetBtn').addEventListener('click', () => {
              document.getElementById('resetModal').classList.remove('active');
            });

            // Confirm reset with password
            document.getElementById('confirmResetBtn').addEventListener('click', async () => {
              const resetPwd = document.getElementById('resetPassword').value;
              const correctPassword = '15425142';

              if (resetPwd !== correctPassword) {
                alert('❌ Incorrect reset password');
                return;
              }

              await performReset();
            });

            // Actually perform the reset
            async function performReset() {
              const token = localStorage.getItem('ADMIN_AUTH');
              if (!token) { alert('Login first'); return; }
              try {
                const r = await fetch('/admin/reset', { 
                  method:'POST', 
                  headers:{ 'Content-Type':'application/json', 'Authorization':'Basic ' + token }, 
                  body:JSON.stringify({}) 
                });
                const j = await r.json();
                document.getElementById('resetModal').classList.remove('active');
                if (r.ok) {
                  alert('✅ ' + (j.message || 'Reset completed'));
                } else {
                  alert('❌ ' + (j.error || 'Reset failed'));
                }
              } catch (e) { 
                alert('❌ Reset failed'); 
              }
            }

            document.getElementById('downloadBtn').addEventListener('click', downloadVCF);
            document.getElementById('logoutBtn').addEventListener('click', () => { 
              localStorage.removeItem('ADMIN_AUTH'); 
              hideControls(); 
              alert('Logged out'); 
            });

            // If token present, reveal controls
            if (localStorage.getItem('ADMIN_AUTH')) { showControls(); }
          </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))