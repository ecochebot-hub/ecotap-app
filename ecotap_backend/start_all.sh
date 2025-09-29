#!/bin/bash

echo "⛔ Останавливаю старые процессы..."
pkill -f "uvicorn" 2>/dev/null
pkill -f "bot.py" 2>/dev/null
pkill -f "cloudflared" 2>/dev/null
sleep 2

echo "🌱 Запускаю API (uvicorn)..."
nohup uvicorn api:app --host 0.0.0.0 --port 8080 > api.log 2>&1 &

echo "🤖 Запускаю бота..."
nohup python bot.py > bot.log 2>&1 &

echo "🌍 Запускаю Cloudflare Tunnel..."
nohup cloudflared tunnel --url http://localhost:8080 --no-autoupdate > tunnel.log 2>&1 &

sleep 8  # ждём пока tunnel.log появится URL

# Ищем URL в tunnel.log
URL=$(grep -oE "https://[a-zA-Z0-9.-]+\.trycloudflare.com" tunnel.log | tail -n 1)

if [ -n "$URL" ]; then
    echo "🌍 Найден новый URL: $URL"
    # Обновляем index.html
    sed -i "s|const API_BASE = .*|const API_BASE = '${URL}';|" ~/ecotap-app/index.html
    echo "✅ index.html обновлён с новым API_BASE"
else
    echo "❌ Не удалось найти URL в tunnel.log"
fi

echo "✅ Всё запущено!"
echo "👉 Логи: tail -f api.log | tail -f bot.log | tail -f tunnel.log"
