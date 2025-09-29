#!/bin/bash
# 🚀 Стартовый скрипт для EcoTap
# Останавливает старые процессы и запускает новые

echo "⛔ Останавливаю старые процессы..."
pkill -f "uvicorn"
pkill -f "bot.py"
pkill -f "cloudflared"

sleep 2

echo "🌱 Запускаю EcoTapBot и API..."

# Запуск API (FastAPI + Uvicorn)
uvicorn api:app --host 0.0.0.0 --port 8080 > api.log 2>&1 &

# Запуск Telegram Bot
python bot.py > bot.log 2>&1 &

# Запуск Cloudflared (туннель)
cloudflared tunnel --url http://localhost:8080 > tunnel.log 2>&1 &

echo "✅ Всё запущено!"
echo "👉 Логи: tail -f bot.log | tail -f api.log | tail -f tunnel.log"
