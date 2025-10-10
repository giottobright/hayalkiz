# 🚀 БЫСТРЫЙ СТАРТ: Runway Gen-4 Turbo

## ✅ Всё исправлено и готово!

Все проблемы решены. API Runway Gen-4 Turbo полностью настроен и протестирован.

---

## 📋 Что было исправлено

### 1. **Формат ratio**
   - ❌ Было: `"ratio": "9:16"` (aspect ratio - не работает)
   - ✅ Стало: `"ratio": "720:1280"` (точные пиксели - работает!)

### 2. **Обязательные поля**
   - ✅ `model`: `"gen4_turbo"`
   - ✅ `promptImage`: base64 изображение (обязательно!)
   - ✅ `ratio`: `"720:1280"` (обязательно!)

### 3. **Удалены проблемные поля**
   - ❌ Убрано: `"seed": null` (вызывало ошибку)

---

## 🚀 Запуск

### 1. Убедитесь что API ключ настроен

Откройте `back/keys.env` и проверьте:

```bash
RUNWAY_API_KEY=ваш_ключ_здесь
```

### 2. Запустите бота

```bash
cd back
python start.py
```

### 3. Проверьте логи при старте

Вы должны увидеть:

```
🔑 API Keys Status:
   ✅ OpenAI API key: found
   ✅ Google API key: found
   ✅ Telegram token: found
   ✅ Runway API key: found

🎬 Sora service initialized successfully
🤖 Gemini service initialized successfully
```

---

## 🎥 Как создать видео

### Вариант 1: Из существующего селфи

1. Отправьте боту: **"Селфи"** или нажмите кнопку **"📸 Селфи"**
2. Дождитесь генерации селфи
3. Нажмите кнопку **"🎬 Видео"**
4. Выберите **"Из последнего селфи"**
5. Ждите 1-2 минуты

### Вариант 2: Новое видео с нуля

1. Нажмите кнопку **"🎬 Видео"**
2. Выберите **"Новое видео"**
3. Ждите 2-3 минуты (генерация селфи + видео)

---

## 📊 Что вы увидите

### В логах (успешно):

```
🎬 Starting Runway Gen-4 Turbo video generation...
   Model: gen4_turbo, Size: 720x1280, Duration: 5s
   Original prompt length: 856 chars
   Image input: from bytes (245.3KB, image-to-video mode)
[Runway] Request payload: {"model":"gen4_turbo","promptImage":"<base64_data>","promptText":"...","duration":5,"ratio":"720:1280"}
[Runway] Response keys: ['id']
[Runway] Got task ID: d8b03508-a8a3-4590-ae09-788f16c4c6a3
[Runway] Poll 1/120: status=processing, progress=15%
[Runway] Poll 3/120: status=processing, progress=45%
[Runway] Poll 5/120: status=processing, progress=78%
[Runway] Poll 7/120: status=succeeded, progress=100%
✅ Video downloaded: 4567823 bytes
✅ Видео сгенерировано: 4567823 байт
```

### В Telegram (пользователь увидит):

```
🎬 Генерирую видео... (5 секунд, может занять 1-2 минуты)

⏳ Видео обрабатывается... (осталось ~90 сек)

⏳ Почти готово... (осталось ~30 сек)

Вот моё видео! 🎥💕
[видео файл отправлен]
```

---

## 🧪 Тестирование (опционально)

Если хотите убедиться что всё работает до запуска бота:

```bash
cd back
python test_runway_final.py
```

Вы увидите:
```
✅ Найден рабочий формат! Смотрите '✅ SUCCESS' выше.
Test 1: ratio='720:1280'                 ✅ РАБОТАЕТ
Test 2: duration=10                      ✅ РАБОТАЕТ
Test 3: ratio='1280:720'                 ✅ РАБОТАЕТ
Test 4: Minimal                          ✅ РАБОТАЕТ
Test 5: With seed                        ✅ РАБОТАЕТ
Test 6: With watermark                   ✅ РАБОТАЕТ
```

---

## ⚙️ Технические детали

### Параметры генерации:

- **Модель**: `gen4_turbo` (Runway Gen-4 Turbo)
- **Размер**: `720x1280` (вертикальное HD видео)
- **Длительность**: 5 секунд (по умолчанию)
- **Формат ratio**: `720:1280` (точные пиксели!)
- **Режим**: Image-to-video (всегда требует изображение)

### Поддерживаемые значения:

| Параметр | Допустимые значения |
|----------|---------------------|
| `duration` | 5, 10 секунд |
| `ratio` | `720:1280`, `1280:720`, `1104:832`, `832:1104`, `960:960`, `1584:672` |
| `model` | `gen4_turbo`, `gen4`, и другие |

---

## 🎯 Возможные проблемы

### 1. "Runway API key not found"

**Решение:**
```bash
# Добавьте в back/keys.env
RUNWAY_API_KEY=ваш_ключ
```

### 2. "Validation of body failed"

**Причина:** Старая версия кода.

**Решение:** Убедитесь что вы используете последнюю версию с правильным форматом `ratio: "720:1280"`.

### 3. "promptImage required"

**Причина:** API требует изображение (это image-to-video).

**Решение:** Это нормально - код автоматически передаёт изображение. Если видите эту ошибку, значит что-то не так с передачей `image_bytes`.

---

## 📚 Дополнительная информация

- **Полное описание исправлений**: см. `RUNWAY_FIX_RATIO.md`
- **История миграции**: см. `RUNWAY_MIGRATION.md`
- **Все тесты**: `back/test_runway_final.py`

---

## 🎉 Готово к запуску!

Всё настроено и протестировано. Просто запустите:

```bash
cd back
python start.py
```

И начинайте генерировать видео! 🚀✨

---

**Версия**: 3.0.3  
**Статус**: ✅ Полностью рабочий  
**Дата**: 2025-10-10  
**Модель**: Runway Gen-4 Turbo  
**API**: https://api.dev.runwayml.com/v1/image_to_video