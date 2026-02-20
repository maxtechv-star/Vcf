# Meta VCF

Serverless EJS-based contact collector (Vercel functions) with admin panel and VCF export.

Quick setup:
1. Create a Git repo and add these files.
2. Add environment variables in Vercel (Project Settings -> Environment Variables):
   - DATABASE_URL (Postgres connection string)
   - TARGET_COUNT (optional, default 700)
   - ADMIN_USER (optional)
   - ADMIN_PASS (optional)
   - RESET_CONFIRM (optional)
3. Push to GitHub and import project to Vercel.
4. Deploy. Root (/) is served by /api/index function.

Notes:
- Do NOT commit a real `.env` to source control.
- Remove trailing dot from your DATABASE_URL if present.
- For local development use `vercel dev` and a local `.env` (copy .env.example).