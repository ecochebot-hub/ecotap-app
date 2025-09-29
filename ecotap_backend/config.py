

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env
load_dotenv()

# ================== Telegram ==================
BOT_TOKEN = os.getenv("BOT_TOKEN", "CHANGE_ME")

# ================== Database ==================
class DBConfig:
    # Лучше хранить БД в отдельной папке data/
    PATH = os.getenv("DATABASE_PATH", "data/ecotap.db")

# ================== Game Settings ==================
class GameConfig:
    POINTS_PER_TAP = int(os.getenv("POINTS_PER_TAP", 1))
    POINTS_PER_TREE = int(os.getenv("POINTS_PER_TREE", 1000))
    MAX_ENERGY = int(os.getenv("MAX_ENERGY", 100))
    ENERGY_RESTORE_TIME = int(os.getenv("ENERGY_RESTORE_TIME", 60))  # seconds
