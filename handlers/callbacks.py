# handlers/callbacks.py
from aiogram import Router
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query()
async def handle_callback(query: CallbackQuery):
    """
    This is a placeholder for handling callback queries.
    For example, from inline keyboards.
    """
    # You can answer the callback query to remove the "loading" state on the button
    await query.answer("Button pressed!")
    
    # Example of handling specific data
    # if query.data == "show_leaderboard":
    #     await query.message.answer("Here is the leaderboard...")
