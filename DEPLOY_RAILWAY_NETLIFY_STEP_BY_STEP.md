# Aziz Academy Operators — Railway + Netlify deploy

## Tuzilma

- `backend/` — Django + PostgreSQL API. Railwayga deploy qilinadi.
- `frontend/` — Vue/Vite admin panel. Netlifyga deploy qilinadi.

## 1) GitHubga yuklashdan oldin

`.env`, `node_modules`, `dist`, `__pycache__` yuklanmasin. Bu ZIPda ular tozalangan.

## 2) Railway backend

Railway project ichida avval PostgreSQL qo‘shing, keyin shu repo ichidan backend service yarating.

Railway backend service sozlamalari:

```text
Root Directory: backend
Start Command: python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py init_db && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers ${WEB_CONCURRENCY:-2} --threads 4 --timeout 120
Healthcheck Path: /api/health/
```

Backend Variables uchun `backend/.env.railway.example` ichidagi qiymatlardan foydalaning.

Eng muhimlari:

```env
NODE_ENV=production
DEBUG=False
DATABASE_URL=${{Postgres.DATABASE_URL}}
DB_SSL_REQUIRE=true
ALLOWED_HOSTS=.up.railway.app
CORS_ALLOWED_ORIGINS=https://azizacademyoperators.netlify.app
CSRF_TRUSTED_ORIGINS=https://azizacademyoperators.netlify.app
```

Agar Railway PostgreSQL service nomi `Postgres` bo‘lmasa, `DATABASE_URL=${{Postgres.DATABASE_URL}}` ichidagi `Postgres` nomini o‘sha service nomiga almashtiring.

Backend ishlayotganini tekshirish:

```text
https://YOUR-BACKEND.up.railway.app/api/health/
```

## 3) Netlify frontend

Netlify sozlamalari:

```text
Base directory: frontend
Build command: npm run build
Publish directory: dist
```

Netlify Variables ichiga faqat shu kerak:

```env
VITE_API_URL=https://YOUR-BACKEND.up.railway.app/api/
```

Netlifyga `DATABASE_URL`, `SECRET_KEY`, `JWT_*`, `ADMIN_PASSWORD`, `TELEGRAM_BOT_TOKEN` yozilmaydi.

## 4) Admin login

Birinchi deployda admin `ADMIN_USERNAME` va `ADMIN_PASSWORD` bo‘yicha yaratiladi.

```text
Login: admin
Parol: Railway Variables ichidagi ADMIN_PASSWORD
```

Agar database oldin yaratilgan bo‘lsa, admin parol avtomatik o‘zgarmaydi. Bunday holatda yangi admin yaratish yoki parolni database orqali almashtirish kerak.

## 5) Telegram notification

Backend Variables:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_group_or_user_chat_id
TELEGRAM_CHAT_IDS=
```

Bir nechta chat uchun:

```env
TELEGRAM_CHAT_IDS=-1001111111111,-1002222222222
```

## 6) Xavfsizlik

- `.env` GitHubga chiqmasin.
- `SECRET_KEY`, `JWT_ACCESS_SECRET`, `JWT_REFRESH_SECRET` uzun random bo‘lsin.
- `CORS_ALLOWED_ORIGINS` faqat Netlify domen bo‘lsin.
- Database faqat Railway backend Variables ichida bo‘lsin.
- Railway PostgreSQL backup yoqib qo‘yilsin.
