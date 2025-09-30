#!/bin/bash

echo "⛔ Останавливаю старые процессы..."
# Убиваем все старые процессы, чтобы избежать конфликтов
pkill -f "uvicorn api:app"
pkill -f "python bot.py"
pkill -f "cloudflared"
pkill -f "python -m http.server"
sleep 2

# --- БЭКЕНД ---
echo "🌱 Запускаю API (uvicorn) на порту 8080..."
nohup uvicorn api:app --host 0.0.0.0 --port 8080 > api.log 2>&1 &
sleep 2

echo "🤖 Запускаю бота..."
nohup python bot.py > bot.log 2>&1 &
sleep 2

echo "🌍 Запускаю Cloudflare Tunnel для API..."
nohup cloudflared tunnel --url http://localhost:8080 > tunnel.log 2>&1 &

# --- ФРОНТЕНД ---
echo "🎨 Запускаю сервер для фронтенда на порту 8081..."
# Запускаем сервер в папке, где лежит index.html
(cd ~/ecotap-app && nohup python -m http.server 8081 > ~/ecotap-app/frontend.log 2>&1 &)
sleep 2

echo "🌐 Запускаю Cloudflare Tunnel для ФРОНТЕНДА..."
nohup cloudflared tunnel --url http://localhost:8081 > ~/ecotap-app/frontend_tunnel.log 2>&1 &

# --- СИНХРОНИЗАЦИЯ ---
echo "⏳ Жду 8 секунд, пока туннели поднимутся..."
sleep 8

# Достаём URL бэкенда и обновляем index.html
BACKEND_URL=$(grep -oE "https://[a-zA-Z0-9.-]+\.trycloudflare.com" tunnel.log | head -n1)

if [ -n "$BACKEND_URL" ]; then
    echo "🌍 API URL: $BACKEND_URL"
    sed -i "s|const API_BASE = .*|const API_BASE = '$BACKEND_URL';|" ~/ecotap-app/index.html
    echo "✅ index.html обновлён с адресом API"
else
    echo "❌ Не удалось найти URL бэкенда в tunnel.log"
fi

# Достаём URL фронтенда и показываем его пользователю
FRONTEND_URL=$(grep -oE "https://[a-zA-Z0-9.-]+\.trycloudflare.com" ~/ecotap-app/frontend_tunnel.log | head -n1)

if [ -n "$FRONTEND_URL" ]; then
    echo "=============================================================="
    echo "🔴 ВАЖНО! Ссылка для @BotFather:"
    echo "   $FRONTEND_URL"
    echo "=============================================================="
else
    echo "❌ Не удалось найти URL фронтенда в frontend_tunnel.log"
fi

echo "✅ Всё запущено!"

