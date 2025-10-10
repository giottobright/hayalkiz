# 🎬 Video Generation Feature Guide

## Обзор / Overview

Добавлена возможность генерации видео с помощью OpenAI Sora 2 API.  
Added video generation capability using OpenAI Sora 2 API.

## Возможности / Features

### 1. Видео из селфи (Video from Selfie)

Пользователь может запросить видео на основе последнего сгенерированного селфи:
- Берется промпт последнего селфи
- GPT анализирует промпт и создает новый промпт для видео по стандартам Sora 2
- Sora 2 генерирует 5-секундное вертикальное видео (720x1280) на основе селфи

### 2. Новое видео (New Video)

Создание видео с нуля:
1. Генерируется промпт для нового селфи (GPT)
2. Создается селфи (Gemini)
3. На основе промпта селфи генерируется промпт для видео (GPT)
4. Создается видео (Sora 2)

## Архитектура

### Новые файлы

1. **`back/app/services_sora.py`** - сервис для работы с Sora 2 API
   - `generate_video()` - основной метод генерации видео
   - Поддержка image-to-video и text-to-video режимов
   - Polling для async задач
   
2. **Обновленные файлы:**
   - `back/app/services_gpt.py` - добавлен `build_video_prompt()` для генерации промптов видео
   - `back/app/db.py` - добавлена таблица `generated_content` для хранения промптов и контента
   - `back/app/main.py` - добавлены:
     - Кнопка "🎬 Video gönder" / "🎬 Отправь видео"
     - `generate_video_from_selfie()` - генерация видео из последнего селфи
     - `generate_new_video()` - генерация нового видео с нуля
     - Обработчики callback для выбора типа видео

### База данных

Новая таблица `generated_content`:
```sql
CREATE TABLE generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    content_type TEXT,  -- 'selfie' или 'video'
    prompt TEXT,
    file_data BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Использование / Usage

### Для пользователя

1. Выбрать девушку через Mini App
2. Нажать кнопку "🎬 Video gönder" / "🎬 Отправь видео"
3. Выбрать один из вариантов:
   - "📸➡️🎬 Son selfie'den video yap" - видео из последнего селфи
   - "✨ Yeni video oluştur" - создать новое видео

### Технические детали

#### Параметры видео:
- **Длительность**: 5 секунд (настраивается: 4, 8 или 12)
- **Разрешение**: 720x1280 (вертикальное)
- **Модель**: sora-2 (можно использовать sora-2-pro для больших разрешений)
- **Качество**: HD 720p

#### Процесс генерации промптов для видео:

GPT получает:
- Оригинальный промпт селфи
- Персону и ее характер
- Инструкции по формату Sora 2 (из документации)

GPT создает промпт включающий:
- **Style & Format** - стиль видео (1-2 предложения)
- **Scene description** - описание сцены с локацией, освещением (2-3 предложения)
- **Cinematography** - камера, объектив, освещение, настроение (2-3 предложения)
- **Actions** - что происходит за 5 секунд (1 главное действие)
- **Background Sound** - только ambient звуки

#### Эротический контент:

В 50% случаев добавляются соблазнительные элементы:
- Флирт с камерой
- Игривый взгляд
- Приглашающие жесты
- Tasteful показ кожи

Это контролируется в `services_gpt.py:build_video_prompt()`:
```python
is_seductive = random.random() < 0.5
```

## API Reference

### SoraService

```python
class SoraService:
    async def generate_video(
        self,
        prompt: str,
        *,
        image_bytes: Optional[bytes] = None,
        image_url: Optional[str] = None,
        duration: int = 5,
        size: str = "720x1280",
        model: str = "sora-2"
    ) -> Optional[bytes]
```

**Параметры:**
- `prompt` - текстовое описание видео
- `image_bytes` - стартовое изображение (для image-to-video)
- `image_url` - URL стартового изображения
- `duration` - длительность в секундах (4, 8, 12)
- `size` - разрешение видео
- `model` - модель Sora (`sora-2` или `sora-2-pro`)

**Возвращает:**
- `bytes` - видео в формате MP4
- `None` - если генерация не удалась

### GPTService

```python
def build_video_prompt(
    self,
    *,
    persona: Persona,
    photo_prompt: str,
    user_lang: str = "tr"
) -> str
```

**Параметры:**
- `persona` - персона девушки
- `photo_prompt` - промпт использованный для генерации селфи
- `user_lang` - язык пользователя

**Возвращает:**
- `str` - промпт для Sora 2 на английском языке

## Конфигурация / Configuration

### Environment Variables

Используется существующий `OPENAI_API_KEY` из `back/keys.env`:
```env
OPENAI_API_KEY=sk-proj-...
```

Sora 2 API использует тот же ключ что и GPT.

### Настройка параметров видео

В `services_sora.py` можно изменить дефолтные параметры:

```python
# Длительность (4, 8 или 12 секунд)
duration: int = 5

# Разрешение (вертикальное или горизонтальное)
size: str = "720x1280"  # вертикальное
# size: str = "1280x720"  # горизонтальное

# Модель
model: str = "sora-2"  # базовая
# model: str = "sora-2-pro"  # для больших разрешений
```

### Настройка вероятности эротического контента

В `services_gpt.py:build_video_prompt()`:

```python
# 50% вероятность
is_seductive = random.random() < 0.5

# Всегда эротично:
# is_seductive = True

# Никогда:
# is_seductive = False

# 75% вероятность:
# is_seductive = random.random() < 0.75
```

## Troubleshooting

### Видео не генерируется

1. **Проверить API ключ**: убедиться что `OPENAI_API_KEY` установлен в `back/keys.env`
2. **Проверить логи**: 
   ```bash
   # Логи покажут этапы генерации
   [Sora] Starting video generation...
   [Sora] Request payload: {...}
   [Sora] Poll 1/120: status=processing
   [Sora] Poll 15/120: status=completed
   ```
3. **Проверить лимиты API**: Sora 2 может иметь rate limits
4. **Timeout**: генерация видео может занять до 2 минут

### Ошибка "Önce bir selfie oluştur"

Пользователь пытается создать видео из селфи, но еще не генерировал селфи.  
**Решение**: сначала создать селфи через кнопку "📸 Selfie göster"

### Большой размер видео файла

Sora 2 генерирует HD видео, размер файла может быть 5-20 MB.  
**Решение**: Telegram поддерживает до 50 MB для видео.

## Производительность / Performance

- **Генерация видео из селфи**: ~30-60 секунд
- **Генерация нового видео**: ~60-120 секунд (включает генерацию селфи)
- **Размер видео**: 5-20 MB для 5-секундного HD видео

## Безопасность / Security

- Промпты и контент сохраняются в локальной SQLite БД
- API ключи хранятся в `keys.env` (не коммитятся в git)
- Файлы видео хранятся в БД в формате BLOB (можно отключить для экономии места)

## Будущие улучшения / Future Improvements

- [ ] Поддержка разных стилей видео (cinematic, documentary, etc)
- [ ] Кастомизация длительности через UI
- [ ] Предпросмотр стартового кадра перед генерацией
- [ ] История сгенерированных видео
- [ ] Экспорт видео на внешнее хранилище (S3)
- [ ] Поддержка transitions между несколькими сценами

## Примеры промптов / Example Prompts

### Пример селфи промпта:
```
Ultra-photorealistic portrait of Elif, a beautiful 24-year-old Turkish woman 
with soft chestnut hair, hazel eyes reflecting warm light. She sits at a 
window-side table in a modern Istanbul café, golden hour sunlight streaming 
through windows. Shot on iPhone 15 Pro, 77mm telephoto, f/2.8.
```

### Пример видео промпта (сгенерирован GPT):
```
Style: Cinematic vertical video, natural golden hour lighting, iPhone quality.

In a modern Istanbul café by the window, Elif, a beautiful 24-year-old Turkish 
woman with soft chestnut hair, sits with a warm smile. Golden hour sunlight 
streams through floor-to-ceiling windows, casting soft shadows. She holds a 
poetry book, her hazel eyes reflecting the ambient light.

Cinematography: Medium close-up, 50mm, f/2.8, slow push-in from waist-up to 
shoulder shot, shallow depth of field creating bokeh background. Natural key 
light from left window, soft ambient café fill.

Actions: She looks up from the book towards camera, her smile deepening, makes 
gentle eye contact with a slight head tilt, then glances back at the book with 
a content expression.

Background Sound: Soft café ambience, light street traffic, pages rustling.
```

## Контакты / Contact

Для вопросов и поддержки:
- GitHub Issues
- Telegram: @yourusername



