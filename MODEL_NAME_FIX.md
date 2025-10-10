# 🔧 Исправление: Неправильное название модели

## ❌ Проблема

**Ошибка:**
```
"Model variant gen4-turbo is not available"
```

**Причина:** Неправильное название модели в запросе к Runway API.

---

## ✅ Исправления

### 1. Изменено название модели

**Было:**
```python
model: str = "gen4-turbo"
```

**Стало:**
```python
model: str = "gen4"
```

### 2. Добавлены дополнительные параметры

```python
payload = {
    "promptText": truncated_prompt,
    "model": model,
    "duration": duration,
    "ratio": "9:16",
    "watermark": False,  # ← добавлено
    "seed": None         # ← добавлено
}
```

---

## 🧪 Как проверить правильное название

### Запустите тест:

```bash
cd back
python test_runway_api.py
```

Этот тест проверит разные варианты названий моделей:
- `gen4`
- `gen4-turbo`
- `gen-4`
- `gen-4-turbo`
- `gen4_turbo`
- `gen_4_turbo`

### Что вы увидите:

**Правильная модель:**
```
✅ SUCCESS! Model 'gen4' works!
📋 Task ID: xxx-yyy-zzz
```

**Неправильная модель:**
```
❌ Error: Model variant gen4-turbo is not available
💡 Model 'gen4-turbo' is not available
```

---

## 🚀 Что делать СЕЙЧАС

### 1. Перезапустите бота:

```bash
cd back
python start.py
```

### 2. Попробуйте создать видео:

1. Создайте селфи
2. Нажмите "🎬 Видео"
3. Выберите "Из последнего селфи"

---

## 📊 Ожидаемые результаты

### В логах:

**Успех:**
```
🎬 Starting Runway Gen-4 Turbo video generation...
   Model: gen4, Size: 720x1280, Duration: 4s
   Original prompt length: 856 chars
[Runway] Request payload: {...}
[Runway] Got task ID: xxx-yyy-zzz
[Runway] Poll 1/120: status=processing, progress=15%
[Runway] Poll 5/120: status=succeeded, progress=100%
✅ Video downloaded: 8456234 bytes
```

**Если всё еще ошибка:**
```
❌ Runway API error 403: Model variant gen4 is not available
```

Тогда запустите тест и найдите правильное название.

---

## 🔧 Если нужно изменить модель

### В `services_runway.py`:

```python
model: str = "gen4"  # ← изменить на правильное название
```

### В `main.py`:

```python
model="gen4"  # ← изменить на правильное название
```

---

## 🎯 Возможные варианты названий

Согласно документации Runway, возможные варианты:
- `gen4` ✅ (используем сейчас)
- `gen-4`
- `gen4_turbo`
- `gen_4_turbo`

---

## 🚀 Попробуйте сейчас!

```bash
cd back
python start.py
```

Затем в Telegram создайте видео - теперь должно работать! 🎥✨

---

**Версия**: 3.0.2  
**Исправление**: Название модели  
**Статус**: ✅ Готово к тестированию

