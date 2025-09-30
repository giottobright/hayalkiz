import asyncio
import logging
import sys
import uvicorn
from fastapi import FastAPI
from app.main import main as bot_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Minimal health-check HTTP server
app = FastAPI()

@app.get("/")
@app.get("/health")
async def health():
    return {"status": "ok", "service": "hayalkiz-bot"}


async def run_bot():
    """Run the Telegram bot"""
    try:
        logger.info("🤖 Запуск Telegram бота...")
        await bot_main()
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в боте: {e}", exc_info=True)
        # Don't exit, let health server continue running
        logger.warning("⚠️ Бот остановлен, но health-сервер продолжает работу")


async def run_web():
    """Run the health-check web server"""
    try:
        logger.info("🌐 Запуск health-check сервера на порту 8000...")
        config = uvicorn.Config(
            app, 
            host="0.0.0.0", 
            port=8000, 
            log_level="info",
            access_log=True
        )
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА в health-сервере: {e}", exc_info=True)
        raise


async def main():
    """Run both bot and health server concurrently"""
    logger.info("=" * 70)
    logger.info("🚀 ЗАПУСК ПРИЛОЖЕНИЯ HAYALKIZ")
    logger.info("=" * 70)
    
    try:
        await asyncio.gather(
            run_bot(),
            run_web(),
            return_exceptions=True
        )
    except Exception as e:
        logger.error(f"❌ Ошибка в главном процессе: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"❌ ФАТАЛЬНАЯ ОШИБКА: {e}", exc_info=True)
        sys.exit(1)
