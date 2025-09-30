import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from database import db
from handlers import start, callbacks, game
from middlewares.throttling import ThrottlingMiddleware, AntiFloodMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


async def on_startup():
    """Actions on bot startup"""
    logger.info("🚀 Starting EcoTap Bot...")
    
    # Initialize database
    try:
        await db.init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"✅ Bot started: @{bot_info.username}")
    logger.info(f"Bot ID: {bot_info.id}")
    
    # Optional: Send notification to admin
    from config import ADMIN_IDS
    if ADMIN_IDS:
        try:
            for admin_id in ADMIN_IDS:
                await bot.send_message(
                    admin_id,
                    "🤖 <b>EcoTap Bot Started!</b>\n\n"
                    f"Bot: @{bot_info.username}\n"
                    f"Status: ✅ Online"
                )
        except Exception as e:
            logger.warning(f"Failed to notify admin: {e}")


async def on_shutdown():
    """Actions on bot shutdown"""
    logger.info("⏹ Shutting down EcoTap Bot...")
    
    # Close database connection
    await db.close()
    logger.info("✅ Database connection closed")
    
    # Close bot session
    await bot.session.close()
    logger.info("✅ Bot session closed")
    
    # Optional: Send notification to admin
    from config import ADMIN_IDS
    if ADMIN_IDS:
        try:
            for admin_id in ADMIN_IDS:
                await bot.send_message(
                    admin_id,
                    "🤖 <b>EcoTap Bot Stopped</b>\n\n"
                    "Status: ⏹ Offline"
                )
        except:
            pass


async def main():
    """Main function"""
    try:
        # Register middlewares
        dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
        dp.callback_query.middleware(ThrottlingMiddleware(rate_limit=0.3))
        dp.message.middleware(AntiFloodMiddleware(time_window=60, max_messages=20))
        
        # Register routers
        dp.include_router(start.router)
        dp.include_router(callbacks.router)
        dp.include_router(game.router)
        
        logger.info("✅ Handlers registered")
        
        # Startup
        await on_startup()
        
        # Start polling
        logger.info("🔄 Starting polling...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        raise
    finally:
        await on_shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹ Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
