# Alif24 ERP — Server Deployment Guide

## Arxitektura

```
/home/ishburiyevnurali/
├── alif-24/              ← TEGMAYMIZ (mavjud loyiha)
│   ├── docker-compose.yml  (postgres, redis, nginx, ...)
│   └── docker/nginx/nginx.conf  (erp.alif24.uz qo'shildi)
│
└── alif24-erp/           ← YANGI (ERP loyiha)
    └── docker-compose.yml  (faqat erp-backend, erp-worker, erp-frontend)
```

**Muhim**: ERP o'zining postgres/redis/nginx yaratmaydi. Mavjud alif-24 konteynerlaridan foydalanadi.

## Serverda qadamlar

### 1. ERP kodini serverga ko'chirish

```bash
cd ~
git clone <erp-repo-url> alif24-erp
# yoki scp/rsync bilan ko'chirish
```

### 2. .env faylini yaratish

```bash
cd ~/alif24-erp
cp .env.server .env
nano .env
```

**MUHIM**: `POSTGRES_PASSWORD` ni alif-24 dagi parol bilan aynan bir xil qiling!
Alif-24 parolni ko'rish uchun:
```bash
cat ~/alif-24/.env | grep POSTGRES_PASSWORD
```

### 3. alif24_erp database yaratish

```bash
cd ~/alif24-erp
chmod +x scripts/*.sh
bash scripts/init-erp-database.sh
```

### 4. Upload papkasini yaratish

```bash
sudo mkdir -p /data/erp-uploads
sudo chown -R $(whoami):$(whoami) /data/erp-uploads
```

### 5. Docker network nomini tekshirish

```bash
docker network ls | grep alif24
```

Agar natija `alif-24_alif24-network` bo'lsa — tayyor.
Agar boshqa nom bo'lsa — `docker-compose.yml` da `name:` ni o'zgartiring.

### 6. ERP ni build va ishga tushirish

```bash
cd ~/alif24-erp
docker compose build
docker compose up -d
```

### 7. Alembic migration

```bash
docker exec erp-backend alembic upgrade head
```

### 8. alif-24 nginx ni yangilash

```bash
cd ~/alif-24
git pull  # nginx.conf yangilangan versiya
docker exec alif24-gateway nginx -s reload
```

### 9. SSL sertifikat (agar wildcard bo'lmasa)

```bash
# Avval HTTP orqali certbot
sudo certbot certonly --webroot -w /var/www/certbot -d erp.alif24.uz

# Yoki mavjud wildcard sertifikat ishlatsa — hech narsa qilish shart emas
```

### 10. Tekshirish

```bash
# Backend health
curl http://localhost:8010/health

# Loglar
docker logs erp-backend --tail 30
docker logs erp-worker --tail 10
docker logs erp-frontend --tail 10

# Database tekshirish
docker exec alif24-postgres psql -U postgres -c '\l' | grep erp
```

## Ma'lumotlar oqimi

```
Foydalanuvchi
    ↓
https://erp.alif24.uz (yoki school1.erp.alif24.uz)
    ↓
alif24-gateway (nginx) — alif-24 docker-compose ichida
    ↓
erp-backend:8000 — alif24-erp docker-compose ichida
    ↓
alif24-postgres → alif24_erp database (ERP ma'lumotlar)
                → alif24 database (faqat O'QISH — foydalanuvchilar, studentlar)
```

## Foydali buyruqlar

```bash
# ERP loglarini ko'rish
docker logs -f erp-backend

# ERP ni to'xtatish (alif-24 ga ta'sir qilmaydi)
cd ~/alif24-erp && docker compose down

# ERP ni qayta build
cd ~/alif24-erp && docker compose build --no-cache && docker compose up -d

# Database tekshirish
docker exec alif24-postgres psql -U postgres -d alif24_erp -c '\dt public.*'
```
