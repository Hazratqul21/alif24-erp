#!/bin/bash
# Alif24 ERP — mavjud PostgreSQL ichida yangi database yaratish
# Bu skript serverda 1 marta ishlatiladi

set -e

echo "=== Alif24 ERP Database yaratish ==="

# alif-24 postgres konteyneridan foydalanib database yaratamiz
docker exec -i alif24-postgres psql -U postgres <<'SQL'
-- alif24_erp database yaratish (agar mavjud bo'lmasa)
SELECT 'CREATE DATABASE alif24_erp'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'alif24_erp')\gexec

-- Kerakli extensionlarni qo'shish
\c alif24_erp
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
SQL

echo "=== alif24_erp database tayyor! ==="
echo ""
echo "Tekshirish:"
echo "  docker exec alif24-postgres psql -U postgres -c '\\l' | grep alif24_erp"
