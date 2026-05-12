# Saqlash va xavfsizlik bo‘yicha kiritilgan o‘zgarishlar

## Ma’lumot yo‘qolmasligi uchun

- Operator statusni har safar o‘zgartirsa, `lead_status_history` jadvaliga yangi qator yoziladi.
- Oldingi statuslar ustidan yozib yuborilmaydi.
- User delete qilinsa ham database’dan o‘chmaydi: `is_active=false` bo‘ladi.
- Excel import qilingan har bir qator `excel_import_rows` jadvalida JSON ko‘rinishida saqlanadi.
- Excelda dublikat kelsa ham lead saqlanadi, faqat `is_duplicate=true` belgilanadi.
- Filial rahbari qaror o‘zgartirsa, eski/yangisi `lead_visit_decision_history`ga tushadi.
- User update/deactivate, lead status va reminder o‘zgarishlari `data_audit_logs`ga yoziladi.

## Ma’lumot ochilib ketmasligi uchun

- `.env` fayllar ZIP/GitHubdan chiqarildi, faqat `.env.example` qoldi.
- Productionda kuchsiz JWT secret yoki admin parol bilan backend ishga tushmaydi.
- CORS productionda bo‘sh qolsa backend frontendga ochilmaydi.
- CORS `*` qo‘yilmasligi kerak.
- Security headerlar qo‘shildi.
- Login rate limit qo‘shildi.
- Public online lead formaga rate limit qo‘shildi.
- Excel upload faqat `.xlsx` bo‘lishi kerak.
- Upload hajmi default 10 MB.
- Backend Railway portida `0.0.0.0`da eshitadi.
