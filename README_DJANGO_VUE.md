# Aziz Academy Operators — Django backend + Vue frontend

Bu versiyada backend Node.js emas, Django bilan qayta yozilgan. Frontend Vue/Vite holicha qoldi va API endpointlar eski frontend bilan mos qilindi.

## Local ishga tushirish

### Backend

```powershell
cd backend
copy .env.example .env
pip install -r requirements.txt
python manage.py init_db
python manage.py runserver 127.0.0.1:8000
```

`backend/.env` ichida `DATABASE_URL` ni o'zingizning PostgreSQL parolingiz bilan to'g'rilang:

```env
DATABASE_URL=postgresql://postgres:PAROL@localhost:5432/azizacademyoperators
DB_SSL_REQUIRE=false
```

Tekshirish:

```text
http://127.0.0.1:8000/api/health/
```

### Frontend

```powershell
cd frontend
copy .env.example .env
npm ci
npm run dev
```

`frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api/
```

Sayt:

```text
http://localhost:5173
```

## Railway backend

Railway backend service:

```text
Root Directory: backend
Start Command: python manage.py init_db && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Variables:

```env
NODE_ENV=production
DEBUG=false
SECRET_KEY=UZUN_DJANGO_SECRET
TIME_ZONE=Asia/Tashkent
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_SSL_REQUIRE=true
CORS_ALLOWED_ORIGINS=https://azizacademyoperators.netlify.app
JWT_ACCESS_SECRET=UZUN_RANDOM_SECRET
JWT_REFRESH_SECRET=BOSHQA_UZUN_RANDOM_SECRET
ACCESS_TOKEN_EXPIRES_IN=30m
REFRESH_TOKEN_EXPIRES_IN=7d
ADMIN_USERNAME=admin
ADMIN_PASSWORD=KUCHLI_PAROL
ADMIN_FULL_NAME=Administrator
ADMIN_PHONE=
MAX_UPLOAD_MB=10
```

## Netlify frontend

```text
Base directory: frontend
Build command: npm run build
Publish directory: dist
```

Netlify env:

```env
VITE_API_URL=https://SIZNING-RAILWAY-BACKEND.up.railway.app/api/
```

Netlify'ga `DATABASE_URL`, `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET`, `ADMIN_PASSWORD` yozilmaydi.
