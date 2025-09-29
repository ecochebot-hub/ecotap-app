#!/bin/bash
set -e

# Находим URL туннеля в логах cloudflared
URL=$(grep -o "https://[a-zA-Z0-9.-]*trycloudflare.com" tunnel.log | tail -n 1)

if [ -z "$URL" ]; then
  echo "❌ URL не найден в tunnel.log"
  exit 1
fi

echo "🌍 Новый URL: $URL"

# Подставляем в index.html
sed -i "s|http://127.0.0.1:8080|$URL|g" ../index.html
sed -i "s|https://.*trycloudflare.com|$URL|g" ../index.html

echo "✅ index.html обновлён"

# Коммитим и пушим в GitHub
cd ..
git add index.html
git commit -m "Update API_BASE to $URL"
git push origin main

echo "🚀 Обновлённый фронтенд задеплоен с новым API URL"
