# 🔧 Исправление Endpoint для Sora API

## ✅ Что было исправлено

### 1. Правильный endpoint

**Было (неправильно):**
```python
self.endpoint = "https://api.openai.com/v1/video/generations"
```

**Стало (правильно):**
```python
self.endpoint = "https://api.openai.com/v1/videos"
```

### 2. Endpoint для polling

**Было:**
```python
status_url = f"https://api.openai.com/v1/video/generations/{task_id}"
```

**Стало:**
```python
status_url = f"https://api.openai.com/v1/videos/{task_id}"
```

---

## 🧪 Как проверить

### Запустите тест endpoint:

```bash
cd back
python test_sora_endpoint.py
```

Этот тест проверит:
1. ✅ Доступность разных endpoints
2. ✅ Наличие Sora моделей в списке
3. ✅ Правильность API ключа

### Что вы увидите:

#### Если API доступен:
```
✅ SUCCESS - Endpoint works!
```
или
```
✅ CREATED - Video generation started!
```

#### Если API еще не доступен:
```
❌ NOT FOUND - Endpoint doesn't exist
```

#### Если проблема с доступом:
```
⚠️  FORBIDDEN - No access to this endpoint
```

---

## 📊 Проверка доступных моделей

Тест также проверяет список моделей OpenAI:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Если Sora доступен**, вы увидите модели типа:
- `sora-2`
- `sora-2-pro`
- или похожие

**Если не доступен**, в списке будут только:
- `gpt-4o`
- `gpt-4`
- `dall-e-3`
- и т.д.

---

## 🎯 Текущий статус

После исправления endpoint, возможны два сценария:

### Сценарий 1: API заработает ✅

Если у вас есть доступ к Sora API, после перезапуска бота:

```bash
cd back
python start.py
```

Видео начнут генерироваться!

### Сценарий 2: Всё еще 404 ⏰

Если всё еще получаете 404, это означает:
- Endpoint правильный
- Но API еще не открыт для вашего аккаунта

---

## 📝 Изменённые файлы

1. ✅ **`back/app/services_sora.py`**
   - Строка 85: исправлен основной endpoint
   - Строка 216: исправлен polling endpoint

2. ✅ **`back/test_sora_endpoint.py`** (новый)
   - Тест доступности endpoints
   - Проверка моделей

---

## 🚀 Шаги после исправления

### 1. Перезапустить бота

```bash
cd back
python start.py
```

### 2. Проверить логи

Смотрите на логи при инициализации:
```
✅ Sora сервис инициализирован
```

### 3. Попробовать создать видео

В Telegram:
1. Создайте селфи
2. Нажмите "🎬 Видео"
3. Выберите режим

### 4. Проверить результат

**Если работает:**
```
🎬 Starting Sora video generation...
   Endpoint: https://api.openai.com/v1/videos
[Sora] Status: processing
[Sora] Status: completed
✅ Video downloaded
```

**Если всё еще 404:**
```
❌ Sora API endpoint not found (404)
   Endpoint attempted: https://api.openai.com/v1/videos
```

Это означает что API еще не доступен для вашего ключа.

---

## 💡 Дополнительные проверки

### Проверка 1: API ключ валиден?

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

Должен вернуть список моделей (не ошибку 401).

### Проверка 2: Есть ли доступ к новым моделям?

Проверьте на platform.openai.com:
- Settings → Limits
- API Keys → Permissions

### Проверка 3: Попробовать разные endpoints

Тест `test_sora_endpoint.py` автоматически проверит:
- `/v1/videos` (правильный)
- `/v1/video/generations` (старый, для сравнения)

---

## 📞 Что делать если всё еще не работает

### 1. Убедитесь что исправления применены

```bash
cd back
grep "v1/videos" app/services_sora.py
```

Должны увидеть:
```python
self.endpoint = "https://api.openai.com/v1/videos"
```

### 2. Запустите полный тест

```bash
cd back
python test_sora_endpoint.py
```

### 3. Проверьте вывод

Если видите **404 на всех video endpoints** - API еще не доступен.

Если видите **400/403** - endpoint существует, но нужно:
- Запросить доступ на platform.openai.com
- Проверить права API ключа
- Дождаться активации

### 4. Свяжитесь с OpenAI

Если тест показывает что endpoint существует (400/403), но не работает:
1. Перейдите на platform.openai.com/account/limits
2. Проверьте доступные модели
3. Запросите доступ к Sora через Help → Contact Support

---

## ✅ Checklist проверки

После исправления проверьте:

- [ ] Endpoint изменен на `/v1/videos`
- [ ] Polling endpoint также исправлен
- [ ] Бот перезапущен
- [ ] Тест `test_sora_endpoint.py` запущен
- [ ] Логи проверены
- [ ] Попытка создать видео в Telegram

Если всё ✅ но всё еще 404 - просто ждем открытия API.

---

## 🎯 TL;DR

**Исправлено:**
- ✅ Endpoint: `/v1/video/generations` → `/v1/videos`
- ✅ Добавлен тест endpoint

**Что делать:**
```bash
cd back
python test_sora_endpoint.py  # Проверить доступность
python start.py                # Перезапустить бота
```

**Результат:**
- Если endpoint доступен → Видео заработает! 🎉
- Если всё еще 404 → Ждем открытия API ⏰

---

**Версия**: 2.1.2  
**Дата**: 10 октября 2025  
**Исправление**: Правильный endpoint для Sora API



