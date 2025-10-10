# 🎯 ИСПРАВЛЕНИЕ: Runway API - Правильный формат ratio

## ❌ Проблема

**Ошибка:**
```
"Model variant gen4-turbo is not available"
```

**Затем:**
```
`ratio` must be one of: 1280:720, 720:1280, 1104:832, 832:1104, 960:960, 1584:672
```

---

## ✅ Решение

### Главная проблема: Неправильный формат `ratio`

**Было (НЕПРАВИЛЬНО):**
```python
"ratio": "9:16"  # Aspect ratio - НЕ РАБОТАЕТ!
```

**Стало (ПРАВИЛЬНО):**
```python
"ratio": "720:1280"  # Точный размер в пикселях - РАБОТАЕТ!
```

### Допустимые значения `ratio`:

| Значение | Описание |
|----------|----------|
| `1280:720` | Горизонтальный HD (16:9) |
| **`720:1280`** | **Вертикальный HD (9:16)** ← используем для селфи |
| `1104:832` | Альтернативный горизонтальный |
| `832:1104` | Альтернативный вертикальный |
| `960:960` | Квадратный |
| `1584:672` | Широкоформатный |

---

## 🔧 Что исправлено

### 1. `services_runway.py`

**Было:**
```python
payload = {
    "promptText": prompt,
    "model": model,
    "duration": duration,
    "ratio": "9:16" if "720x1280" in size else "16:9",  # НЕПРАВИЛЬНО!
    "watermark": False,
    "seed": None  # Также проблема - null не поддерживается
}
```

**Стало:**
```python
# Определяем правильный формат ratio
if "720x1280" in size or "720:1280" in size:
    ratio = "720:1280"  # Vertical HD
elif "1280x720" in size or "1280:720" in size:
    ratio = "1280:720"  # Horizontal HD
else:
    ratio = "720:1280"  # Default to vertical

# Runway image_to_video API ТРЕБУЕТ изображение
if not image_bytes and not image_url:
    logger.error("❌ Runway image_to_video API requires an image!")
    return None

# Prepare image
if image_bytes:
    compressed_image = compress_image_for_api(image_bytes, max_size_kb=800)
    b64_image = base64.b64encode(compressed_image).decode("utf-8")
    prompt_image = f"data:image/jpeg;base64,{b64_image}"
elif image_url:
    prompt_image = image_url

# Build complete payload
payload = {
    "model": model,                # ОБЯЗАТЕЛЬНО
    "promptImage": prompt_image,   # ОБЯЗАТЕЛЬНО
    "promptText": prompt,          # Опционально, но рекомендуется
    "duration": duration,          # Опционально (default: 5)
    "ratio": ratio                 # ОБЯЗАТЕЛЬНО, точный формат пикселей!
}
```

---

## ✅ Результаты тестов

Все тесты прошли успешно:

```
📊 SUMMARY
Test 1: ratio='720:1280'                 ✅ РАБОТАЕТ
Test 2: duration=10                      ✅ РАБОТАЕТ
Test 3: ratio='1280:720'                 ✅ РАБОТАЕТ
Test 4: Minimal                          ✅ РАБОТАЕТ
Test 5: With seed                        ✅ РАБОТАЕТ
Test 6: With watermark                   ✅ РАБОТАЕТ

✅ Найден рабочий формат!
```

**Примеры успешных запросов:**
- ✅ Task ID: `d8b03508-a8a3-4590-ae09-788f16c4c6a3`
- ✅ Task ID: `781d2c73-76c4-4970-8dfb-d14e2cdfc78d`
- ✅ Task ID: `6c873017-ec73-449c-83a0-7a21724f2580`

---

## 📋 Обязательные параметры Runway API

### Для `/v1/image_to_video`:

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `model` | string | ✅ Да | `gen4_turbo` или другие |
| `promptImage` | string | ✅ Да | Base64 или URL изображения |
| `ratio` | string | ✅ Да | Точный размер (например, `720:1280`) |
| `promptText` | string | ⚠️ Рекомендуется | Описание желаемого видео |
| `duration` | number | ❌ Нет | По умолчанию: 5 (допустимы: 5, 10) |
| `seed` | number | ❌ Нет | Для воспроизводимости (не `null`!) |
| `watermark` | boolean | ❌ Нет | Добавлять ли водяной знак |

---

## 🚀 Как запустить

### 1. Убедитесь что API ключ настроен:

```bash
# В файле back/keys.env
RUNWAY_API_KEY=ваш_ключ_здесь
```

### 2. Перезапустите бота:

```bash
cd back
python start.py
```

### 3. Попробуйте создать видео:

1. Отправьте "Селфи" в бота
2. Дождитесь генерации селфи
3. Нажмите "🎬 Видео"
4. Выберите "Из последнего селфи"

---

## 📊 Ожидаемые логи

**Успешная генерация:**

```
🎬 Starting Runway Gen-4 Turbo video generation...
   Model: gen4_turbo, Size: 720x1280, Duration: 5s
   Original prompt length: 856 chars
   Image input: from bytes (245.3KB, image-to-video mode)
[Runway] Request payload: {"model":"gen4_turbo","promptImage":"<base64_data>","promptText":"...","duration":5,"ratio":"720:1280"}
[Runway] Response keys: ['id']
[Runway] Got task ID: d8b03508-a8a3-4590-ae09-788f16c4c6a3, starting polling...
[Runway] Poll 1/120: status=processing
[Runway] Poll 5/120: status=succeeded
✅ Video downloaded: 4567823 bytes
✅ Видео сгенерировано: 4567823 байт
```

**В Telegram:**
```
🎬 Генерирую видео... (5 секунд, может занять 1-2 минуты)
⏳ Видео обрабатывается... (осталось ~90 сек)
⏳ Почти готово... (осталось ~30 сек)
Вот моё видео! 🎥💕
[видео файл]
```

---

## 🎯 Ключевые выводы

1. ✅ **Ratio формат**: Используйте точные размеры в пикселях (`720:1280`), НЕ aspect ratio (`9:16`)
2. ✅ **Image обязателен**: `/v1/image_to_video` всегда требует изображение
3. ✅ **Модель работает**: `gen4_turbo` полностью функциональна
4. ✅ **Все параметры**: `model`, `promptImage`, `ratio` - обязательны
5. ✅ **Duration**: Поддерживаются значения 5 и 10 секунд

---

## 🧪 Дополнительное тестирование

### Запустить полный тест:

```bash
cd back
python test_runway_final.py
```

Это проверит все комбинации параметров и покажет что работает.

---

## 🎉 Всё готово!

Проблема полностью решена. API работает отлично. Можно запускать бота и генерировать видео! 🚀✨

**Версия**: 3.0.3  
**Статус**: ✅ Полностью рабочий  
**Дата**: 2025-10-10

