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
        # Check if this is an asset request
        if self.path.startswith('/assets/'):
            # This is a placeholder - in production, serve static files differently
            self.serve_logo_placeholder()
            return
            
        # Serve HTML form
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>STATUS VIEWS CENTRE - Contact Manager</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                :root {
                    --primary: #2c3e50;
                    --secondary: #3498db;
                    --accent: #e74c3c;
                    --light: #ecf0f1;
                    --dark: #2c3e50;
                    --success: #27ae60;
                    --warning: #f39c12;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                    color: var(--dark);
                }
                
                .container {
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 25px 50px rgba(0,0,0,0.25);
                    padding: 40px;
                    width: 100%;
                    max-width: 750px;
                    position: relative;
                    overflow: hidden;
                    display: flex;
                    gap: 20px;
                }

                .left {
                    flex: 1.2;
                }
                
                .right {
                    width: 320px;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    position: relative;
                }
                
                .logo-placeholder {
                    width: 120px;
                    height: 120px;
                    margin: 0 auto 20px;
                    background: linear-gradient(135deg, var(--secondary), var(--primary));
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 48px;
                    box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
                }
                
                h1 {
                    color: var(--primary);
                    margin-bottom: 10px;
                    font-size: 2.2em;
                    font-weight: 700;
                }
                
                .subtitle {
                    color: #7f8c8d;
                    font-size: 1.1em;
                    line-height: 1.5;
                    margin-bottom: 10px;
                }
                
                .tagline {
                    color: var(--secondary);
                    font-weight: 600;
                    font-size: 1.2em;
                    margin-bottom: 30px;
                }
                
                .form-container {
                    background: var(--light);
                    padding: 30px;
                    border-radius: 15px;
                    margin-bottom: 30px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
                }
                
                .form-group {
                    margin-bottom: 25px;
                }
                
                label {
                    display: block;
                    margin-bottom: 8px;
                    color: var(--primary);
                    font-weight: 600;
                    font-size: 1.1em;
                }
                
                .input-with-icon {
                    position: relative;
                }
                
                .input-with-icon i {
                    position: absolute;
                    left: 15px;
                    top: 50%;
                    transform: translateY(-50%);
                    color: var(--secondary);
                    font-size: 18px;
                }
                
                .input-with-icon input {
                    width: 100%;
                    padding: 15px 15px 15px 50px;
                    border: 2px solid #dfe6e9;
                    border-radius: 10px;
                    font-size: 16px;
                    transition: all 0.3s;
                }
                
                .input-with-icon input:focus {
                    outline: none;
                    border-color: var(--secondary);
                    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
                }
                
                button {
                    width: 100%;
                    padding: 17px;
                    background: linear-gradient(135deg, var(--secondary) 0%, var(--primary) 100%);
                    color: white;
                    border: none;
                    border-radius: 10px;
                    font-size: 18px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s;
                    margin-top: 10px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                }
                
                button:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 10px 25px rgba(52, 152, 219, 0.4);
                }
                
                button:active {
                    transform: translateY(-1px);
                }
                
                .message {
                    padding: 15px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                    text-align: center;
                    font-weight: 500;
                    display: none;
                }
                
                .success {
                    background-color: #d5f4e6;
                    color: var(--success);
                    border: 1px solid #b8e994;
                    display: block;
                }
                
                .error {
                    background-color: #ffeaa7;
                    color: var(--warning);
                    border: 1px solid #fdcb6e;
                    display: block;
                }
                
                .admin-section {
                    margin-top: 20px;
                    padding: 20px;
                    background: linear-gradient(135deg, #34495e 0%, #2c3e50 100%);
                    border-radius: 12px;
                    color: white;
                }
                
                .admin-title {
                    font-size: 1.1em;
                    margin-bottom: 10px;
                    text-align: center;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                }
                
                .admin-title i {
                    color: var(--secondary);
                }
                
                .download-btn {
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                }
                
                .download-btn:hover {
                    box-shadow: 0 10px 25px rgba(231, 76, 60, 0.4);
                }
                
                .password-input {
                    margin-bottom: 15px;
                }
                
                .stats {
                    display: flex;
                    justify-content: space-between;
                    gap: 8px;
                    margin-top: 20px;
                    padding-top: 10px;
                    border-top: 1px solid #dfe6e9;
                }
                
                .stat-item {
                    text-align: center;
                    flex: 1;
                }
                
                .stat-number {
                    font-size: 1.6em;
                    font-weight: 700;
                    color: var(--secondary);
                    display: block;
                }
                
                .stat-label {
                    font-size: 0.9em;
                    color: #7f8c8d;
                }
                
                .footer {
                    text-align: center;
                    margin-top: 20px;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }
                
                .pulse {
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
                
                @media (max-width: 900px) {
                    .container {
                        padding: 20px;
                        flex-direction: column;
                    }
                    
                    .right {
                        width: 100%;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="left">
                    <div class="header">
                        <div class="logo-placeholder">
                            <i class="fas fa-eye"></i>
                        </div>
                        <h1>STATUS VIEWS CENTRE</h1>
                        <div class="tagline">Contact Management System</div>
                        <p class="subtitle">Add your contacts below to generate VCF file for easy sharing</p>
                    </div>
                    
                    <div id="message" class="message"></div>
                    
                    <div class="form-container">
                        <form id="contactForm">
                            <div class="form-group">
                                <label for="name"><i class="fas fa-user"></i> Full Name:</label>
                                <div class="input-with-icon">
                                    <i class="fas fa-user-circle"></i>
                                    <input type="text" id="name" name="name" placeholder="Enter full name (e.g., Uthuman)" required>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label for="phone"><i class="fas fa-phone"></i> Phone Number:</label>
                                <div class="input-with-icon">
                                    <i class="fas fa-mobile-alt"></i>
                                    <input type="tel" id="phone" name="phone" placeholder="Enter phone number (e.g., 256784670936)" required>
                                </div>
                                <small style="color:#7f8c8d;display:block;margin-top:8px;">
                                    Only Ugandan numbers allowed (must start with <strong>256</strong>). Example: <code>256784670936</code>
                                </small>
                            </div>
                            
                            <button type="submit" class="pulse">
                                <i class="fas fa-plus-circle"></i> Add Contact
                            </button>
                        </form>
                    </div>

                    <div class="stats">
                        <div class="stat-item">
                            <span class="stat-number" id="contactCount">0</span>
                            <span class="stat-label">Contacts</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number" id="todayCount">0</span>
                            <span class="stat-label">Today</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-number" id="remainingCount">1000</span>
                            <span class="stat-label">Remaining to 1000</span>
                        </div>
                    </div>

                    <div class="footer">
                        <p>© 2026 STATUS VIEWS CENTRE. All rights reserved.</p>
                        <p>VCF Contact Management System v1.0</p>
                    </div>
                </div>

                <div class="right">
                    <div class="admin-section">
                        <h3 class="admin-title">
                            <i class="fas fa-lock"></i> Admin Access
                        </h3>
                        <div class="form-group password-input">
                            <div class="input-with-icon">
                                <i class="fas fa-key"></i>
                                <input type="password" id="password" name="password" placeholder="Enter admin password">
                            </div>
                        </div>

                        <div style="margin-bottom:10px;">
                            <label style="color:#fff; font-weight:600;">WhatsApp group (required to download VCF)</label>
                            <p style="color:#fff; font-size:0.9em;">
                                Please join: <a href="https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa" target="_blank" style="color:#ffd;">Join WhatsApp Group</a>
                            </p>
                            <label style="display:flex;gap:8px;align-items:center;color:#fff;">
                                <input type="checkbox" id="joinedWhatsapp" /> I have joined the WhatsApp group
                            </label>
                        </div>

                        <button class="download-btn" onclick="downloadVCF()">
                            <i class="fas fa-download"></i> Download VCF File
                        </button>

                        <hr style="margin:15px 0;border-color:rgba(255,255,255,0.1)" />

                        <button style="background:#c0392b;margin-bottom:8px;" onclick="adminReset()">
                            <i class="fas fa-trash-alt"></i> Reset / Delete All Contacts
                        </button>

                        <small style="display:block;color:#ffd;margin-top:8px;">
                            Reset will permanently delete all contacts and reset IDs. Admin password required.
                        </small>
                    </div>
                </div>
            </div>
            
            <script>
                const GOAL = 1000;

                // Load contact statistics
                async function loadStats() {
                    try {
                        const response = await fetch('/contacts');
                        const data = await response.json();
                        
                        if (data.success) {
                            document.getElementById('contactCount').textContent = data.count;
                            
                            // Calculate today's contacts
                            const today = new Date().toISOString().split('T')[0];
                            const todayCount = data.contacts.filter(contact => 
                                contact.created_at && contact.created_at.startsWith(today)
                            ).length;
                            document.getElementById('todayCount').textContent = todayCount;

                            const remaining = Math.max(GOAL - data.count, 0);
                            document.getElementById('remainingCount').textContent = remaining;
                        }
                    } catch (error) {
                        console.error('Error loading stats:', error);
                    }
                }
                
                document.getElementById('contactForm').addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    const name = document.getElementById('name').value.trim();
                    const phoneRaw = document.getElementById('phone').value.trim();
                    
                    if (!name || !phoneRaw) {
                        showMessage('Please fill in all fields', 'error');
                        return;
                    }

                    // Normalize phone: remove non-digits
                    const phone = phoneRaw.replace(/\\D/g, '');
                    
                    // Validate Ugandan phone (must start with 256)
                    if (!phone.startsWith('256')) {
                        showMessage('Only Ugandan numbers are allowed. The number must start with 256.', 'error');
                        return;
                    }
                    
                    try {
                        const response = await fetch('/add', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ name, phone })
                        });
                        
                        const result = await response.json();
                        
                        if (response.ok) {
                            showMessage(result.message || '✓ Contact added successfully!', 'success');
                            document.getElementById('contactForm').reset();
                            loadStats(); // Refresh stats
                        } else {
                            showMessage(result.error || (result.message) || '✗ Error adding contact', 'error');
                        }
                        
                    } catch (error) {
                        console.error('Error:', error);
                        showMessage('✗ Network error. Please try again.', 'error');
                    }
                });
                
                async function downloadVCF() {
                    const password = document.getElementById('password').value;
                    const joined = document.getElementById('joinedWhatsapp').checked;
                    
                    if (!joined) {
                        showMessage('You must join the WhatsApp group before downloading the VCF.', 'error');
                        return;
                    }

                    if (!password) {
                        showMessage('Admin password required to download VCF', 'error');
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/download?password=${encodeURIComponent(password)}`);
                        
                        if (response.ok) {
                            const blob = await response.blob();
                            const url = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `status_views_contacts_${new Date().toISOString().split('T')[0]}.vcf`;
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                            showMessage('✓ VCF file downloaded successfully!', 'success');
                        } else {
                            const error = await response.json();
                            showMessage(`✗ ${error.error || 'Download failed'}`, 'error');
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        showMessage('✗ Download failed. Please try again.', 'error');
                    }
                }

                async function adminReset() {
                    const password = document.getElementById('password').value;
                    if (!password) {
                        showMessage('Admin password required to reset', 'error');
                        return;
                    }

                    if (!confirm('This will permanently delete ALL contacts and reset IDs. Are you sure?')) {
                        return;
                    }

                    try {
                        const res = await fetch('/admin/reset', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({ password })
                        });

                        const json = await res.json();
                        if (res.ok) {
                            showMessage(json.message || 'All contacts deleted and reset', 'success');
                            loadStats();
                        } else {
                            showMessage(json.error || 'Reset failed', 'error');
                        }
                    } catch (err) {
                        console.error(err);
                        showMessage('Network error during reset', 'error');
                    }
                }
                
                function showMessage(text, type) {
                    const messageDiv = document.getElementById('message');
                    messageDiv.textContent = text;
                    messageDiv.className = `message ${type}`;
                    
                    // Clear message after 6 seconds
                    setTimeout(() => {
                        messageDiv.className = 'message';
                        messageDiv.textContent = '';
                    }, 6000);
                }
                
                // Load stats on page load
                document.addEventListener('DOMContentLoaded', loadStats);
                
                // Add enter key support for password field
                document.getElementById('password').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        downloadVCF();
                    }
                });
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
        return
    
    def serve_logo_placeholder(self):
        # Serve a placeholder logo or redirect
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Logo placeholder - upload your logo to /assets/logo.png')
        return
    
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
                # If unique index causes error (race), translate to duplicate
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