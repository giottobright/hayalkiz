# 🎬 Логика генерации видео - Подробное описание

## 📋 Обзор

В боте реализованы **2 варианта** генерации видео:

1. **🎯 Из существующего селфи** - использует уже созданное селфи
2. **🆕 Новое видео с нуля** - создаёт селфи + видео

---

## 🎯 ВАРИАНТ 1: Генерация видео из существующего селфи

### 📍 Точка входа
**Пользователь:** Нажимает "🎬 Видео" → "Из последнего селфи"

### 🔄 Пошаговая логика

#### **Шаг 1: Проверка данных**
```python
# Функция: generate_video_from_selfie()
# Файл: back/app/main.py, строки 640-720

1. Проверка инициализации RunwayService
2. Получение последнего селфи из БД:
   - selfie_prompt = get_last_selfie_prompt(user_id)
   - selfie_bytes = get_last_selfie_data(user_id)
3. Проверка что данные существуют
```

#### **Шаг 2: Генерация видео-промпта**
```python
# Функция: gpt_service.build_video_prompt()
# Файл: back/app/services_gpt.py, строки 180-250

ВХОДНЫЕ ДАННЫЕ:
- persona: объект персонажа (имя, характер)
- photo_prompt: промпт оригинального селфи
- user_lang: язык пользователя (ru/tr)

ПРОЦЕСС:
1. Случайно добавляется "соблазнительность" (50% шанс)
2. GPT анализирует photo_prompt и извлекает:
   - Девушку (внешность, характер)
   - Активность (что она делает)
   - Локацию (где происходит)
   - Одежду и настроение
3. GPT создаёт новый промпт для видео по правилам Sora 2

СИСТЕМНЫЙ ПРОМПТ GPT:
"""
You are a video prompt expert for Runway Gen-4 Turbo.
Create a 4-second vertical video (720x1280) prompt.

REQUIREMENTS:
1. Extract girl, activity, location, outfit, mood from photo prompt
2. Add 50% chance of seductive/flirty elements
3. Keep girl's identity and character
4. ONE clear movement over 4 seconds
5. Cinematic quality with technical details
6. 4-6 sentences total, under 1000 characters

STRUCTURE:
- Style & Scene (2-3 sentences)
- Cinematography & Actions (2-3 sentences)
- Background Sound: ambient only
"""

ПРИМЕР РЕЗУЛЬТАТА:
"Style & Format: Create a vibrant 4-second vertical video showcasing Eylül, 
an energetic Turkish influencer, in an art-filled gallery setting. 
The scene should emphasize her playful spirit and inviting confidence.

Scene Description: Eylül stands gracefully in the modern gallery, 
her blond hair catching the warm gallery lighting as she slowly turns 
to face the camera with a captivating smile. She wears a stylish 
contemporary outfit that complements the artistic environment.

Cinematography: Use a 35mm lens with shallow depth of field (f/1.8), 
slow push-in movement, and golden hour lighting streaming through 
large gallery windows. The camera should capture her natural elegance 
with smooth, cinematic motion.

Background Sound: Ambient gallery atmosphere with soft footsteps 
and distant conversations."
```

#### **Шаг 3: Генерация видео через Runway API**
```python
# Функция: runway_service.generate_video()
# Файл: back/app/services_runway.py, строки 95-200

ВХОДНЫЕ ДАННЫЕ:
- prompt: видео-промпт от GPT
- image_bytes: байты селфи из БД
- duration: 4 секунды
- size: "720x1280"
- model: "gen4_turbo"

ПРОЦЕСС:
1. Сжатие изображения (до 800KB) для избежания ошибки 413
2. Конвертация в base64
3. Построение payload:
   {
     "model": "gen4_turbo",
     "promptImage": "data:image/jpeg;base64,{b64_image}",
     "promptText": video_prompt,
     "duration": 4,
     "ratio": "720:1280"  # КРИТИЧНО: точные пиксели!
   }
4. POST запрос к https://api.dev.runwayml.com/v1/image_to_video
5. Получение task_id
6. Polling статуса каждые 5 секунд (до 120 попыток)
7. Скачивание готового видео

ПРИМЕР ЛОГОВ:
[Runway] Request payload: {"model":"gen4_turbo","promptImage":"<base64_data>","promptText":"...","duration":4,"ratio":"720:1280"}
[Runway] Response keys: ['id']
[Runway] Got task ID: d8b03508-a8a3-4590-ae09-788f16c4c6a3
[Runway] Poll 1/120: status=processing, progress=15%
[Runway] Poll 3/120: status=processing, progress=45%
[Runway] Poll 5/120: status=succeeded, progress=100%
✅ Video downloaded: 4567823 bytes
```

#### **Шаг 4: Сохранение и отправка**
```python
1. Сохранение видео в БД:
   save_generated_content(user_id, "video", video_prompt, video_bytes)
2. Отправка видео пользователю
3. Удаление статусного сообщения
```

### ⏱️ Время выполнения: ~1-2 минуты

---

## 🆕 ВАРИАНТ 2: Новое видео с нуля

### 📍 Точка входа
**Пользователь:** Нажимает "🎬 Видео" → "Новое видео"

### 🔄 Пошаговая логика

#### **Шаг 1: Генерация селфи-промпта**
```python
# Функция: generate_new_video()
# Файл: back/app/main.py, строки 750-900

1. Получение персонажа: persona = get_persona(user_id)
2. Генерация селфи-промпта через GPT:
   selfie_prompt = await asyncio.to_thread(
       gpt_service.generate_selfie_prompt,
       persona=persona,
       user_lang=user_lang
   )
```

#### **Шаг 2: Генерация селфи**
```python
# Функция: gemini_service.generate_image()
# Файл: back/app/services_gemini.py

1. Отправка selfie_prompt в Gemini Image API
2. Получение изображения в base64
3. Конвертация в bytes
4. Сохранение в БД: save_generated_content(user_id, "selfie", selfie_prompt, selfie_bytes)
```

#### **Шаг 3: Генерация видео-промпта**
```python
# Аналогично Варианту 1, Шаг 2
# Используется тот же build_video_prompt()
```

#### **Шаг 4: Генерация видео**
```python
# Аналогично Варианту 1, Шаг 3
# Используется тот же runway_service.generate_video()
```

#### **Шаг 5: Сохранение и отправка**
```python
1. Сохранение селфи в БД
2. Сохранение видео в БД
3. Отправка видео пользователю
```

### ⏱️ Время выполнения: ~2-3 минуты

---

## 🧠 Детали GPT промптинга (ОБНОВЛЕНО v3.1.0)

### 🎨 Система выбора стиля и действий

Новая система генерирует **уникальные, креативные, Instagram-worthy** видео!

#### **5 стилей видео:**
```python
video_styles = [
    "flirty_seductive",   # 20% - Соблазнительное
    "playful_fun",        # 20% - Игривое
    "elegant_beauty",     # 20% - Элегантное
    "energetic_dynamic",  # 20% - Энергичное
    "mysterious_alluring" # 20% - Загадочное
]
chosen_style = random.choice(video_styles)
```

#### **25 уникальных действий** (5 на каждый стиль):

**Flirty Seductive:**
- Медленно поворачивается с подмигиванием, кусает губу
- Приближается к камере с приглашающей улыбкой
- Идёт с уверенной походкой, бросает взгляд через плечо
- Поправляет одежду, показывая немного кожи
- Посылает воздушный поцелуй, касается губ

**Playful Fun:**
- Смеётся и кружится с радостью
- Танцует игриво, делает твирл
- Прыгает от восторга, машет рукой
- Делает селфи, корчит рожицы
- Играет с аксессуарами, надувает жвачку

**Elegant Beauty:**
- Грациозно поправляет волосы
- Идёт с изысканной осанкой
- Садится элегантно, скрещивает ноги
- Смотрит задумчиво, потом на камеру
- Поправляет украшения изящно

**Energetic Dynamic:**
- Прыгает энергично в кадр
- Идёт быстро с жестами
- Делает танцевальное движение, замирает
- Резко поворачивается с улыбкой
- Делает смелый жест, силовая поза

**Mysterious Alluring:**
- Выходит из теней медленно
- Смотрит загадочно, потом на камеру
- Касается губ задумчиво
- Идёт гипнотически медленно
- Играет со светом и тенью

#### **7 движений камеры:**
```python
camera_movements = [
    "slow push-in with shallow depth of field",
    "gentle pan following her movement",
    "smooth dolly shot tracking her",
    "handheld cinematic micro-shake for intimacy",
    "slow zoom with rack focus",
    "orbit camera movement around her",
    "low angle hero shot emphasizing confidence"
]
```

#### **7 сетапов освещения:**
```python
lighting_setups = [
    "golden hour sunlight streaming through window",
    "soft neon glow creating vibrant atmosphere",
    "natural daylight with gentle fill",
    "dramatic side lighting with deep shadows",
    "soft diffused light, beauty lighting",
    "sunset magic hour, warm orange-pink glow",
    "urban night lights bokeh background"
]
```

### 📝 Системный промпт (обновлённый)

```python
system_prompt = """You are an EXPERT Instagram video creator for Runway Gen-4 Turbo.
Create CAPTIVATING, DYNAMIC 4-second vertical videos that stop the scroll.

CRITICAL SPECS:
- 4 seconds duration, 720x1280 vertical format
- Instagram-ready: visually stunning, trendy, shareable
- Girl MUST perform interesting action (not just standing/smiling)
- Cinematic quality with professional camera work

YOUR PROMPT MUST INCLUDE:
1. WHAT SHE DOES: Specific engaging action from start to finish
2. HOW SHE MOVES: Body language, gestures, facial expressions
3. CAMERA WORK: Dynamic movement, focal length, aperture
4. LIGHTING: Specific setup creating mood
5. VIBE: The feeling/energy of the video

STRUCTURE (stay under 1000 chars):
- Opening: What happens in first 2 seconds
- Action: Her specific movements and expressions
- Camera & Lighting: Technical details creating cinematic look
- Vibe: Overall mood and energy

Be SPECIFIC and VISUAL. Write ONLY the video prompt, nothing else."""
```

### 🎯 User промпт (обновлённый)

```python
user_prompt = f"""PHOTO CONTEXT:
{photo_prompt[:400]}

PERSONA:
{persona.name_tr} - {persona.tagline_tr}

VIDEO STYLE: {chosen_style.replace('_', ' ').title()}

CREATE A PROMPT FOR THIS ACTION:
{chosen_action}

CAMERA: {chosen_camera}
LIGHTING: {chosen_lighting}

Make it Instagram-worthy! Show her personality through movement and expression.
Keep under 950 characters for safety. Be specific about what she does each second.
Write cinematic prompt that brings this to life."""
```

### 📊 Разнообразие

**Всего уникальных комбинаций:** 5 × 5 × 7 × 7 = **1,225 вариантов!**

Плюс вариативность от GPT (temperature=0.95) = **Практически бесконечное разнообразие**

### 📊 Примеры промптов

#### **Входной селфи-промпт:**
```
"Ultra-photorealistic portrait of Eylül, a vibrant 24-year-old Turkish woman 
with naturally flowing blond hair framing her face, her rich brown eyes 
sparkling with enthusiasm as she stands in an art-filled gallery in Karaköy, 
exuding her energetic and creative personality. She wears a stylish 
contemporary outfit that complements the artistic environment."
```

#### **Выходной видео-промпт:**
```
"Style & Format: Create a vibrant 4-second vertical video showcasing Eylül, 
an energetic Turkish influencer, in an art-filled gallery setting. 
The scene should emphasize her playful spirit and inviting confidence.

Scene Description: Eylül stands gracefully in the modern gallery, 
her blond hair catching the warm gallery lighting as she slowly turns 
to face the camera with a captivating smile. She wears a stylish 
contemporary outfit that complements the artistic environment.

Cinematography: Use a 35mm lens with shallow depth of field (f/1.8), 
slow push-in movement, and golden hour lighting streaming through 
large gallery windows. The camera should capture her natural elegance 
with smooth, cinematic motion.

Background Sound: Ambient gallery atmosphere with soft footsteps 
and distant conversations."
```

---

## 🔧 Технические детали

### 🗄️ База данных

```sql
-- Таблица: generated_content
CREATE TABLE generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    content_type TEXT NOT NULL,  -- 'selfie' или 'video'
    prompt TEXT NOT NULL,
    file_data BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 🔑 API Ключи

```python
# back/app/config.py
class Settings:
    openai_api_key: str | None = None      # Для GPT промптов
    google_api_key: str | None = None      # Для Gemini селфи
    runway_api_key: str | None = None      # Для Runway видео
    telegram_token: str | None = None      # Для Telegram бота
```

### 📏 Ограничения

| Параметр | Ограничение | Причина |
|----------|-------------|---------|
| Промпт видео | ≤1000 символов | Runway API |
| Изображение | ≤800KB | Избежать 413 ошибки |
| Длительность | 4 секунды | Runway API |
| Размер видео | 720x1280 | Вертикальный формат |
| Polling | 120 попыток | 10 минут максимум |

---

## 🎯 Ключевые отличия вариантов

| Аспект | Из селфи | Новое видео |
|--------|----------|-------------|
| **Время** | 1-2 минуты | 2-3 минуты |
| **Селфи** | Использует существующее | Создаёт новое |
| **Промпт селфи** | Из БД | Генерирует GPT |
| **Промпт видео** | Анализирует селфи-промпт | Анализирует селфи-промпт |
| **Сохранение** | Только видео | Селфи + видео |
| **Стоимость** | Меньше (1 API call) | Больше (2 API calls) |

---

## 🚀 Поток данных

### Вариант 1 (Из селфи):
```
БД → selfie_prompt → GPT → video_prompt → Runway → video_bytes → Пользователь
```

### Вариант 2 (Новое видео):
```
GPT → selfie_prompt → Gemini → selfie_bytes → GPT → video_prompt → Runway → video_bytes → Пользователь
```

---

## 🎬 Результат

В обоих случаях пользователь получает:
- **4-секундное вертикальное видео** (720x1280)
- **Высокое качество** (Runway Gen-4 Turbo)
- **Синематографичность** (технические детали камеры)
- **Персонализация** (характер девушки)
- **Вариативность** (50% соблазнительности)

---

**Версия**: 3.0.3  
**Дата**: 2025-10-10  
**Статус**: ✅ Полностью рабочий
