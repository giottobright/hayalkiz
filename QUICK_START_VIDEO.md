# 🎬 Quick Start - Video Feature

## ✨ Что нового / What's New

Теперь пользователи могут получать **видео** от ИИ-девушек!  
Users can now get **videos** from AI girls!

## 🚀 Быстрый старт / Quick Start

### 1️⃣ Проверить API ключ / Check API Key

Убедитесь что в `back/keys.env` есть:
```env
OPENAI_API_KEY=sk-proj-...
```

⚠️ **Важно**: Ключ должен иметь доступ к Sora 2 API (beta)

### 2️⃣ Обновить базу данных / Update Database

База автоматически обновится при первом запуске.  
Будет создана новая таблица `generated_content`.

### 3️⃣ Запустить бота / Start Bot

```bash
cd back
python start.py
```

или / or:

```bash
docker-compose restart
```

### 4️⃣ Протестировать / Test

#### В Telegram:
1. Открыть бота
2. Выбрать девушку через Mini App
3. Нажать "🎬 Video gönder" / "🎬 Отправь видео"
4. Выбрать режим:
   - 📸➡️🎬 Из последнего селфи
   - ✨ Новое видео
5. Подождать ~1-2 минуты
6. Получить видео!

#### Автоматическое тестирование:
```bash
cd back
python test_video_feature.py
```

## 📋 Что было добавлено / What Was Added

### Новые файлы / New Files:
- `back/app/services_sora.py` - Sora 2 API service
- `back/test_video_feature.py` - Test script
- `VIDEO_FEATURE_GUIDE.md` - Technical guide
- `VIDEO_USER_GUIDE_RU_TR.md` - User guide
- `CHANGELOG_VIDEO_FEATURE.md` - Detailed changelog

### Обновленные файлы / Updated Files:
- `back/app/services_gpt.py` - Added `build_video_prompt()`
- `back/app/db.py` - Added `generated_content` table
- `back/app/main.py` - Added video generation endpoints

## ⚡ Основные возможности / Key Features

✅ **Два режима генерации:**
- Видео из селфи (30-60 сек)
- Новое видео с нуля (1-2 мин)

✅ **Характеристики видео:**
- 5 секунд, вертикальное HD (720x1280)
- Cinematic качество
- Естественные движения

✅ **Разнообразие контента:**
- 50% обычные видео
- 50% с легким флиртом и соблазнением

## 🔧 Настройки / Configuration

### Изменить длительность видео:

В `back/app/main.py` найти:
```python
video_bytes = await sora_service.generate_video(
    prompt=video_prompt,
    duration=5,  # ← Изменить на 4, 8 или 12
    ...
)
```

### Изменить вероятность эротического контента:

В `back/app/services_gpt.py` найти:
```python
is_seductive = random.random() < 0.5  # 50%

# Варианты:
# is_seductive = True  # всегда
# is_seductive = False  # никогда
# is_seductive = random.random() < 0.75  # 75%
```

### Изменить разрешение видео:

В `back/app/main.py` найти:
```python
size="720x1280",  # вертикальное HD
# Или:
# size="1280x720"  # горизонтальное HD
# size="1024x1792"  # вертикальное больше (sora-2-pro)
```

## 🐛 Troubleshooting

### ❌ Видео не генерируется

**Причины:**
1. API ключ не имеет доступа к Sora 2
2. Недостаточно кредитов OpenAI
3. Timeout (слишком долгая генерация)

**Решение:**
- Проверить логи: `tail -f back/logs/bot.log`
- Убедиться что `OPENAI_API_KEY` валиден
- Связаться с OpenAI support для доступа к Sora 2

### ❌ "Önce bir selfie oluştur"

**Причина:** Пользователь пытается создать видео из селфи, но не создал селфи.

**Решение:** Сначала создать селфи (📸 кнопка)

### ❌ Timeout during generation

**Причина:** Генерация видео занимает слишком много времени (>4 минуты)

**Решение:** 
- Попробовать еще раз
- Проверить интернет соединение
- Уменьшить `duration` до 4 секунд

## 📊 Мониторинг / Monitoring

### Логи:
```bash
# Смотреть логи в реальном времени
tail -f back/logs/bot.log | grep -E "🎬|Sora|video"

# Только ошибки
tail -f back/logs/bot.log | grep "❌"
```

### Важные логи:
```
🎬 Запрос видео от {user_id}
📸 Найден промпт последнего селфи
🧠 Генерация видео-промпта через GPT
✅ Видео-промпт создан
🎬 Генерация видео через Sora
[Sora] Request payload: {...}
[Sora] Poll 1/120: status=processing
[Sora] Poll 15/120: status=completed
✅ Видео сгенерировано: X байт
💾 Видео сохранено в БД
```

## 📈 Производительность / Performance

| Действие | Время | Стоимость (примерно) |
|----------|-------|----------------------|
| Видео из селфи | 30-60 сек | ~$0.50-1.00 |
| Новое видео | 60-120 сек | ~$1.00-2.00 |
| Хранение в БД | мгновенно | бесплатно |

## 💡 Советы / Tips

1. **Для быстрой генерации**: используйте "Видео из селфи"
2. **Для разнообразия**: используйте "Новое видео"
3. **Экономия места**: отключите сохранение файлов в БД (изменить `file_data=None`)
4. **Лучшее качество**: используйте `model="sora-2-pro"` (требует больше кредитов)

## 🔗 Документация / Documentation

- **Полное техническое руководство**: `VIDEO_FEATURE_GUIDE.md`
- **Руководство пользователя**: `VIDEO_USER_GUIDE_RU_TR.md`
- **Changelog**: `CHANGELOG_VIDEO_FEATURE.md`
- **Официальная документация Sora 2**: [OpenAI Cookbook](https://cookbook.openai.com/examples/sora/sora2_prompting_guide)

## ❓ FAQ

**Q: Сколько стоит генерация видео?**  
A: Примерно $0.50-2.00 за видео (зависит от длительности и модели)

**Q: Можно ли генерировать горизонтальные видео?**  
A: Да, измените `size="1280x720"`

**Q: Можно ли изменить персонажа в видео?**  
A: Нет, видео генерируется на основе выбранной девушки

**Q: Безопасно ли хранить видео в БД?**  
A: Да, но занимает много места. Можно отключить.

**Q: Работает ли без интернета?**  
A: Нет, требуется подключение к OpenAI API

## 🎉 Готово! / Ready!

Теперь ваши пользователи могут получать красивые видео от ИИ-девушек!

---

**Версия**: 2.1.0  
**Дата**: 10 октября 2025  
**Поддержка**: [GitHub Issues](https://github.com/yourusername/hayalkiz/issues)



