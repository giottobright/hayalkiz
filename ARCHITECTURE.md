# 🏗️ Архитектура HayalKiz Bot v2.0

## 📊 Общая схема

```
┌─────────────────────────────────────────────────────────────┐
│                    TELEGRAM USER                             │
│                         👤                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  TELEGRAM BOT API                            │
│                    (aiogram 3.x)                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     main.py                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Handlers:                                           │   │
│  │  • /start → language_selection                       │   │
│  │  • on_language_selection → set language              │   │
│  │  • on_persona_selection → set persona                │   │
│  │  • on_message → chat / selfie                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────┬──────────────┬──────────────┬────────────────┬────────┘
      │              │              │                │
      ▼              ▼              ▼                ▼
┌─────────┐    ┌──────────┐   ┌──────────┐    ┌──────────┐
│   DB    │    │   GPT    │   │  FLUX    │    │ PERSONAS │
│ (db.py) │    │(services │   │(services │    │(personas │
│         │    │_gpt.py)  │   │_flux.py) │    │   .py)   │
└─────────┘    └──────────┘   └──────────┘    └──────────┘
     │              │               │
     ▼              ▼               ▼
┌─────────┐    ┌──────────┐   ┌──────────┐
│ SQLite  │    │ OpenAI   │   │   BFL    │
│  (app   │    │   API    │   │ Flux API │
│  .db)   │    │          │   │          │
└─────────┘    └──────────┘   └──────────┘
```

## 🔄 Поток данных

### 1️⃣ Первый запуск (новый пользователь)

```
User: /start
   │
   ▼
┌──────────────────────────────────────┐
│ main.py: cmd_start()                 │
│ • Проверяет существование языка      │
│ • Язык НЕ найден                     │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ Отправка language_selection_keyboard │
│ [🇹🇷 Türkçe] [🇷🇺 Русский]          │
└───────────┬──────────────────────────┘
            │
User: нажимает 🇷🇺 Русский
            │
            ▼
┌──────────────────────────────────────┐
│ main.py: on_language_selection()     │
│ • db.set_language(user_id, "ru")     │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ Отправка webapp_keyboard(lang="ru")  │
│ [Мини-приложение]                    │
└───────────┬──────────────────────────┘
            │
User: выбирает персону "Элиф"
            │
            ▼
┌──────────────────────────────────────┐
│ main.py: on_webapp_data()            │
│ • db.set_persona(user_id, "elif")    │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ Отправка chat_keyboard(lang="ru")    │
│ [📸 Покажи селфи]                    │
│ [👥 Сменить девушку]                 │
└──────────────────────────────────────┘
```

### 2️⃣ Генерация селфи

```
User: нажимает [📸 Покажи селфи]
   │
   ▼
┌──────────────────────────────────────┐
│ main.py: on_message()                │
│ • Определяет: это запрос селфи       │
│ • user_lang = db.get_language()      │
│ • persona = db.get_persona()         │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ main.py: generate_selfie()           │
│ • Формирует промпт для Flux          │
│ • "A beautiful selfie photo of..."   │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ services_flux.py:                    │
│   generate_photo_data_uri()          │
│ • POST запрос к BFL API              │
│ • Polling статуса                    │
│ • Скачивание изображения             │
│ • Конвертация в data URI             │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ Telegram: message.answer_photo()     │
│ Отправка фото пользователю           │
└──────────────────────────────────────┘
```

### 3️⃣ Обычное сообщение

```
User: "Привет! Как дела?"
   │
   ▼
┌──────────────────────────────────────┐
│ main.py: on_message()                │
│ • user_lang = db.get_language()      │
│ • persona = db.get_persona()         │
│ • db.add_message(user, text)         │
│ • history = db.get_recent_messages() │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ services_gpt.py:                     │
│   generate_reply(persona, messages,  │
│                  user_lang="ru")     │
│ • Формирует system prompt (RU)       │
│ • Вызов OpenAI API                   │
└───────────┬──────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ main.py:                             │
│ • db.add_message(assistant, reply)   │
│ • message.answer(reply)              │
└──────────────────────────────────────┘
```

## 🗄️ Структура базы данных

```sql
-- Таблица user_state
CREATE TABLE user_state (
    user_id TEXT PRIMARY KEY,
    persona TEXT,              -- Код персоны (elif, zeynep, ...)
    language TEXT DEFAULT 'tr', -- NEW! Язык (tr/ru)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица messages
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    role TEXT,                 -- 'user' или 'assistant'
    content TEXT,              -- Текст сообщения
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧩 Компоненты системы

### 1. Обработчики (main.py)

```python
# Команды
@dp.message(CommandStart())
async def cmd_start(message: Message)
    # Запуск бота, выбор языка

# Callback queries
@dp.callback_query(lambda c: c.data.startswith("lang:"))
async def on_language_selection(callback_query)
    # Сохранение выбранного языка

@dp.callback_query(lambda c: c.data.startswith("select_persona:"))
async def on_persona_selection(callback_query)
    # Сохранение выбранной персоны

# WebApp данные
@dp.message(F.web_app_data)
async def on_webapp_data(message: Message)
    # Получение персоны из Mini App

# Текстовые сообщения
@dp.message()
async def on_message(message: Message)
    # Обработка обычных сообщений и запросов селфи
```

### 2. Клавиатуры

```python
# Выбор языка
def language_selection_keyboard() -> InlineKeyboardMarkup
    # [🇹🇷 Türkçe] [🇷🇺 Русский]

# Mini App
def webapp_keyboard(user_lang: str) -> ReplyKeyboardMarkup
    # [Mini Uygulama / Мини-приложение]

# Чат с кнопками
def chat_keyboard(user_lang: str) -> ReplyKeyboardMarkup
    # [📸 Селфи] [👥 Смена]

# Fallback выбор персоны
def persona_selection_keyboard() -> InlineKeyboardMarkup
    # [Элиф] [Зейнеп] [Мелис] ...
```

### 3. Сервисы

```python
# GPT сервис (services_gpt.py)
class GPTService:
    def generate_reply(persona, messages, user_lang):
        # Генерация ответа на выбранном языке
        # • Формирование system prompt
        # • Вызов OpenAI API
        # • Возврат текста

# Flux сервис (services_flux.py)
class FluxService:
    async def generate_photo_data_uri(prompt):
        # Генерация изображения
        # • POST к BFL API
        # • Polling результата
        # • Конвертация в base64
        # • Возврат data URI
```

### 4. База данных (db.py)

```python
# Персоны
def set_persona(user_id: str, persona: str)
def get_persona(user_id: str) -> str | None

# Языки (NEW!)
def set_language(user_id: str, language: str)
def get_language(user_id: str) -> str

# Сообщения
def add_message(user_id: str, role: str, content: str)
def get_recent_messages(user_id: str, limit=12) -> List[Tuple[str, str]]
```

## 🔐 Безопасность и валидация

### Входные данные

```python
# Язык
if lang in ["tr", "ru"]:  # Только разрешенные языки
    db_set_language(user_id, lang)

# Персона
persona = get_persona(code)
if persona:  # Проверка существования
    db_set_persona(user_id, persona.code)

# API ключи
settings = get_settings()  # Валидация при загрузке
if not settings.telegram_bot_token:
    raise ValueError("Required")
```

### API взаимодействие

```python
# Timeout для всех запросов
timeout = aiohttp.ClientTimeout(total=120)

# Обработка ошибок
try:
    result = await api_call()
except Exception as e:
    logger.error(f"Error: {e}")
    return fallback_response
```

## 📈 Производительность

### Оптимизации v2.0

1. **Меньше токенов**
   - Раньше: 2 языка = ~200 токенов
   - Теперь: 1 язык = ~100 токенов
   - Экономия: ~50%

2. **Быстрее ответы**
   - Меньше токенов → быстрее генерация
   - Улучшение: ~25%

3. **Кэширование**
   - Персоны загружаются один раз
   - Settings загружаются один раз

### Узкие места

1. **Flux API** - генерация 10-30 сек
   - Решение: показываем индикатор прогресса

2. **SQLite** - при большой нагрузке
   - Решение: миграция на PostgreSQL для продакшена

3. **OpenAI API** - зависит от нагрузки
   - Решение: retry логика, fallback сообщения

## 🔄 Жизненный цикл запроса

```
┌─────────────────┐
│ User: /start    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check language  │◄─── DB: get_language()
└────────┬────────┘
         │
    ┌────┴────┐
    │ Found?  │
    └────┬────┘
         │
    ┌────┴────────────────┐
    │ NO          YES     │
    ▼             ▼       │
┌────────┐   ┌─────────┐ │
│Language│   │ Welcome │ │
│Select  │   │ back    │ │
└───┬────┘   └─────────┘ │
    │                    │
    ▼                    │
┌────────────┐           │
│Select      │◄──────────┘
│Persona     │
└─────┬──────┘
      │
      ▼
┌─────────────┐
│ Chat mode   │
│ [Buttons]   │
└─────────────┘
```

## 🧪 Тестирование

### Unit тесты (можно добавить)

```python
# test_db.py
def test_set_get_language():
    set_language("123", "ru")
    assert get_language("123") == "ru"

# test_gpt.py
def test_generate_reply_russian():
    reply = gpt.generate_reply(persona, [], "ru")
    assert is_russian(reply)

# test_flux.py
async def test_generate_photo():
    photo = await flux.generate_photo("test")
    assert photo is not None
```

### Integration тесты

```bash
# Тест полного флоу
1. /start
2. Выбор языка
3. Выбор персоны
4. Отправка сообщения
5. Генерация селфи
```

## 📦 Зависимости

```
aiogram==3.x        # Telegram Bot framework
openai              # OpenAI API client
aiohttp             # Async HTTP client
pydantic            # Settings validation
python-dotenv       # .env файлы
```

## 🚀 Deployment

### Development
```bash
python -m app.main
```

### Production (Docker)
```dockerfile
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "app.main"]
```

---

**Версия архитектуры**: 2.0  
**Последнее обновление**: 30.09.2025
