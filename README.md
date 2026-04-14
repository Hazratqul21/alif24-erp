# Alif24 School ERP

Multi-tenant maktab boshqaruv tizimi. FastAPI + React + PostgreSQL (schema-per-tenant).

## Arxitektura

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18+ (Vite + Tailwind CSS)
- **Database**: PostgreSQL 15+ (schema-per-tenant)
- **Cache/Queue**: Redis + Celery
- **Gateway**: Nginx (wildcard subdomain)

## Tez boshlash

```bash
# .env faylni yaratish
cp .env.example .env
# .env faylni tahrirlash

# Docker bilan ishga tushirish
docker compose up -d

# Yoki lokal ishga tushirish
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010

# Frontend
cd frontend
npm install
npm run dev
```

## Modullar (23+)

1. Foydalanuvchilar va rollar (RBAC)
2. Davomat (QR, RFID)
3. Dars jadvali
4. Baholar va reyting
5. Imtihonlar (onlayn)
6. Uy vazifalari
7. Musobaqalar va tadbirlar
8. Hujjatlar arxivi
9. To'lovlar (Payme, Click, Uzum)
10. Kutubxona (markaziy + maktab)
11. Tibbiyot
12. Intizom jurnali
13. Oshxona
14. Transport (GPS)
15. Bildirishnomalar (SMS, Email, Push)
16. Hisobotlar va tahlil
17. Tizim loglari
18. Qabul (onlayn ariza)
19. Xona band qilish
20. Portfolio
21. So'rovnomalar
22. Audit log
23. Ko'p tillilik (UZ/RU/EN)

## Rollar (19+)

Super Admin, Direktor, Administrator, Direktor o'rinbosarlari, Sinf rahbari, Fan bo'limi rahbari, O'qituvchi, O'quvchi, Ota-ona, Buxgalter, Tibbiyot xodimi, Psixolog, Kutubxonachi, IT Admin, Oshxona mudiri, Transport bo'limi, Qo'riqchi, Ota-onalar kengashi, Bitiruvchi.

## API dokumentatsiya

`http://localhost:8010/docs` (Swagger UI)
`http://localhost:8010/redoc` (ReDoc)
