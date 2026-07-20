# Deploy: Django backend Railway + Vue frontend Netlify

1. GitHub repo ichida `backend` va `frontend` papkalari tursin.
2. Railway project oching va PostgreSQL qo'shing.
3. Railway'da backend service yarating:
   - Root Directory: `backend`
   - Start Command: `python manage.py init_db && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
4. Railway Variables ichiga backend envlarni kiriting.
5. Railway backend domainini tekshiring: `/api/health/`.
6. Netlify'da frontend deploy qiling:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `dist`
7. Netlify env: `VITE_API_URL=https://backend-domain.up.railway.app/api/`.
8. Railway CORS: `CORS_ALLOWED_ORIGINS=https://azizacademyoperators.netlify.app`.

Muhim: secretlar faqat Railway backend Variables ichida bo'ladi.
