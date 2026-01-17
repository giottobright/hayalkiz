-- ============================================================================
-- Migration: Add support for OpenAI Agents API
-- Date: 2024-11-17
-- Description: Добавляет таблицы для хранения Assistant и Thread IDs
-- ============================================================================

-- Таблица для хранения Assistant IDs (агентов) для каждой персоны
CREATE TABLE IF NOT EXISTS assistant_mappings (
    persona_code TEXT PRIMARY KEY,          -- Код персоны (elif, lara, mila)
    assistant_id TEXT NOT NULL,             -- ID агента в OpenAI (asst_xxx)
    model TEXT DEFAULT 'gpt-4o-mini',       -- Модель агента
    version TEXT DEFAULT '1.0',             -- Версия промпта
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,                    -- Когда последний раз использовался
    is_active BOOLEAN DEFAULT TRUE,         -- Активен ли агент
    metadata JSONB                          -- Дополнительные метаданные
);

-- Индексы для assistant_mappings
CREATE INDEX IF NOT EXISTS idx_assistant_mappings_assistant_id 
    ON assistant_mappings(assistant_id);
CREATE INDEX IF NOT EXISTS idx_assistant_mappings_active 
    ON assistant_mappings(is_active) WHERE is_active = TRUE;

-- Таблица для хранения Thread IDs (бесед) для каждого пользователя
CREATE TABLE IF NOT EXISTS user_threads (
    user_id TEXT NOT NULL,                  -- ID пользователя в Telegram
    thread_id TEXT NOT NULL,                -- ID беседы в OpenAI (thread_xxx)
    persona_code TEXT,                      -- Текущая персона в этом thread
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived_at TIMESTAMP,                  -- Когда заархивирован (NULL = активный)
    message_count INTEGER DEFAULT 0,        -- Количество сообщений в thread
    is_active BOOLEAN DEFAULT TRUE,         -- Активен ли thread
    metadata JSONB,                         -- Дополнительные метаданные
    
    PRIMARY KEY (user_id, thread_id)
);

-- Индексы для user_threads
CREATE INDEX IF NOT EXISTS idx_user_threads_user_id 
    ON user_threads(user_id) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_user_threads_thread_id 
    ON user_threads(thread_id);
CREATE INDEX IF NOT EXISTS idx_user_threads_persona 
    ON user_threads(persona_code);
CREATE INDEX IF NOT EXISTS idx_user_threads_active 
    ON user_threads(is_active) WHERE is_active = TRUE;

-- Таблица для хранения истории архивированных threads
-- (опционально, для аналитики)
CREATE TABLE IF NOT EXISTS archived_threads (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    persona_code TEXT,
    started_at TIMESTAMP,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    reason TEXT,                            -- Причина архивации (persona_switch, reset, etc)
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_archived_threads_user_id 
    ON archived_threads(user_id);
CREATE INDEX IF NOT EXISTS idx_archived_threads_archived_at 
    ON archived_threads(archived_at);

-- Представление для получения активных threads пользователей
CREATE OR REPLACE VIEW active_user_threads AS
SELECT 
    ut.user_id,
    ut.thread_id,
    ut.persona_code,
    ut.created_at,
    ut.last_used,
    ut.message_count,
    am.assistant_id,
    am.model,
    am.version
FROM user_threads ut
LEFT JOIN assistant_mappings am ON ut.persona_code = am.persona_code
WHERE ut.is_active = TRUE 
  AND ut.archived_at IS NULL
  AND am.is_active = TRUE;

-- Функция для обновления last_used при использовании thread
CREATE OR REPLACE FUNCTION update_thread_last_used()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_threads
    SET last_used = CURRENT_TIMESTAMP,
        message_count = message_count + 1
    WHERE user_id = NEW.user_id 
      AND thread_id = NEW.thread_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Триггер для автоматического обновления last_used
-- (можно привязать к таблице messages, если нужно)
-- CREATE TRIGGER trigger_update_thread_last_used
-- AFTER INSERT ON messages
-- FOR EACH ROW
-- EXECUTE FUNCTION update_thread_last_used();

-- Функция для архивации thread
CREATE OR REPLACE FUNCTION archive_thread(
    p_user_id TEXT,
    p_thread_id TEXT,
    p_reason TEXT DEFAULT 'manual'
) RETURNS BOOLEAN AS $$
BEGIN
    -- Копируем в archived_threads
    INSERT INTO archived_threads (
        user_id, 
        thread_id, 
        persona_code, 
        started_at, 
        message_count, 
        reason
    )
    SELECT 
        user_id,
        thread_id,
        persona_code,
        created_at,
        message_count,
        p_reason
    FROM user_threads
    WHERE user_id = p_user_id 
      AND thread_id = p_thread_id
      AND is_active = TRUE;
    
    -- Помечаем как архивный
    UPDATE user_threads
    SET is_active = FALSE,
        archived_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id 
      AND thread_id = p_thread_id;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения активного thread пользователя
CREATE OR REPLACE FUNCTION get_active_thread(p_user_id TEXT)
RETURNS TABLE (
    thread_id TEXT,
    persona_code TEXT,
    assistant_id TEXT,
    created_at TIMESTAMP,
    message_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ut.thread_id,
        ut.persona_code,
        am.assistant_id,
        ut.created_at,
        ut.message_count
    FROM user_threads ut
    LEFT JOIN assistant_mappings am ON ut.persona_code = am.persona_code
    WHERE ut.user_id = p_user_id
      AND ut.is_active = TRUE
      AND ut.archived_at IS NULL
    ORDER BY ut.last_used DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Функция для получения Assistant ID по коду персоны
CREATE OR REPLACE FUNCTION get_assistant_id(p_persona_code TEXT)
RETURNS TEXT AS $$
DECLARE
    v_assistant_id TEXT;
BEGIN
    SELECT assistant_id INTO v_assistant_id
    FROM assistant_mappings
    WHERE persona_code = p_persona_code
      AND is_active = TRUE;
    
    RETURN v_assistant_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Если у вас уже есть персоны, можно добавить placeholder записи
-- (реальные assistant_id будут созданы скриптом миграции)

-- INSERT INTO assistant_mappings (persona_code, assistant_id, version) VALUES
-- ('elif', 'asst_placeholder_elif', '1.0'),
-- ('lara', 'asst_placeholder_lara', '1.0'),
-- ('mila', 'asst_placeholder_mila', '1.0')
-- ON CONFLICT (persona_code) DO NOTHING;

-- ============================================================================
-- ANALYTICS QUERIES
-- ============================================================================

-- Статистика по использованию агентов
CREATE OR REPLACE VIEW assistant_usage_stats AS
SELECT 
    am.persona_code,
    am.assistant_id,
    am.version,
    COUNT(DISTINCT ut.user_id) as unique_users,
    SUM(ut.message_count) as total_messages,
    MAX(ut.last_used) as last_used,
    am.created_at as assistant_created_at
FROM assistant_mappings am
LEFT JOIN user_threads ut ON am.persona_code = ut.persona_code
WHERE am.is_active = TRUE
GROUP BY am.persona_code, am.assistant_id, am.version, am.created_at
ORDER BY total_messages DESC;

-- Статистика по архивным threads
CREATE OR REPLACE VIEW archived_threads_stats AS
SELECT 
    DATE(archived_at) as archive_date,
    persona_code,
    reason,
    COUNT(*) as threads_count,
    AVG(message_count) as avg_messages_per_thread,
    SUM(message_count) as total_messages
FROM archived_threads
GROUP BY DATE(archived_at), persona_code, reason
ORDER BY archive_date DESC;

-- ============================================================================
-- CLEANUP & MAINTENANCE
-- ============================================================================

-- Функция для очистки старых архивных threads (>90 дней)
CREATE OR REPLACE FUNCTION cleanup_old_archived_threads(days_old INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM archived_threads
    WHERE archived_at < CURRENT_TIMESTAMP - (days_old || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Запланированная задача для очистки (требует pg_cron extension)
-- SELECT cron.schedule('cleanup-archived-threads', '0 3 * * 0', 'SELECT cleanup_old_archived_threads(90)');

-- ============================================================================
-- ROLLBACK SCRIPT (на случай отката)
-- ============================================================================

-- Чтобы откатить миграцию:
/*
DROP VIEW IF EXISTS assistant_usage_stats;
DROP VIEW IF EXISTS archived_threads_stats;
DROP VIEW IF EXISTS active_user_threads;

DROP FUNCTION IF EXISTS cleanup_old_archived_threads(INTEGER);
DROP FUNCTION IF EXISTS get_assistant_id(TEXT);
DROP FUNCTION IF EXISTS get_active_thread(TEXT);
DROP FUNCTION IF EXISTS archive_thread(TEXT, TEXT, TEXT);
DROP FUNCTION IF EXISTS update_thread_last_used();

DROP TABLE IF EXISTS archived_threads;
DROP TABLE IF EXISTS user_threads;
DROP TABLE IF EXISTS assistant_mappings;
*/

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Проверить что таблицы созданы
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_name IN ('assistant_mappings', 'user_threads', 'archived_threads')
  AND table_schema = 'public';

-- Проверить индексы
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('assistant_mappings', 'user_threads', 'archived_threads')
ORDER BY tablename, indexname;

-- Проверить функции
SELECT 
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_name IN (
    'update_thread_last_used',
    'archive_thread',
    'get_active_thread',
    'get_assistant_id',
    'cleanup_old_archived_threads'
)
ORDER BY routine_name;

-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

-- Пример 1: Добавить нового агента
-- INSERT INTO assistant_mappings (persona_code, assistant_id, version)
-- VALUES ('elif', 'asst_abc123xyz', '1.0')
-- ON CONFLICT (persona_code) DO UPDATE 
-- SET assistant_id = EXCLUDED.assistant_id,
--     updated_at = CURRENT_TIMESTAMP;

-- Пример 2: Создать thread для пользователя
-- INSERT INTO user_threads (user_id, thread_id, persona_code)
-- VALUES ('123456789', 'thread_xyz789abc', 'elif')
-- ON CONFLICT (user_id, thread_id) DO UPDATE
-- SET last_used = CURRENT_TIMESTAMP;

-- Пример 3: Получить активный thread пользователя
-- SELECT * FROM get_active_thread('123456789');

-- Пример 4: Архивировать thread
-- SELECT archive_thread('123456789', 'thread_xyz789abc', 'persona_switch');

-- Пример 5: Статистика использования
-- SELECT * FROM assistant_usage_stats;

-- Пример 6: Очистить старые архивы
-- SELECT cleanup_old_archived_threads(90);


