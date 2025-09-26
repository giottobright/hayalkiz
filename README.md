# HayalKız — Telegram Bot + Mini App (RU+TR)

Русский | Türkçe

## Описание / Açıklama
- RU: Телеграм-бот с мини-приложением (WebApp) для выбора AI-девушки и общения. Ответы генерируются на турецком языке и дублируются на русском. Фото «селфи» генерируются через flux-kontext-pro (заглушка/адаптер в проекте).
- TR: Bir Telegram botu ve Mini Uygulama (WebApp). Kullanıcı bir AI-kız seçer ve sohbet eder. Tüm yanıtlar Türkçe üretilir ve Rusça kopyalanır. "Selfie" fotoğrafları flux-kontext-pro ile üretilir (proje içinde adaptör/stub).

## Стек / Yığın
- Backend: Python, aiogram 3, FastAPI, OpenAI (GPT-4o mini)
- Frontend: React (Vite) WebApp, Telegram WebApp Button
- DB: SQLite

## Установка / Kurulum
1. Python 3.10+
2. `pip install -r requirements.txt`
3. Скопируйте `.env.example` в `.env` и заполните ключи.
4. Перейдите в `webapp/` и установите зависимости: `npm i`.

## Запуск / Çalıştırma
- Backend (бот + API): `python -m app.main`
- Frontend (webapp dev): `cd webapp && npm run dev`

## Переменные окружения / Ortam Değişkenleri
См. файл `.env.example`.

## Структура / Yapı
- `app/` — код бота и API
- `webapp/` — Vite React мини-приложение
- `data/` — SQLite и статические файлы

## Лицензия / Lisans
MIT
