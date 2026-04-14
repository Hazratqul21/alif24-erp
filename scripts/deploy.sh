#!/bin/bash
# Alif24 ERP — To'liq deploy skripti
# Serverda birinchi marta ishlatish uchun

set -e

echo "============================================"
echo "  Alif24 ERP — Server Deployment"
echo "============================================"
echo ""

# 1. Tekshiruvlar
echo "[1/7] Tekshiruvlar..."
if ! docker ps | grep -q "alif24-postgres"; then
    echo "XATO: alif24-postgres konteyneri ishlamayapti!"
    echo "Avval alif-24 ni ishga tushiring: cd ~/alif-24 && docker compose up -d"
    exit 1
fi

if ! docker ps | grep -q "alif24-redis"; then
    echo "XATO: alif24-redis konteyneri ishlamayapti!"
    exit 1
fi

if ! docker ps | grep -q "alif24-gateway"; then
    echo "XATO: alif24-gateway (nginx) konteyneri ishlamayapti!"
    exit 1
fi

echo "  alif24-postgres ✓"
echo "  alif24-redis ✓"
echo "  alif24-gateway ✓"

# 2. .env fayl tekshirish
echo ""
echo "[2/7] .env faylini tekshirish..."
if [ ! -f .env ]; then
    echo "XATO: .env fayl topilmadi!"
    echo "  cp .env.server .env"
    echo "  nano .env  # parollarni to'ldiring"
    exit 1
fi
echo "  .env fayl mavjud ✓"

# 3. Database yaratish
echo ""
echo "[3/7] alif24_erp database yaratish..."
bash scripts/init-erp-database.sh

# 4. Upload papkasini yaratish
echo ""
echo "[4/7] Upload papkasi..."
sudo mkdir -p /data/erp-uploads
sudo chown -R $(whoami):$(whoami) /data/erp-uploads
echo "  /data/erp-uploads ✓"

# 5. Docker network tekshirish
echo ""
echo "[5/7] Docker network tekshirish..."
NETWORK_NAME=$(docker network ls --format '{{.Name}}' | grep alif24-network | head -1)
if [ -z "$NETWORK_NAME" ]; then
    echo "XATO: alif24-network topilmadi!"
    exit 1
fi
echo "  Network: $NETWORK_NAME ✓"

# docker-compose.yml da network nomini yangilash (agar kerak bo'lsa)
if [ "$NETWORK_NAME" != "alif-24_alif24-network" ]; then
    echo "  Network nomi boshqacha: $NETWORK_NAME"
    echo "  docker-compose.yml ni yangilash..."
    sed -i "s|name: alif-24_alif24-network|name: $NETWORK_NAME|g" docker-compose.yml
fi

# 6. Build va Start
echo ""
echo "[6/7] Docker build va start..."
docker compose build --no-cache
docker compose up -d

# 7. Status
echo ""
echo "[7/7] Konteynerlar holati..."
sleep 5
docker compose ps

echo ""
echo "============================================"
echo "  DEPLOY TUGADI!"
echo "============================================"
echo ""
echo "Keyingi qadamlar:"
echo "  1. Alembic migration: docker exec erp-backend alembic upgrade head"
echo "  2. alif-24 nginx konfiguratsiyasini yangilang (erp.alif24.uz qo'shing)"
echo "  3. SSL sertifikat: sudo certbot certonly --webroot -w /var/www/certbot -d erp.alif24.uz"
echo "  4. Nginx reload: docker exec alif24-gateway nginx -s reload"
echo ""
echo "Tekshirish:"
echo "  curl http://localhost:8010/health"
echo "  docker logs erp-backend --tail 20"
