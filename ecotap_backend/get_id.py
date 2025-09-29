import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = "8356742618:AAHhq2wGaBOOw8uRFUBKZFjcDoXmAFvUbWg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def send_id(message: types.Message):
    user_id = message.from_user.id
    await message.answer(f"✅ Ваш Telegram ID: {user_id}")
    print(f"Ваш Telegram ID: {user_id}")
    await bot.session.close()
    raise SystemExit

async def main():
    print("🤖 Напиши /start боту, чтобы получить свой Telegram ID")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
