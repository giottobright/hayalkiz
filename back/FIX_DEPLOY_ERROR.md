# 🔧 Исправление ошибки "Deploy error"

## ⚡ Быстрое решение

### Что было исправлено:

1. ✅ Создан `.dockerignore` - исключает секретные файлы из образа
2. ✅ Оптимизирован `Dockerfile` - улучшена совместимость с Timeweb.Cloud
3. ✅ Добавлен HEALTHCHECK в Dockerfile
4. ✅ Улучшена кодировка UTF-8

### 🚀 Что делать сейчас:

#### Вариант 1: Деплой через Git (рекомендуется)

```bash
# 1. Добавьте все изменения
git add .

# 2. Коммит
git commit -m "Fix deploy error: add .dockerignore and optimize Dockerfile"

# 3. Пуш
git push origin main
```

Затем в Timeweb.Cloud:
- Перейдите в настройки вашего приложения/контейнера
- Нажмите "Redeploy" или "Пересобрать"
- Подождите завершения сборки

#### Вариант 2: Локальная сборка и пуш

```bash
# 1. Перейдите в папку back
cd back

# 2. Соберите образ
docker build -t hayalkiz-bot .

# 3. Если сборка успешна, загрузите на Docker Hub
docker tag hayalkiz-bot YOUR_USERNAME/hayalkiz-bot:latest
docker push YOUR_USERNAME/hayalkiz-bot:latest
```

Затем в Timeweb.Cloud укажите образ: `YOUR_USERNAME/hayalkiz-bot:latest`

### ⚙️ Обязательно! Установите переменные окружения

В панели Timeweb.Cloud добавьте переменные (БЕЗ файла keys.env):

| Переменная | Значение |
|------------|----------|
| `TELEGRAM_BOT_TOKEN` | `YOUR_BOT_TOKEN_FROM_BOTFATHER` |
| `OPENAI_API_KEY` | `YOUR_OPENAI_API_KEY` |
| `WEBAPP_URL` | `https://your-webapp-url.com/` |
| `FLUX_API_KEY` | `YOUR_FLUX_API_KEY` |
| `FLUX_API_URL` | `https://api.bfl.ai/v1/flux-kontext-pro` |
| `DATABASE_PATH` | `data/app.db` |

### 📋 Частые причины "Deploy error"

| Проблема | Решение |
|----------|---------|
| **Файл keys.env в образе** | Теперь исключен через `.dockerignore` ✅ |
| **Неправильный путь к Dockerfile** | Убедитесь: если деплоите из корня - путь `back/Dockerfile` |
| **Недостаточно памяти** | Увеличьте лимит до 1GB в настройках контейнера |
| **Timeout при сборке** | Dockerfile оптимизирован для быстрой сборки ✅ |
| **Переменные окружения не установлены** | Установите ВСЕ 6 переменных выше |

### 🧪 Проверка локально (опционально)

Перед деплоем можно проверить локально:

```bash
cd back

# Сборка
docker build -t test-hayalkiz .

# Если ошибка - смотрите, на каком шаге
# Если успех - запустите:
docker run -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN="YOUR_TOKEN" \
  -e OPENAI_API_KEY="YOUR_KEY" \
  -e WEBAPP_URL="https://giottobright-webapp-cd8e.twc1.net/" \
  test-hayalkiz

# Проверьте в другом терминале:
curl http://localhost:8000/health
# Должен вернуть: {"status":"ok","service":"hayalkiz-bot"}
```

### ✅ После успешного деплоя

1. **Откройте логи на Timeweb.Cloud**
2. Найдите строки:
   ```
   🚀 ЗАПУСК ПРИЛОЖЕНИЯ HAYALKIZ
   ✅ HayalKiz Bot успешно запущен
   ```
3. **Проверьте бота** - отправьте `/start`
4. **Вернитесь к логам** - должна быть строка:
   ```
   👤 /start от пользователя ...
   ```

### ❌ Если всё ещё ошибка

1. **Скопируйте полные логи ошибки** из Timeweb.Cloud
2. **Проверьте:**
   - Путь к Dockerfile правильный?
   - Все переменные окружения установлены?
   - Достаточно ли памяти (min 512MB)?
   - Открыт ли порт 8000?

3. **Попробуйте собрать локально:**
   ```bash
   cd back
   docker build -t test .
   ```
   Если локально ошибка - проблема в коде/Dockerfile  
   Если локально OK - проблема в настройках Timeweb.Cloud

### 📊 Что изменилось в файлах

1. **`.dockerignore`** (новый файл) - исключает keys.env из образа
2. **`Dockerfile`** - оптимизирован, добавлен healthcheck
3. **`start.py`** - улучшено логирование
4. **`app/main.py`** - детальные логи всех операций

### 🎯 Главное

**Секретные ключи НЕ должны быть в Docker-образе!**  
Все ключи передаются через переменные окружения в панели Timeweb.Cloud.

---

**Следующий шаг:** Попробуйте деплой сейчас и проверьте логи!
