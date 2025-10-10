# 🔧 Исправление: Промпт слишком длинный

## ❌ Проблема

**Ошибка:**
```
"Too big: expected string to have <=1000 characters"
```

**Причина:** Runway API имеет лимит **1000 символов** для промпта, а наши промпты от GPT получаются длиннее.

---

## ✅ Исправления

### 1. Автоматическое обрезание промпта

В `services_runway.py` добавлено:
```python
# Truncate prompt to 1000 characters (Runway API limit)
if len(prompt) > 1000:
    truncated_prompt = prompt[:997] + "..."
    logger.info(f"   ⚠️ Prompt truncated from {len(prompt)} to {len(truncated_prompt)} chars")
else:
    truncated_prompt = prompt
```

### 2. Оптимизация генерации промптов

В `services_gpt.py` изменено:
- **Было**: 8-12 предложений
- **Стало**: 4-6 предложений, под 1000 символов
- **Структура**: более компактная

---

## 🚀 Что делать СЕЙЧАС

### Перезапустите бота:

```bash
cd back
python start.py
```

### Попробуйте создать видео:

1. Создайте селфи
2. Нажмите "🎬 Видео"
3. Выберите "Из последнего селфи"

---

## 📊 Ожидаемые результаты

### В логах увидите:

**Если промпт длинный:**
```
Original prompt length: 1245 chars
⚠️ Prompt truncated from 1245 to 1000 chars
[Runway] Request payload: {...}
[Runway] Got task ID: xxx-yyy-zzz
```

**Если промпт короткий:**
```
Original prompt length: 856 chars
[Runway] Request payload: {...}
[Runway] Got task ID: xxx-yyy-zzz
```

### В Telegram:

**Успех:**
```
🎬 Генерирую видео... (4 секунды, может занять 1-2 минуты)
[debug info с обрезанным промптом]
Вот моё видео! 🎥💕
[видео файл]
```

---

## 🎯 Что изменилось

### Промпты стали короче:

**Было (пример):**
```
Style: Cinematic vertical video, natural golden hour lighting, iPhone quality.

In a modern Istanbul café by the window, Elif, a beautiful 24-year-old Turkish woman with soft chestnut hair, sits with a warm smile. Golden hour sunlight streams through floor-to-ceiling windows, casting soft shadows. She holds a poetry book, her hazel eyes reflecting the ambient light.

Cinematography: Medium close-up, 50mm, f/2.8, slow push-in from waist-up to shoulder shot, shallow depth of field creating bokeh background. Natural key light from left window, soft ambient café fill.

Actions: She looks up from the book towards camera, her smile deepening, makes gentle eye contact with a slight head tilt, then glances back at the book with a content expression.

Background Sound: Soft café ambience, light street traffic, pages rustling.
```
*(~1200+ символов)*

**Стало (пример):**
```
Cinematic vertical video of Elif, a beautiful Turkish woman with chestnut hair, sitting in a modern Istanbul café. Golden hour sunlight streams through windows, creating soft shadows. Medium close-up, 50mm, f/2.8, slow push-in. She looks up from her book, smiles at camera, makes gentle eye contact with a slight head tilt. Soft café ambience.
```
*(~400 символов)*

---

## ⚙️ Настройка

### Если хотите изменить лимит:

В `services_runway.py`:
```python
# Изменить лимит (по умолчанию 1000)
if len(prompt) > 1000:  # ← изменить на другое число
```

### Если хотите более короткие промпты:

В `services_gpt.py`:
```python
# Изменить лимит в инструкции GPT
"Keep it 4-6 sentences total, under 1000 characters"  # ← изменить на меньше
```

---

## 🎬 Результат

**Теперь промпты:**
- ✅ **Короче** - 4-6 предложений вместо 8-12
- ✅ **Под лимитом** - автоматическое обрезание до 1000 символов
- ✅ **Качественные** - сохраняют всю важную информацию
- ✅ **Работают** - проходят валидацию Runway API

---

## 🚀 Попробуйте сейчас!

```bash
cd back
python start.py
```

Затем в Telegram создайте видео - теперь должно работать! 🎥✨

---

**Версия**: 3.0.1  
**Исправление**: Лимит длины промпта  
**Статус**: ✅ Готово к тестированию

