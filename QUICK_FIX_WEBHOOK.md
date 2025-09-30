# 🚀 Быстрое исправление бота / Quick Bot Fix

## Проблема
✖️ Бот развернут на Timeweb, но не отвечает на `/start`

## Причина
Бот работал в **polling** режиме, который не работает на production серверах. Нужен **webhook**.

## ✅ Решение (3 простых шага)

### Шаг 1: Загрузите изменения на сервер

Все изменения уже сделаны в коде! Просто загрузите их:

```bash
git add .
git commit -m "Переключение на webhook режим"
git push
```

### Шаг 2: Проверьте переменные окружения

Убедитесь, что в вашем `back/keys.env` есть:

```env
WEBHOOK_URL=https://giottobright-back-29f3.twc1.net/webhook
```

✅ Эта переменная уже добавлена в файл!

### Шаг 3: Перезапустите приложение на Timeweb

На Timeweb приложение должно автоматически перезапуститься после `git push`.

Если нет:
1. Зайдите в панель управления Timeweb
2. Найдите ваше приложение
3. Нажмите "Перезапустить" / "Restart"

## 🧪 Проверка

1. Откройте бота в Telegram: [@your_bot](https://t.me/your_bot)
2. Отправьте команду `/start`
3. Бот должен ответить выбором языка! ✅

## 📊 Диагностика (если не работает)

### Проверьте webhook статус:

```bash
curl https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo
```

Должно быть:
```json
{
  "ok": true,
  "result": {
    "url": "https://giottobright-back-29f3.twc1.net/webhook",
    "pending_update_count": 0
  }
}
```

### Проверьте health endpoint:

```bash
curl https://giottobright-back-29f3.twc1.net/health
```

Должно вернуть:
```json
{"status": "ok", "service": "hayalkiz-bot"}
```

### Проверьте логи на Timeweb:

1. Откройте панель Timeweb
2. Перейдите в раздел "Логи" / "Logs"
3. Найдите строки:
   ```
   ✅ Webhook установлен: https://giottobright-back-29f3.twc1.net/webhook
   ✅ HayalKiz Bot успешно запущен
   ```

## 🆘 Если всё еще не работает

### Сбросьте webhook вручную:

```bash
# Удалите старый webhook
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/deleteWebhook

# Установите новый
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://giottobright-back-29f3.twc1.net/webhook"}'
```

Затем перезапустите приложение на Timeweb.

## 📝 Что было изменено

1. **`back/start.py`** - переключен с polling на webhook
2. **`back/app/config.py`** - добавлена переменная `webhook_url`
3. **`back/app/main.py`** - добавлена функция `init_bot()` для webhook
4. **`back/keys.env`** - добавлена переменная `WEBHOOK_URL`

## 📚 Подробная документация

Смотрите полную документацию в файле [`back/WEBHOOK_SETUP.md`](back/WEBHOOK_SETUP.md)

---

## ⚡ Quick Fix (English)

### Problem
✖️ Bot deployed on Timeweb but doesn't respond to `/start`

### Cause
Bot was in **polling** mode, which doesn't work on production servers. Need **webhook**.

### Solution (3 steps)

1. **Push changes** (already done in code):
   ```bash
   git add .
   git commit -m "Switch to webhook mode"
   git push
   ```

2. **Check environment variables** - `WEBHOOK_URL` is already set in `back/keys.env`

3. **Restart app on Timeweb** - should auto-restart after git push

### Test
1. Open bot in Telegram
2. Send `/start`
3. Bot should respond! ✅

See full docs in [`back/WEBHOOK_SETUP.md`](back/WEBHOOK_SETUP.md)
