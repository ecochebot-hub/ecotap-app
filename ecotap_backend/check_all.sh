#!/bin/bash
echo "🔍 Проверка статуса EcoTap..."

# Проверка API (uvicorn)
if pgrep -f "uvicorn api:app" > /dev/null; then
    echo "✅ API (uvicorn) работает"
else
    echo "❌ API (uvicorn) не запущен"
fi

# Проверка бота (bot.py)
if pgrep -f "bot.py" > /dev/null; then
    echo "✅ Bot (bot.py) работает"
else
    echo "❌ Bot (bot.py) не запущен"
fi

# Проверка туннеля (cloudflared)
if pgrep -f "cloudflared tunnel" > /dev/null; then
    echo "✅ Cloudflare Tunnel работает"

    # Попытка найти активный URL из логов
    url=$(grep -oE "https://[0-9a-zA-Z.-]+\.trycloudflare\.com" tunnel.log | tail -n 1)
    if [ -n "$url" ]; then
        echo "🌍 Внешний доступ: $url"
    else
        echo "🌍 URL туннеля не найден в tunnel.log"
    fi
else
    echo "❌ Cloudflare Tunnel не запущен"
fi

echo "ℹ️ Для логов: tail -f api.log | tail -f bot.log | tail -f tunnel.log"
