import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- BOT ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(admin_id) for admin_id in ADMIN_IDS_STR.split(",") if admin_id]

# --- DATABASE ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# --- WEBAPP ---
WEBAPP_URL = os.getenv("WEBAPP_URL")
