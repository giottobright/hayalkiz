# ⚡ Быстрый чеклист для деплоя на TimeWeb Cloud

## ✅ Что исправлено (30.09.2025)

- [x] Асинхронная инициализация бота (не блокирует health check)
- [x] Убран keys.env из Dockerfile (используются переменные TimeWeb)
- [x] Увеличен timeout для health check
- [x] Обработка ошибок при инициализации

## 📋 Перед деплоем проверьте:

### 1. Переменные окружения в TimeWeb Cloud (бэкенд)
```
✓ TELEGRAM_BOT_TOKEN
✓ OPENAI_API_KEY  
✓ FLUX_API_KEY
✓ WEBAPP_URL
✓ WEBHOOK_URL
✓ DATABASE_PATH=data/app.db
✓ FLUX_API_URL
```

### 2. Git репозиторий
```bash
git status  # Все изменения закоммичены?
git push    # Все отправлено на сервер?
```

### 3. После деплоя (подождите 1-2 минуты)

**Проверка 1: Health Check**
```
https://giottobright-back-29f3.twc1.net/health
```
Ожидается: `{"status": "ok", "initialized": true}`

**Проверка 2: Telegram Bot**
- Отправьте `/start` боту
- Ожидается: Выбор языка → Mini App кнопка

**Проверка 3: Webhook**
Смотрим в логи TimeWeb:
```
✅ Webhook установлен: https://giottobright-back-29f3.twc1.net/webhook
```

## 🚨 Если что-то пошло не так

| Проблема | Решение |
|----------|---------|
| Health check возвращает ошибку | Проверьте логи деплоя в TimeWeb |
| `"initialized": false` | Подождите 30-40 секунд, проверьте снова |
| Бот не отвечает | Проверьте TELEGRAM_BOT_TOKEN в переменных |
| Webhook не установлен | Проверьте WEBHOOK_URL в переменных |
| GPT не работает | Проверьте OPENAI_API_KEY |
| Селфи не генерируются | Проверьте FLUX_API_KEY |

## 📞 Команды для деплоя

```bash
# 1. Закоммитить изменения
git add .
git commit -m "Fix TimeWeb deployment"
git push

# 2. TimeWeb Cloud автоматически задеплоит
# 3. Ждем 1-2 минуты
# 4. Проверяем health check
curl https://giottobright-back-29f3.twc1.net/health
```

## 🎯 Ожидаемый результат

```json
{
  "status": "ok",
  "service": "hayalkiz-bot", 
  "initialized": true
}
```

И бот отвечает на `/start` в Telegram! 🎉
