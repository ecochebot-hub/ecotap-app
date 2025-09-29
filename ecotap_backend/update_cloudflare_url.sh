#!/usr/bin/env bash
set -e

LOGFILE="$PWD/tunnel.log"
FRONTEND_HTML="$HOME/ecotap-app/index.html"
BACKUP_HTML="$HOME/ecotap-app/index.html.bak"

if [ ! -f "$LOGFILE" ]; then
  echo "tunnel.log не найден по пути: $LOGFILE"
  echo "Откройте отдельное окно и выполните: tail -f $LOGFILE"
  exit 1
fi

# Попробуем сначала найти trycloudflare URL (обычный формат)
URL=$(grep -Eo 'https?://[^ ]+' "$LOGFILE" | grep -m1 -E 'trycloudflare|trycloudflare\.com' || true)

# Если не нашли, возьмём первое https:// из лога
if [ -z "$URL" ]; then
  URL=$(grep -Eo 'https?://[^ ]+' "$LOGFILE" | head -n1 || true)
fi

if [ -z "$URL" ]; then
  echo "Не удалось автоматически найти публичный URL в $LOGFILE."
  echo "Откройте лог туннеля: tail -f $LOGFILE и найдите строку вида https://<xxx>.trycloudflare.com"
  exit 1
fi

echo "Найден URL: $URL"

# Бэкап index.html
if [ -f "$FRONTEND_HTML" ]; then
  cp -v "$FRONTEND_HTML" "$BACKUP_HTML"
  echo "Создан бэкап: $BACKUP_HTML"
else
  echo "Файл $FRONTEND_HTML не найден."
  exit 1
fi

# Подставляем URL в index.html: ищем API_BASE или http://127.0.0.1:8000 и заменяем
# поддерживаем несколько вариантов
sed -i -E "s|(const API_BASE = )(['\"]).*?(['\"]);\s*|\1'\2${URL}\3;|g" "$FRONTEND_HTML" 2>/dev/null || true

# Более надёжная замена под знакомым вариантом
sed -i "s|http://127.0.0.1:8000|$URL|g" "$FRONTEND_HTML" || true
sed -i "s|http://localhost:8000|$URL|g" "$FRONTEND_HTML" || true
sed -i "s|http://127.0.0.1:8080|$URL|g" "$FRONTEND_HTML" || true
sed -i "s|http://localhost:8080|$URL|g" "$FRONTEND_HTML" || true

echo "index.html обновлён. Проверьте изменения:"
echo "-----------------------------------------"
grep -n "API_BASE" -n "$FRONTEND_HTML" || true
echo "Перезапустите браузер WebApp (в самом Telegram нажмите стрелку вниз → Reload) или закройте/откройте WebApp."
