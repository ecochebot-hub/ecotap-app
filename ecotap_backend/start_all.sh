#!/data/data/com.termux/files/usr/bin/bash
# 🚀 Универсальный запуск EcoTap (бот + API + туннель)

echo "⛔ Останавливаю старые процессы..."
pkill -f uvicorn
pkill -f bot.py
pkill -f cloudflared

sleep 2

echo "🌱 Запускаю API (uvicorn)..."
uvicorn api:app --host 0.0.0.0 --port 8080 > api.log 2>&1 &

echo "🤖 Запускаю бота..."
python bot.py > bot.log 2>&1 &

echo "🌍 Запускаю Cloudflare Tunnel..."
cloudflared tunnel --url http://localhost:8080 --no-autoupdate > tunnel.log 2>&1 &

sleep 3

echo "✅ Всё запущено!"
echo "👉 Логи: tail -f api.log | tail -f bot.log | tail -f tunnel.log"
