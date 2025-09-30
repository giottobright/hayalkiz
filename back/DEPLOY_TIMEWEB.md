# 🚀 Деплой на Timeweb.Cloud - Пошаговая инструкция

## ⚠️ Важно перед деплоем

**НЕ включайте файл `keys.env` в Docker-образ!**  
Все секретные ключи должны быть переданы через переменные окружения в панели Timeweb.Cloud.

## 📋 Шаг 1: Подготовка к деплою

### Проверьте файлы

Убедитесь, что у вас есть:
- ✅ `Dockerfile`
- ✅ `.dockerignore` (создан автоматически)
- ✅ `requirements.txt`
- ✅ `start.py`
- ✅ `app/` (папка с кодом)

### Не должно быть в образе:
- ❌ `keys.env` (будет игнорироваться)
- ❌ `__pycache__/`
- ❌ `.env`

## 📦 Шаг 2: Сборка Docker-образа

### Локальная проверка (опционально):

```bash
cd back

# Соберите образ
docker build -t hayalkiz-bot .

# Проверьте, что образ собрался
docker images | grep hayalkiz-bot

# Запустите локально для теста (установите переменные окружения)
docker run -p 8000:8000 \
  -e TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN" \
  -e OPENAI_API_KEY="YOUR_OPENAI_KEY" \
  -e WEBAPP_URL="https://your-webapp-url.com/" \
  -e FLUX_API_KEY="YOUR_FLUX_KEY" \
  -e FLUX_API_URL="https://api.bfl.ai/v1/flux-kontext-pro" \
  -e DATABASE_PATH="data/app.db" \
  hayalkiz-bot
```

### Проверка health-endpoint:

```bash
# В другом терминале
curl http://localhost:8000/health

# Должен вернуть:
# {"status":"ok","service":"hayalkiz-bot"}
```

## 🌐 Шаг 3: Деплой на Timeweb.Cloud

### Способ 1: Через Docker Hub

```bash
# 1. Залогиньтесь в Docker Hub
docker login

# 2. Тегируйте образ
docker tag hayalkiz-bot YOUR_DOCKERHUB_USERNAME/hayalkiz-bot:latest

# 3. Загрузите на Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/hayalkiz-bot:latest
```

Затем в Timeweb.Cloud:
1. Создайте новый контейнер
2. Укажите образ: `YOUR_DOCKERHUB_USERNAME/hayalkiz-bot:latest`
3. Перейдите к Шагу 4

### Способ 2: Через Git + Timeweb.Cloud Auto-Deploy

```bash
# 1. Коммит изменений
git add .
git commit -m "Add logging and fix deploy"
git push origin main

# 2. В панели Timeweb.Cloud:
# - Подключите Git репозиторий
# - Укажите путь к Dockerfile: back/Dockerfile
# - Установите переменные окружения (см. Шаг 4)
```

### Способ 3: Через Timeweb.Cloud CLI

```bash
# Установите Timeweb.Cloud CLI (если есть)
# Следуйте документации Timeweb.Cloud
```

## ⚙️ Шаг 4: Настройка переменных окружения

**КРИТИЧЕСКИ ВАЖНО!** В панели управления контейнером на Timeweb.Cloud установите:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
OPENAI_API_KEY=your_openai_api_key
WEBAPP_URL=https://your-webapp-url.com/
FLUX_API_KEY=your_flux_api_key
FLUX_API_URL=https://api.bfl.ai/v1/flux-kontext-pro
DATABASE_PATH=data/app.db
```

**Примечание:** Замените значения на ваши реальные ключи из файла `keys.env`

### Где установить переменные:

1. Откройте панель управления контейнером
2. Найдите раздел "Environment Variables" или "Переменные окружения"
3. Добавьте каждую переменную отдельно
4. Сохраните

## 🔧 Шаг 5: Настройка портов

В настройках контейнера укажите:
- **Внутренний порт:** 8000
- **Внешний порт:** 8000 (или любой доступный)
- **Протокол:** HTTP

## 🚀 Шаг 6: Запуск и проверка

### 1. Запустите контейнер

В панели Timeweb.Cloud нажмите "Start" или "Deploy"

### 2. Проверьте логи (ВАЖНО!)

1. Откройте раздел "Логи" в панели контейнера
2. Дождитесь появления строк:

```
🚀 ЗАПУСК ПРИЛОЖЕНИЯ HAYALKIZ
✅ HayalKiz Bot успешно запущен
🚀 Запуск polling...
🌐 Запуск health-check сервера на порту 8000...
```

### 3. Проверьте health-endpoint

```bash
curl http://YOUR_APP_URL:8000/health
```

Должен вернуть: `{"status":"ok","service":"hayalkiz-bot"}`

### 4. Проверьте бота

1. Откройте вашего бота в Telegram
2. Отправьте `/start`
3. **Сразу вернитесь к логам!**
4. Должна появиться строка:
   ```
   👤 /start от пользователя 123456789
   ```

## ❌ Что делать, если ошибка деплоя

### Ошибка: "Deploy error"

**Причины:**

1. **Проблема с Dockerfile**
   ```bash
   # Проверьте локально
   docker build -t test-build back/
   # Смотрите, на каком шаге ошибка
   ```

2. **Проблема с requirements.txt**
   ```bash
   # Проверьте, что все пакеты доступны
   pip install -r back/requirements.txt
   ```

3. **Проблема с путями**
   - Убедитесь, что путь к Dockerfile правильный
   - Если деплоите из корня репозитория, путь: `back/Dockerfile`
   - Если из папки `back`, путь: `Dockerfile`

4. **Проблема с памятью**
   - Увеличьте лимит памяти контейнера в настройках
   - Минимум: 512MB
   - Рекомендуется: 1GB

### Ошибка: Build timeout

**Решение:**
1. Удалите документацию из образа (уже в .dockerignore)
2. Оптимизируйте Dockerfile:

```dockerfile
# Используйте кэширование слоев
FROM python:3.12-slim

WORKDIR /app

# Сначала только requirements для кэширования
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем код
COPY app/ app/
COPY start.py .

RUN mkdir -p /app/data
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
CMD ["python", "start.py"]
```

## 🔍 Диагностика проблем

### Логи показывают успешный запуск, но бот не отвечает

1. **Проверьте токен бота:**
   ```bash
   # Получите новый токен через @BotFather
   /newbot или /token
   ```

2. **Проверьте переменные окружения:**
   - Все ли переменные установлены?
   - Нет ли опечаток в названиях?
   - Правильно ли скопированы значения?

3. **Проверьте логи при отправке /start:**
   - Если нет строки с 👤 - бот не получает сообщения
   - Проверьте, запущен ли polling в логах

### Health-endpoint не отвечает

1. Проверьте порты (должен быть 8000)
2. Проверьте, что контейнер запущен
3. Проверьте логи - есть ли строка "🌐 Запуск health-check сервера"?

## 📊 Мониторинг

После успешного деплоя в логах будет видно:

- Каждый запрос к боту
- Каждое сообщение пользователя
- Все ошибки

Держите окно логов открытым при тестировании!

## ✅ Checklist успешного деплоя

- [ ] Docker-образ собирается локально без ошибок
- [ ] `.dockerignore` создан и исключает `keys.env`
- [ ] Все переменные окружения установлены на Timeweb.Cloud
- [ ] Порт 8000 открыт и доступен
- [ ] Логи показывают "✅ HayalKiz Bot успешно запущен"
- [ ] Health-endpoint возвращает `{"status":"ok"}`
- [ ] Бот отвечает на `/start` в Telegram
- [ ] В логах видны сообщения от пользователей

## 🆘 Если ничего не помогает

1. Скопируйте **полные логи деплоя** из Timeweb.Cloud
2. Скопируйте **логи запуска контейнера**
3. Проверьте:
   - Какая именно строка с ❌ есть в логах?
   - На каком этапе деплоя происходит ошибка?
   - Все ли файлы скопированы в образ?

---

**Важно:** keys.env теперь в .dockerignore - при локальной сборке файл не будет включен в образ!
