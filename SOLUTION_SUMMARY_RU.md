# 📝 Резюме: Решение проблемы генерации фото на проде

## Проблема
**Симптом:** Генерация фото недоступна на продакшене (TimeWeb Cloud), хотя локально все работает.

**Причина:** На сервере не установлена переменная окружения `GEMINI_API_KEY`, которая критически важна для генерации изображений через Gemini API.

## Диагностика

### До исправления
Health endpoint показывал:
```json
{
  "initialized": true,
  "bot_is_none": false,
  "dp_is_none": false,
  "import_error": null,
  "env_vars": {
    "TELEGRAM_BOT_TOKEN": "set",
    "OPENAI_API_KEY": "set",
    "WEBAPP_URL": "https://giottobright-webapp-cd8e.twc1.net/",
    "WEBHOOK_URL_env": "not set in env",
    "WEBHOOK_URL_actual": "https://giottobright-back-3800.twc1.net/webhook",
    "DATABASE_PATH": "data/app.db"
  }
}
```

**Проблема:** `GEMINI_API_KEY` вообще не проверялся!

### После исправления
Debug endpoint (`/debug`) теперь показывает:
```json
{
  "env_vars": {
    "TELEGRAM_BOT_TOKEN": "set",
    "OPENAI_API_KEY": "set",
    "GEMINI_API_KEY": "set" или "NOT SET - REQUIRED FOR IMAGE GENERATION",
    "FLUX_API_KEY": "set" или "not set (optional)",
    "FLUX_API_URL": "https://..." или "not set (will use default)"
  }
}
```

## Что было сделано

### 1. Обновлен debug endpoint (`back/start.py`)
- ✅ Добавлена проверка `GEMINI_API_KEY`
- ✅ Добавлена проверка `FLUX_API_KEY`
- ✅ Добавлена проверка `FLUX_API_URL`
- ✅ Понятные сообщения о статусе каждой переменной

### 2. Обновлена документация деплоя (`back/DEPLOY_TIMEWEB.md`)
- ✅ Добавлен `GEMINI_API_KEY` в список обязательных переменных
- ✅ Добавлено предупреждение о важности этого ключа
- ✅ Обновлены примеры Docker команд

### 3. Обновлен docker-compose.yml
- ✅ Добавлена переменная `GEMINI_API_KEY` в секцию environment

### 4. Созданы инструкции по исправлению
- ✅ **FIX_IMAGE_GENERATION.md** - подробная инструкция на английском
- ✅ **QUICK_FIX_IMAGE_GENERATION_RU.md** - быстрая инструкция на русском

## Решение для пользователя

### Вариант 1: Через веб-интерфейс TimeWeb (Рекомендуется)

1. Зайдите на https://timeweb.cloud/
2. Откройте приложение `giottobright-back-3800`
3. Settings → Environment Variables
4. Добавьте переменную:
   - **Имя:** `GEMINI_API_KEY`
   - **Значение:** `AIzaSyApvDQafuIxHcAyBc5FVy_vbP8KuRNQJhc`
5. Save → Restart
6. Подождите 30-60 секунд
7. Проверьте: `https://giottobright-back-3800.twc1.net/debug`

### Вариант 2: Через .env файл на сервере (если есть SSH доступ)

```bash
# SSH на сервер
ssh your-server

# Перейдите в директорию приложения
cd /path/to/app

# Добавьте переменную в .env
echo "GEMINI_API_KEY=AIzaSyApvDQafuIxHcAyBc5FVy_vbP8KuRNQJhc" >> .env

# Перезапустите
docker-compose restart
```

## Проверка результата

### 1. Проверьте debug endpoint
```
https://giottobright-back-3800.twc1.net/debug
```

Должно быть:
```json
{
  "env_vars": {
    "GEMINI_API_KEY": "set"
  }
}
```

### 2. Протестируйте бота
1. Откройте бота в Telegram
2. Выберите персонажа
3. Запросите селфи
4. Генерация должна работать!

## Дополнительные переменные (опционально)

Для расширенной функциональности также можно добавить:

```
FLUX_API_KEY=01483a08-56ae-494b-bbd1-20daf4cad819
FLUX_API_URL=https://api.bfl.ai/v1/flux-pro-1.1-ultra
```

## Почему это работало локально?

Локально переменные загружались из файла `back/keys.env`:
```env
GEMINI_API_KEY=AIzaSyApvDQafuIxHcAyBc5FVy_vbP8KuRNQJhc
```

На проде (TimeWeb Cloud) переменные должны быть установлены через:
- Панель управления → Environment Variables
- .env файл на сервере
- docker-compose.yml environment секцию

## Файлы для справки

- **Быстрое решение:** `QUICK_FIX_IMAGE_GENERATION_RU.md`
- **Подробная инструкция:** `FIX_IMAGE_GENERATION.md`
- **Деплой:** `back/DEPLOY_TIMEWEB.md`
- **Пример переменных:** `back/keys.example.env`

## Чек-лист

- [ ] Открыта панель TimeWeb Cloud
- [ ] Найдено приложение giottobright-back-3800
- [ ] Добавлена переменная GEMINI_API_KEY
- [ ] Приложение перезапущено
- [ ] Debug endpoint показывает "set"
- [ ] Генерация фото в боте работает

---

**Статус:** ✅ Проблема диагностирована и решение готово

**Следующий шаг:** Добавить `GEMINI_API_KEY` в переменные окружения на TimeWeb Cloud

