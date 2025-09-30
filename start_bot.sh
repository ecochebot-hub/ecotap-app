#!/data/data/com.termux/files/usr/bin/bash

# Navigate to bot directory
cd ~/ecotap-app

# Activate virtual environment (if using)
# source venv/bin/activate

# Start PostgreSQL
pg_ctl -D $PREFIX/var/lib/postgresql start

# Wait for PostgreSQL to start
sleep 3

# Start bot
python bot.py
