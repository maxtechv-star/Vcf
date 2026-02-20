# Meta VCF 🚀

A full-stack contact collection app with admin panel, VCF export, and live progress tracking.

**Built with:** Express.js, EJS, PostgreSQL, Vercel  
**Current Version:** 1.0.0

---

## Features ✨

- 📝 **Contact Submission Form** - Collect phone numbers and names
- 📊 **Live Progress Tracker** - Real-time sync of collected vs. target
- 🎯 **Custom Goals** - Admin can set collection targets on-the-fly
- 💾 **VCF Export** - Download contacts as .vcf file once target is reached
- 🔐 **Admin Panel** - Secure login with reset & goal management
- ⚠️ **WhatsApp Integration** - Links to join WhatsApp group/channel
- 📱 **Responsive Design** - Mobile-friendly dark theme UI

---

## Setup Instructions

### Prerequisites
- Node.js 16+
- PostgreSQL database (Render Postgres recommended)
- Vercel account (for deployment)

### Local Development

1. **Clone & Install**
   ```bash
   git clone <repo-url>
   cd meta-vcf
   npm install
   ```

2. **Configure .env**
   ```env
   DATABASE_URL=postgresql://user:pass@host/dbname
   ADMIN_USER=admin
   ADMIN_PASS=uthuman
   RESET_CONFIRM=1542
   TARGET_COUNT=700
   NODE_ENV=development
   ```

3. **Run Dev Server**
   ```bash
   npm run dev
   ```
   Visit http://localhost:3000

---

## Deployment to Vercel

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/<your-username>/meta-vcf.git
git push -u origin main
```

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"New Project"** and select your GitHub repository
3. Under **"Environment Variables"** add:
   - `DATABASE_URL` = Your Render PostgreSQL connection string
   - `ADMIN_USER` = admin
   - `ADMIN_PASS` = uthuman
   - `RESET_CONFIRM` = 1542
   - `TARGET_COUNT` = 700

4. Click **"Deploy"** and wait for it to complete

### Step 3: Test
Visit your Vercel deployment URL and verify:
- Home page loads with form
- Form submissions work
- Admin login works (admin / uthuman)
- Admin panel shows progress & controls

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page with form |
| GET | `/admin-login` | Admin login page |
| GET | `/admin` | Admin panel (cookie-protected) |
| POST | `/api/contacts` | Submit contact |
| GET | `/api/count` | Get progress stats |
| POST | `/api/admin/login` | Admin login (sets cookie) |
| GET | `/api/admin/export-vcf` | Download VCF file |
| POST | `/api/admin/reset` | Reset all contacts |
| POST | `/api/admin/set-goal` | Set new target goal |

---

## Default Admin Credentials
- **Username:** admin
- **Password:** uthuman
- **Reset Confirm Code:** 1542

⚠️ **Change these in production!**

---

## Directory Structure
```
meta-vcf/
├── api/
│   ├── server.js           # Express app & routes
│   └── lib/
│       └── db.js           # Database functions
├── views/
│   ├── layout.ejs          # (unused in this setup)
│   ├── index.ejs           # Home page
│   ├── admin-login.ejs     # Login page
│   ├── admin.ejs           # Admin panel
│   └── error.ejs           # Error page
├── public/                 # Static files (if needed)
├── package.json
├── .env
├── .gitignore
├── vercel.json             # Vercel config
└── README.md
```

---

## Tech Stack

- **Backend:** Express.js (Node.js)
- **Frontend:** EJS templates + Vanilla JS
- **Database:** PostgreSQL
- **Hosting:** Vercel
- **Styling:** Inline CSS (dark theme)

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | — | PostgreSQL connection string (required) |
| TARGET_COUNT | 700 | Initial collection target |
| ADMIN_USER | admin | Admin username |
| ADMIN_PASS | uthuman | Admin password |
| RESET_CONFIRM | 1542 | Password to confirm reset |
| NODE_ENV | development | Environment (development / production) |
| PORT | 3000 | Server port |

---

## Security Notes ⚠️

1. **Admin Credentials:** Change defaults in production!
2. **SSL:** Always use HTTPS in production
3. **Rate Limiting:** Consider adding rate-limit middleware
4. **Input Validation:** Already basic validation; add more for production
5. **CORS:** Open by default; lock down if needed

---

## Troubleshooting

### Database Connection Error
- Verify DATABASE_URL in Vercel environment
- Check Render PostgreSQL whitelist (allow Vercel IPs)

### Admin Login Not Working
- Clear browser cookies
- Verify ADMIN_USER & ADMIN_PASS env vars
- Check server logs

### VCF Export Returns 403
- Ensure target is reached (collected >= target)
- Try setting a lower goal via admin panel

---

## Support

- **WhatsApp Group:** [Join Here](https://chat.whatsapp.com/FQMf4pL5ezr5QlMKMANEqa?mode=gi_t)
- **GitHub Issues:** Report bugs and request features

---

## License

MIT © 2026 Meta VCF

Made with ❤️ by the development team