#!/data/data/com.termux/files/usr/bin/bash

# Пути
FRONTEND_HTML=~/ecotap-app/index.html
BACKEND_LOG=~/ecotap-app/ecotap_backend/tunnel.log

# Достаём последний URL из логов Cloudflare
NEW_URL=$(grep -oP "https://[a-zA-Z0-9.-]+\.trycloudflare\.com" "$BACKEND_LOG" | tail -n 1)

if [ -z "$NEW_URL" ]; then
  echo "❌ Не удалось найти URL в $BACKEND_LOG"
  exit 1
fi

# Обновляем API_BASE в index.html
sed -i "s|const API_BASE = '.*'|const API_BASE = '$NEW_URL';|" "$FRONTEND_HTML"

echo "✅ API_BASE обновлён на $NEW_URL"
