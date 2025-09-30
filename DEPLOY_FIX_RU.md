# 🛠️ Исправление проблемы деплоя на TimeWeb Cloud

## ❌ Проблема
```
WARNING | Cannot get HTTP 200 for domain giottobright-back-29f3.twc1.net
```

## ✅ Решение

### Что было сделано:

1. **Убрали блокирующую инициализацию**
   - Health endpoint теперь отвечает сразу
   - Бот инициализируется в фоновом режиме
   - Webhook устанавливается после запуска

2. **Исправили Dockerfile**
   - Убрали `COPY keys.env .` (переменные берутся из TimeWeb Cloud)
   - Увеличили время для health check до 40 секунд

3. **Сделали config.py гибким**
   - Работает с переменными окружения TimeWeb Cloud
   - Не требует файл keys.env в продакшене

## 📝 Что нужно проверить в TimeWeb Cloud

Откройте настройки деплоя бэкенда и убедитесь, что заданы все переменные окружения:

```
TELEGRAM_BOT_TOKEN=ваш_telegram_bot_token
OPENAI_API_KEY=ваш_openai_api_key
FLUX_API_KEY=ваш_flux_api_key
WEBAPP_URL=https://giottobright-webapp-cd8e.twc1.net/
WEBHOOK_URL=https://giottobright-back-29f3.twc1.net/webhook
DATABASE_PATH=data/app.db
FLUX_API_URL=https://api.bfl.ai/v1/flux-kontext-pro
```

> ⚠️ **Важно:** Используйте реальные ключи из вашего локального файла `keys.env`

## 🚀 Как задеплоить

1. **Закоммитьте изменения**:
   ```bash
   git add .
   git commit -m "Fix TimeWeb deployment - async init & remove keys.env"
   git push
   ```

2. **Запустите деплой** в TimeWeb Cloud

3. **Проверьте health check** (через 1-2 минуты):
   ```
   https://giottobright-back-29f3.twc1.net/health
   ```
   
   Должен вернуть:
   ```json
   {
     "status": "ok",
     "service": "hayalkiz-bot",
     "initialized": true
   }
   ```

4. **Проверьте бота** в Telegram:
   - Отправьте `/start`
   - Выберите язык
   - Откройте Mini App
   - Выберите девушку
   - Напишите сообщение

## 📊 Что смотреть в логах

**Успешный запуск:**
```
✅ Конфигурация загружена
✅ Все сервисы инициализированы
✅ База данных инициализирована
✅ Webhook установлен
✅ Полная инициализация завершена
```

**Если что-то не так:**
- `❌ TELEGRAM_BOT_TOKEN не установлен` → проверьте переменные в настройках TimeWeb
- `❌ Ошибка установки webhook` → проверьте WEBHOOK_URL
- `⚠️ Бот еще не инициализирован` → подождите 30-40 секунд

## ✨ Весь функционал сохранен

- ✅ Telegram бот с Mini App
- ✅ Выбор языка (Турецкий/Русский)
- ✅ 8 персон девушек
- ✅ Диалоги через GPT-4
- ✅ Генерация селфи через Flux
- ✅ Webhook режим
- ✅ История сообщений

## 🔍 Дополнительно

Если после деплоя бот не отвечает:
1. Проверьте логи деплоя в TimeWeb Cloud
2. Откройте `/health` endpoint и посмотрите `"initialized": true/false`
3. Проверьте, что все переменные окружения заданы правильно
