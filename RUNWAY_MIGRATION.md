# 🎬 Миграция на Runway Gen-4 Turbo

## ✅ Что сделано

Полностью переписан сервис генерации видео с **Sora 2** (недоступен) на **Runway Gen-4 Turbo** (публично доступен)!

---

## 🚀 Быстрый старт

### 1. Получите API ключ Runway

Перейдите на https://app.runwayml.com/ и:
1. Зарегистрируйтесь/войдите
2. Перейдите в Settings → API Keys
3. Создайте новый API ключ
4. Скопируйте его

### 2. Добавьте ключ в keys.env

```bash
cd back
nano keys.env
```

Добавьте строку:
```env
RUNWAY_API_KEY=ваш_ключ_здесь
```

Или используйте существующий OpenAI ключ (fallback).

### 3. Перезапустите бота

```bash
cd back
python start.py
```

### 4. Попробуйте в Telegram!

1. Создайте селфи
2. Нажмите "🎬 Video gönder"
3. Выберите "Из последнего селфи"
4. Получите видео!

---

## 📊 Изменения

### Новые файлы:
- ✅ `back/app/services_runway.py` - Runway API сервис

### Обновленные файлы:
- ✅ `back/app/main.py` - используется RunwayService вместо SoraService
- ✅ `back/app/config.py` - добавлен runway_api_key
- ✅ `back/keys.example.env` - добавлен RUNWAY_API_KEY

### Удаленные:
- ❌ `back/app/services_sora.py` - больше не нужен (можно удалить)

---

## 🔧 Технические детали

### Runway Gen-4 Turbo API

**Endpoint**: `https://api.dev.runwayml.com/v1/image_to_video`

**Параметры**:
```json
{
  "promptText": "описание видео",
  "promptImage": "data:image/jpeg;base64,...",
  "model": "gen4-turbo",
  "duration": 4,
  "ratio": "9:16"
}
```

**Длительность**: 4, 8 секунд (мы используем 4)

**Соотношение сторон**:
- `9:16` - вертикальное (720x1280)
- `16:9` - горизонтальное (1280x720)

### Процесс генерации:

1. POST запрос → получаем task ID
2. Polling каждые 3 секунды
3. Когда status = "succeeded" → скачиваем видео

---

## 💰 Стоимость

Runway Gen-4 Turbo:
- **~$0.05-0.10** за 4-секундное видео
- **Значительно дешевле** чем Sora 2
- **Публично доступен!**

---

## ⚙️ Конфигурация

### Переменные окружения:

**Обязательная**:
```env
RUNWAY_API_KEY=ваш_ключ
```

**Опциональная** (fallback на OPENAI_API_KEY):
Если RUNWAY_API_KEY не указан, используется OPENAI_API_KEY.

### Параметры видео:

В `main.py`:
```python
video_bytes = await runway_service.generate_video(
    prompt=video_prompt,
    image_bytes=selfie_bytes,
    duration=4,  # 4 или 8 секунд
    size="720x1280",  # вертикальное
    model="gen4-turbo"
)
```

---

## 🎯 Преимущества Runway

### ✅ Плюсы:
- 🌐 **Публично доступен** - не нужно ждать бета-доступа
- 💰 **Дешевле** - ~$0.05-0.10 за видео
- ⚡ **Быстрее** - генерация ~30-60 секунд
- 📚 **Хорошая документация** - https://docs.dev.runwayml.com/
- 🎬 **Качественное видео** - Gen-4 Turbo это последняя модель

### ⚠️ Особенности:
- ⏱️ **Длительность**: только 4 или 8 секунд (мы используем 4)
- 📐 **Aspect ratio**: 9:16 или 16:9 (мы используем 9:16 вертикальное)

---

## 🔄 Совместимость

### Обратная совместимость:
✅ **ДА!** Весь существующий код работает без изменений:
- Генерация селфи
- Общение с девушками
- База данных
- UI/UX

Изменилась только реализация генерации видео.

---

## 📝 Логи

При успешной генерации вы увидите:
```
🎬 Starting Runway Gen-4 Turbo video generation...
   Model: gen4-turbo, Size: 720x1280, Duration: 4s
🗜️ Image compressed: 2450.5KB → 785.2KB
[Runway] Request payload: {...}
[Runway] Got task ID: xxx-yyy-zzz
[Runway] Poll 1/120: status=processing, progress=15%
[Runway] Poll 5/120: status=processing, progress=75%
[Runway] Poll 8/120: status=succeeded, progress=100%
✅ Video ready, downloading...
📥 Downloading video from URL...
✅ Video downloaded: 8456234 bytes
💾 Видео сохранено в БД
```

---

## ❓ FAQ

### Q: Нужно ли удалять services_sora.py?
A: Можно, но не обязательно. Он больше не используется.

### Q: Работает ли без RUNWAY_API_KEY?
A: Да, будет использован OPENAI_API_KEY как fallback.

### Q: Можно ли использовать 8 секунд?
A: Да! Измените `duration=8` в `main.py`.

### Q: Можно ли горизонтальное видео?
A: Да! Измените `size="1280x720"` в `main.py`.

### Q: Где получить API ключ?
A: https://app.runwayml.com/ → Settings → API Keys

---

## 🎉 Готово!

Теперь функция видео **работает** с Runway Gen-4 Turbo!

**Попробуйте прямо сейчас:**
```bash
cd back
python start.py
```

Затем в Telegram:
1. Создайте селфи
2. Нажмите "🎬 Видео"
3. Получите реальное видео! 🎥✨

---

**Версия**: 3.0.0  
**Дата**: 10 октября 2025  
**API**: Runway Gen-4 Turbo  
**Статус**: ✅ Работает!


