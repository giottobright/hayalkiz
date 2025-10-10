# Исправление проблемы генерации изображений на TimeWeb Cloud

## Проблема
Генерация фото не работает на проде, потому что не установлены необходимые переменные окружения для API генерации изображений.

## Диагностика
Проверьте endpoint `/debug` или `/health` вашего бэкенда:
```
https://giottobright-back-3800.twc1.net/debug
```

Если видите:
```json
{
  "env_vars": {
    "GEMINI_API_KEY": "NOT SET - REQUIRED FOR IMAGE GENERATION"
  }
}
```

Значит проблема подтверждена.

## Решение

### Шаг 1: Найдите ваши API ключи
В файле `back/keys.env` (локально) находятся ваши ключи:
- `GEMINI_API_KEY` - **ОБЯЗАТЕЛЬНО** для генерации изображений
- `FLUX_API_KEY` - опционально (для альтернативной генерации)
- `FLUX_API_URL` - опционально (для Flux API)

### Шаг 2: Добавьте переменные окружения в TimeWeb Cloud

#### Вариант 1: Через веб-интерфейс TimeWeb
1. Зайдите в панель управления TimeWeb Cloud
2. Откройте ваше приложение (giottobright-back)
3. Перейдите в раздел **"Переменные окружения"** или **"Settings"** → **"Environment Variables"**
4. Добавьте следующие переменные:

```
GEMINI_API_KEY=AIzaSyApvDQafuIxHcAyBc5FVy_vbP8KuRNQJhc
FLUX_API_KEY=01483a08-56ae-494b-bbd1-20daf4cad819
FLUX_API_URL=https://api.bfl.ai/v1/flux-pro-1.1-ultra
```

5. Сохраните изменения
6. Перезапустите приложение (обычно происходит автоматически)

#### Вариант 2: Через docker-compose.yml (если используете Docker)
Добавьте в секцию `environment` вашего сервиса:

```yaml
services:
  bot:
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GEMINI_API_KEY=${GEMINI_API_KEY}  # ← Добавьте эту строку
      - FLUX_API_KEY=${FLUX_API_KEY}      # ← И эту (опционально)
      - FLUX_API_URL=${FLUX_API_URL}      # ← И эту (опционально)
      - WEBAPP_URL=${WEBAPP_URL}
      - DATABASE_PATH=data/app.db
```

#### Вариант 3: Через файл .env на сервере
Если TimeWeb использует .env файлы, создайте/обновите `.env` на сервере:

```bash
# SSH в ваш сервер
ssh your-server

# Перейдите в директорию приложения
cd /path/to/your/app

# Создайте/обновите .env файл
nano .env

# Добавьте строки:
GEMINI_API_KEY=AIzaSyApvDQafuIxHcAyBc5FVy_vbP8KuRNQJhc
FLUX_API_KEY=01483a08-56ae-494b-bbd1-20daf4cad819
FLUX_API_URL=https://api.bfl.ai/v1/flux-pro-1.1-ultra

# Сохраните (Ctrl+O, Enter, Ctrl+X)

# Перезапустите приложение
docker-compose restart
# или
systemctl restart your-app-name
```

### Шаг 3: Проверьте результат

1. Подождите 30-60 секунд после перезапуска
2. Откройте `/debug` endpoint снова:
   ```
   https://giottobright-back-3800.twc1.net/debug
   ```

3. Должно быть:
   ```json
   {
     "env_vars": {
       "GEMINI_API_KEY": "set",
       "FLUX_API_KEY": "set"
     }
   }
   ```

4. Протестируйте генерацию фото в боте

## Альтернативное решение: Использование Flux вместо Gemini

Если у вас есть только `FLUX_API_KEY`, можно переключиться на использование Flux для генерации. Для этого нужно будет изменить код в `back/app/main.py`.

## Важные замечания

⚠️ **Безопасность**: 
- НЕ коммитьте API ключи в Git
- Используйте переменные окружения платформы
- Регулярно меняйте ключи

📝 **API лимиты**:
- Gemini API может иметь квоты/лимиты
- Проверьте консоль Google Cloud для лимитов: https://console.cloud.google.com/
- Убедитесь, что API активирован в вашем проекте

## Логи для отладки

Если проблема остается, проверьте логи приложения:

```bash
# Логи Docker (если используется)
docker-compose logs -f bot

# Или системные логи
journalctl -u your-app-name -f
```

Ищите строки:
```
❌ Gemini service не инициализирован или нет API ключа
⚠️ GEMINI_API_KEY не установлен
```

## Контакты поддержки
- Документация Gemini API: https://ai.google.dev/
- Документация Flux API: https://docs.bfl.ml/



