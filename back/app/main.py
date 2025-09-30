

import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from .config import get_settings
from .db import init_db, set_persona as db_set_persona, get_persona as db_get_persona, add_message, get_recent_messages
from .personas import get_persona, PERSONAS
from .services_gpt import GPTService
from .services_flux import FluxService

# Configure logging
logger = logging.getLogger(__name__)

logger.info("📋 Загрузка конфигурации...")
settings = get_settings()

# Validate settings
if not settings.telegram_bot_token:
    logger.error("❌ TELEGRAM_BOT_TOKEN не установлен!")
    raise ValueError("TELEGRAM_BOT_TOKEN is required")
if not settings.openai_api_key:
    logger.error("❌ OPENAI_API_KEY не установлен!")
    raise ValueError("OPENAI_API_KEY is required")

logger.info(f"✅ Конфигурация загружена:")
logger.info(f"   - Bot token: {settings.telegram_bot_token[:10]}...")
logger.info(f"   - OpenAI key: {settings.openai_api_key[:10]}...")
logger.info(f"   - WebApp URL: {settings.webapp_url}")
logger.info(f"   - Database: {settings.database_path}")

logger.info("🤖 Инициализация бота...")
bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

logger.info("🧠 Инициализация GPT сервиса...")
gpt_service = GPTService()
logger.info("🎨 Инициализация Flux сервиса...")
flux_service = FluxService()


def webapp_keyboard() -> ReplyKeyboardMarkup:
    # Use a placeholder HTTPS URL for development
    webapp_url = settings.webapp_url
    if webapp_url.startswith("http://localhost"):
        # For development, use a placeholder HTTPS URL
        webapp_url = "https://example.com"  # Placeholder
    
    wa = WebAppInfo(url=webapp_url)
    btn = KeyboardButton(text="Mini Uygulama / Мини-приложение", web_app=wa)
    return ReplyKeyboardMarkup(keyboard=[[btn]], resize_keyboard=True)


def persona_selection_keyboard() -> InlineKeyboardMarkup:
    """Fallback keyboard with persona selection buttons"""
    buttons = []
    for persona in PERSONAS.values():
        buttons.append([
            InlineKeyboardButton(
                text=f"{persona.name_tr} / {persona.name_ru}",
                callback_data=f"select_persona:{persona.code}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    logger.info(f"👤 /start от пользователя {user_id} (@{username})")
    
    text = (
        "Merhaba! Benimle hayalindeki kızı seç ve sohbet etmeye başla.\n"
        "Tüm mesajlar önce Türkçe, sonra aynı mesajda Rusça kopyalanır.\n\n"
        "Привет! Выбери девушку из каталога и начни общение.\n"
        "Все сообщения сначала на турецком, затем дублируются на русском."
    )
    
    # Try WebApp keyboard first, fallback to inline keyboard
    try:
        await message.answer(text, reply_markup=webapp_keyboard())
        logger.info(f"✅ Отправлена WebApp клавиатура пользователю {user_id}")
    except Exception as e:
        logger.warning(f"⚠️ WebApp не сработал для {user_id}, используем inline: {e}")
        # If WebApp fails, use inline keyboard
        await message.answer(
            text + "\n\nMini App недоступен, выберите девушку ниже:",
            reply_markup=persona_selection_keyboard()
        )


@dp.callback_query(lambda c: c.data.startswith("select_persona:"))
async def on_persona_selection(callback_query):
    """Handle persona selection from inline keyboard"""
    user_id = callback_query.from_user.id
    persona_code = callback_query.data.split(":")[1]
    logger.info(f"💃 Пользователь {user_id} выбрал персону: {persona_code}")
    
    persona = get_persona(persona_code)
    
    if persona:
        db_set_persona(str(callback_query.from_user.id), persona.code)
        logger.info(f"✅ Персона {persona_code} установлена для {user_id}")
        await callback_query.message.edit_text(
            f"Seçildi: {persona.name_tr} — {persona.tagline_tr}.\n"
            "Sohbete başlayabiliriz! 'selfie' istersen söyle.\n\n"
            f"Выбрана: {persona.name_ru} — {persona.tagline_ru}.\n"
            "Можем начинать! Если хочешь 'селфи' — скажи."
        )
    else:
        logger.warning(f"⚠️ Неверная персона {persona_code} от {user_id}")
        await callback_query.answer("Geçersiz seçim / Неверный выбор")


@dp.message(F.web_app_data)
async def on_webapp_data(message: Message):
    user_id = message.from_user.id
    logger.info(f"📱 WebApp данные от пользователя {user_id}")
    
    try:
        data = message.web_app_data.data
        import json
        payload = json.loads(data)
        code = str(payload.get("persona", "")).lower()
        logger.info(f"   Выбрана персона: {code}")
        
        persona = get_persona(code)
        if not persona:
            logger.warning(f"⚠️ Персона {code} не найдена для {user_id}")
            await message.answer(
                "Seçim anlaşılamadı. Lütfen tekrar deneyin.\n\nВыбор не распознан. Попробуйте ещё раз."
            )
            return
        db_set_persona(str(message.from_user.id), persona.code)
        logger.info(f"✅ Персона {code} установлена через WebApp для {user_id}")
        
        await message.answer(
            (
                f"Seçildi: {persona.name_tr} — {persona.tagline_tr}.\n"
                "Sohbete başlayabiliriz! 'selfie' istersen söyle.\n\n"
                f"Выбрана: {persona.name_ru} — {persona.tagline_ru}.\n"
                "Можем начинать! Если хочешь 'селфи' — скажи."
            ),
            reply_markup=webapp_keyboard(),
        )
    except Exception as e:
        logger.error(f"❌ Ошибка обработки WebApp данных от {user_id}: {e}", exc_info=True)
        await message.answer(
            "Bir hata oluştu, tekrar dener misin?\n\nПроизошла ошибка, попробуйте ещё раз."
        )


@dp.message()
async def on_message(message: Message):
    user_id = str(message.from_user.id)
    user_text = message.text or ""
    logger.info(f"💬 Сообщение от {user_id}: {user_text[:50]}...")
    
    code = db_get_persona(user_id)
    if not code:
        logger.info(f"⚠️ У пользователя {user_id} не выбрана персона")
        await message.answer(
            "Önce bir kız seç.\n\nСначала выбери девушку.",
            reply_markup=persona_selection_keyboard(),
        )
        return
    
    persona = get_persona(code)
    assert persona is not None
    logger.info(f"👤 Текущая персона для {user_id}: {persona.code}")

    if any(k in user_text.lower() for k in ["selfie", "селфи", "foto", "фото"]):
        logger.info(f"📸 Запрос селфи от {user_id}")
        prompt = (
            f"{persona.name_tr} stilinde, {persona.tagline_tr} havasında bir selfie."
            " Doğal ışık, portre."
        )
        try:
            data_uri = await flux_service.generate_photo_data_uri(prompt)
            if data_uri:
                logger.info(f"✅ Селфи сгенерировано для {user_id}")
                await message.answer(
                    "İşte istediğin selfie!\n\nВот запрошенное селфи!"
                )
                await message.answer_photo(photo=data_uri)
            else:
                logger.warning(f"⚠️ Генерация селфи не удалась для {user_id}")
                await message.answer(
                    "Şu anda foto üretimi hazır değil. Yakında aktif olacak.\n\nГенерация фото пока недоступна. Скоро включим."
                )
        except Exception as e:
            logger.error(f"❌ Ошибка генерации селфи для {user_id}: {e}", exc_info=True)
            await message.answer(
                "Şu anda foto üretimi hazır değil. Yakında aktif olacak.\n\nГенерация фото пока недоступна. Скоро включим."
            )
        return

    add_message(user_id, "user", user_text)
    history = get_recent_messages(user_id)
    messages = [{"role": r, "content": c} for r, c in history]

    try:
        logger.info(f"🧠 Генерация ответа GPT для {user_id}...")
        reply = await asyncio.to_thread(gpt_service.generate_reply, persona, messages)
        logger.info(f"✅ GPT ответ получен для {user_id}: {reply[:50]}...")
    except Exception as e:
        logger.error(f"❌ Ошибка GPT для {user_id}: {e}", exc_info=True)
        reply = (
            "Şu anda yanıt üretirken bir sorun oldu, birazdan tekrar dene.\n\n"
            "Сейчас возникла ошибка при генерации ответа, попробуй чуть позже."
        )

    add_message(user_id, "assistant", reply)
    await message.answer(reply)
    logger.info(f"✅ Ответ отправлен пользователю {user_id}")


async def main() -> None:
    # Ensure console can handle non-ASCII without crashing on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
    except Exception:
        pass
    
    logger.info("🗄️ Инициализация базы данных...")
    try:
        init_db()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}", exc_info=True)
        raise
    
    # Get bot info and show startup message
    try:
        logger.info("🔍 Получение информации о боте...")
        bot_info = await bot.get_me()
        logger.info("=" * 70)
        logger.info("✅ HayalKiz Bot успешно запущен / Uspeshno zapushchen")
        logger.info(f"   Bot: @{bot_info.username}")
        logger.info(f"   Bot ID: {bot_info.id}")
        logger.info(f"   WebApp URL: {settings.webapp_url}")
        logger.info("=" * 70)
        logger.info("📖 Использование / Ispolzovanie:")
        logger.info("   1. Откройте бота в Telegram / Otkroyte bota v Telegram")
        logger.info("   2. Отправьте /start / Otpravte /start")
        logger.info("   3. Нажмите кнопку Mini App / Nazhmite knopku Mini App")
        logger.info("   4. Выберите девушку и общайтесь / Vyberite devushku i obshchaytes'")
        logger.info("=" * 70)
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА при запуске бота: {e}", exc_info=True)
        logger.error("   Проверьте TELEGRAM_BOT_TOKEN в файле keys.env")
        raise
    
    try:
        logger.info("🚀 Запуск polling...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка во время polling: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
