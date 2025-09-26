

import asyncio
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

settings = get_settings()

bot = Bot(token=settings.telegram_bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

gpt_service = GPTService()
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
    text = (
        "Merhaba! Benimle hayalindeki kızı seç ve sohbet etmeye başla.\n"
        "Tüm mesajlar önce Türkçe, sonra aynı mesajda Rusça kopyalanır.\n\n"
        "Привет! Выбери девушку из каталога и начни общение.\n"
        "Все сообщения сначала на турецком, затем дублируются на русском."
    )
    
    # Try WebApp keyboard first, fallback to inline keyboard
    try:
        await message.answer(text, reply_markup=webapp_keyboard())
    except Exception:
        # If WebApp fails, use inline keyboard
        await message.answer(
            text + "\n\nMini App недоступен, выберите девушку ниже:",
            reply_markup=persona_selection_keyboard()
        )


@dp.callback_query(lambda c: c.data.startswith("select_persona:"))
async def on_persona_selection(callback_query):
    """Handle persona selection from inline keyboard"""
    persona_code = callback_query.data.split(":")[1]
    persona = get_persona(persona_code)
    
    if persona:
        db_set_persona(str(callback_query.from_user.id), persona.code)
        await callback_query.message.edit_text(
            f"Seçildi: {persona.name_tr} — {persona.tagline_tr}.\n"
            "Sohbete başlayabiliriz! 'selfie' istersen söyle.\n\n"
            f"Выбрана: {persona.name_ru} — {persona.tagline_ru}.\n"
            "Можем начинать! Если хочешь 'селфи' — скажи."
        )
    else:
        await callback_query.answer("Geçersiz seçim / Неверный выбор")


@dp.message(F.web_app_data)
async def on_webapp_data(message: Message):
    try:
        data = message.web_app_data.data
        import json
        payload = json.loads(data)
        code = str(payload.get("persona", "")).lower()
        persona = get_persona(code)
        if not persona:
            await message.answer(
                "Seçim anlaşılamadı. Lütfen tekrar deneyin.\n\nВыбор не распознан. Попробуйте ещё раз."
            )
            return
        db_set_persona(str(message.from_user.id), persona.code)
        await message.answer(
            (
                f"Seçildi: {persona.name_tr} — {persona.tagline_tr}.\n"
                "Sohbete başlayabiliriz! 'selfie' istersen söyle.\n\n"
                f"Выбрана: {persona.name_ru} — {persona.tagline_ru}.\n"
                "Можем начинать! Если хочешь 'селфи' — скажи."
            ),
            reply_markup=webapp_keyboard(),
        )
    except Exception:
        await message.answer(
            "Bir hata oluştu, tekrar dener misin?\n\nПроизошла ошибка, попробуйте ещё раз."
        )


@dp.message()
async def on_message(message: Message):
    user_id = str(message.from_user.id)
    code = db_get_persona(user_id)
    if not code:
        await message.answer(
            "Önce bir kız seç.\n\nСначала выбери девушку.",
            reply_markup=persona_selection_keyboard(),
        )
        return
    persona = get_persona(code)
    assert persona is not None

    user_text = message.text or ""

    if any(k in user_text.lower() for k in ["selfie", "селфи", "foto", "фото"]):
        prompt = (
            f"{persona.name_tr} stilinde, {persona.tagline_tr} havasında bir selfie."
            " Doğal ışık, portre."
        )
        data_uri = await flux_service.generate_photo_data_uri(prompt)
        if data_uri:
            await message.answer(
                "İşte istediğin selfie!\n\nВот запрошенное селфи!"
            )
            await message.answer_photo(photo=data_uri)
        else:
            await message.answer(
                "Şu anda foto üretimi hazır değil. Yakında aktif olacak.\n\nГенерация фото пока недоступна. Скоро включим."
            )
        return

    add_message(user_id, "user", user_text)
    history = get_recent_messages(user_id)
    messages = [{"role": r, "content": c} for r, c in history]

    try:
        reply = await asyncio.to_thread(gpt_service.generate_reply, persona, messages)
    except Exception as e:
        print(f"GPT reply error for user {user_id}: {e}")
        reply = (
            "Şu anda yanıt üretirken bir sorun oldu, birazdan tekrar dene.\n\n"
            "Сейчас возникла ошибка при генерации ответа, попробуй чуть позже."
        )

    add_message(user_id, "assistant", reply)
    await message.answer(reply)


async def main() -> None:
    # Ensure console can handle non-ASCII without crashing on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="ignore")
    except Exception:
        pass
    init_db()
    
    # Get bot info and show startup message
    try:
        bot_info = await bot.get_me()
        print("=" * 60)
        print("HayalKiz Bot basariyla baslatildi / Uspeshno zapushchen")
        print(f"Bot: @{bot_info.username}")
        print(f"Bot ID: {bot_info.id}")
        print(f"WebApp URL: {settings.webapp_url}")
        print("=" * 60)
        print("Kullanim / Ispolzovanie:")
        print("1. Telegram'da botu acin / Otkroyte bota v Telegram")
        print("2. /start komutunu gonderin / Otpravte /start")
        print("3. Mini Uygulama butonuna tiklayin / Nazhmite knopku Mini App")
        print("4. Bir kiz secin ve sohbet baslatin / Vyberite devushku i obshchaytes'")
        print("=" * 60)
        print("Durdurmak icin Ctrl+C / Dlya ostanovki nazhmite Ctrl+C")
        print("=" * 60)
    except Exception as e:
        print(f"Bot baslatma hatasi / Oshibka zapuska bota: {e}")
        return
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
