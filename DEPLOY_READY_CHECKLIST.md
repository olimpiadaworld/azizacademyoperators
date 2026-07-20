# Railway + Netlify deploy checklist

## Backend (Railway)
- Root Directory: `backend`
- Start Command: `npm start`
- Add PostgreSQL service in the same Railway project.
- Variables:

```env
NODE_ENV=production
HOST=0.0.0.0
TIME_ZONE=Asia/Tashkent
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_SSL_REQUIRE=true
CORS_ALLOWED_ORIGINS=https://YOUR-NETLIFY-SITE.netlify.app
JWT_ACCESS_SECRET=PASTE_LONG_RANDOM_SECRET
JWT_REFRESH_SECRET=PASTE_DIFFERENT_LONG_RANDOM_SECRET
ADMIN_USERNAME=admin
ADMIN_PASSWORD=PASTE_STRONG_PASSWORD
ADMIN_FULL_NAME=Administrator
API_RATE_LIMIT_PER_MINUTE=240
AUTH_RATE_LIMIT_PER_15_MINUTES=20
PUBLIC_LEAD_RATE_LIMIT_PER_MINUTE=8
MAX_UPLOAD_MB=10
```

Never put `DATABASE_URL`, `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`, `ADMIN_PASSWORD`, or PostgreSQL password into Netlify/Vite variables.

## Frontend (Netlify)
- Base directory: `frontend`
- Build command: `npm run build`
- Publish directory: `dist`
- Environment variable:

```env
VITE_API_URL=https://YOUR-RAILWAY-BACKEND.up.railway.app/api/
```

Only `VITE_API_URL` is needed on Netlify.

## Data safety
- All app data is stored in PostgreSQL through `DATABASE_URL`.
- Do not recreate/delete the Railway PostgreSQL service unless you have exported/backed up data.
- Enable Railway backups/snapshots if available for your database.
