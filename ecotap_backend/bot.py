import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import BOT_TOKEN
from database import db
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_tunnel_url():
    """Читает последний URL из tunnel.log"""
    try:
        with open("tunnel.log", "r") as f:
            lines = f.readlines()
            for line in reversed(lines):
                if "trycloudflare.com" in line:
                    url = line.split()[-1]
                    if url.startswith("https://"):
                        return url
    except Exception as e:
        logging.warning(f"Tunnel URL not найден: {e}")
    return "https://example.com"  # fallback

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Обработчик /start"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Регистрируем пользователя
    is_new_user = await db.register_user(user_id, username, first_name, last_name)

    # Получаем актуальный URL туннеля
    tunnel_url = get_tunnel_url()
    webapp_button = InlineKeyboardButton(
        text="🌱 Play EcoTap",
        web_app=WebAppInfo(url=tunnel_url)
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[webapp_button]])

    if is_new_user:
        welcome_text = (
            f"🌿 Добро пожаловать в EcoTap, {first_name}!\n\n"
            "🎮 Тапай, зарабатывай очки и выращивай виртуальный лес!\n"
            "💧 Каждый тап = 1 очко\n"
            "🌳 1000 очков = 1 дерево\n"
            "⚡ Энергия восстанавливается со временем\n\n"
            "Нажми кнопку ниже, чтобы начать игру!"
        )
    else:
        progress = await db.get_user_progress(user_id)
        if progress:
            welcome_text = (
                f"🌿 С возвращением, {first_name}!\n\n"
                f"📊 Твой прогресс:\n"
                f"🌳 Деревьев: {progress['trees']}\n"
                f"💰 Очков: {progress['points']}\n"
                f"⭐ Уровень: {progress['level']}\n"
                f"⚡ Энергия: {progress['energy']}/100\n"
                f"👆 Всего тапов: {progress['total_taps']}\n\n"
                "Продолжай выращивать свой лес!"
            )
        else:
            welcome_text = "🌿 Добро пожаловать в EcoTap! Нажми кнопку ниже, чтобы начать игру!"

    await message.answer(welcome_text, reply_markup=keyboard)

async def main():
    await db.init_db()
    print("🤖 EcoTap бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
