from aiogram import Router
from aiogram.types import Message, WebAppInfo
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import db
from utils.texts import format_welcome_message
from config import WEBAPP_URL

router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with the `/start` command,
    registers the user, and shows their progress.
    """
    user = message.from_user
    
    # Register or update user info in the database
    await db.register_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Get user progress
    progress = await db.get_user_progress(user.id)
    
    # Create the inline keyboard with the "Play Game" button
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🎮 Play EcoTap", 
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    
    # Format the welcome message
    welcome_text = format_welcome_message(user.first_name, progress)
    
    await message.answer(
        welcome_text,
        reply_markup=builder.as_markup()
    )
