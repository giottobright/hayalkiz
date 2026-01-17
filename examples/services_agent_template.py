"""
AgentService - Template для интеграции OpenAI Agents API

Этот файл нужно будет скопировать в back/app/services_agent.py
и доработать под вашу архитектуру.
"""

from typing import Dict, Optional, List
from openai import OpenAI
import logging
import asyncio
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentService:
    """Сервис для работы с OpenAI Agents API"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
        # Кэш Assistant IDs для каждой персоны
        # Формат: {"elif": "asst_abc123", "lara": "asst_def456", ...}
        self.assistants: Dict[str, str] = {}
        
        # Кэш Thread IDs для каждого пользователя
        # Формат: {"user_123": "thread_xyz789", ...}
        self.threads: Dict[str, str] = {}
        
        logger.info("✅ AgentService initialized")
    
    # ========================================================================
    # ASSISTANT MANAGEMENT
    # ========================================================================
    
    async def get_or_create_assistant(
        self,
        persona_code: str,
        instructions: str,
        force_recreate: bool = False
    ) -> str:
        """
        Получить или создать агента для персоны
        
        Args:
            persona_code: Код персоны (elif, lara, mila)
            instructions: Инструкции для агента
            force_recreate: Принудительно пересоздать агента
        
        Returns:
            Assistant ID (например: asst_abc123)
        """
        
        # Проверяем кэш
        if persona_code in self.assistants and not force_recreate:
            logger.debug(f"Using cached assistant for {persona_code}")
            return self.assistants[persona_code]
        
        # Проверяем БД
        assistant_id = self._get_assistant_from_db(persona_code)
        if assistant_id and not force_recreate:
            self.assistants[persona_code] = assistant_id
            logger.info(f"✅ Loaded assistant from DB for {persona_code}: {assistant_id}")
            return assistant_id
        
        # Создаем нового агента
        logger.info(f"🤖 Creating new assistant for {persona_code}...")
        
        try:
            assistant = self.client.beta.assistants.create(
                name=f"HayalKız - {persona_code.capitalize()}",
                instructions=instructions,
                model="gpt-4o-mini",
                metadata={
                    "persona_code": persona_code,
                    "version": "1.0",
                    "created_at": datetime.now().isoformat()
                }
            )
            
            # Сохраняем в кэш и БД
            self.assistants[persona_code] = assistant.id
            self._save_assistant_to_db(persona_code, assistant.id)
            
            logger.info(f"✅ Created assistant for {persona_code}: {assistant.id}")
            return assistant.id
            
        except Exception as e:
            logger.error(f"❌ Failed to create assistant for {persona_code}: {e}")
            raise
    
    async def update_assistant_instructions(
        self,
        persona_code: str,
        new_instructions: str
    ) -> bool:
        """
        Обновить инструкции существующего агента
        
        Args:
            persona_code: Код персоны
            new_instructions: Новые инструкции
        
        Returns:
            True если успешно
        """
        
        assistant_id = await self.get_or_create_assistant(persona_code, new_instructions)
        
        try:
            # Получаем текущую версию
            assistant = self.client.beta.assistants.retrieve(assistant_id)
            old_version = assistant.metadata.get("version", "1.0")
            new_version = self._increment_version(old_version)
            
            # Обновляем
            self.client.beta.assistants.update(
                assistant_id=assistant_id,
                instructions=new_instructions,
                metadata={
                    **assistant.metadata,
                    "version": new_version,
                    "updated_at": datetime.now().isoformat(),
                    "previous_version": old_version
                }
            )
            
            logger.info(f"✅ Updated assistant {assistant_id}: {old_version} → {new_version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update assistant {assistant_id}: {e}")
            return False
    
    # ========================================================================
    # THREAD MANAGEMENT
    # ========================================================================
    
    async def get_or_create_thread(
        self,
        user_id: str,
        persona_code: Optional[str] = None
    ) -> str:
        """
        Получить или создать thread для пользователя
        
        Args:
            user_id: ID пользователя
            persona_code: Код персоны (для метаданных)
        
        Returns:
            Thread ID (например: thread_xyz789)
        """
        
        # Проверяем кэш
        if user_id in self.threads:
            logger.debug(f"Using cached thread for user {user_id}")
            return self.threads[user_id]
        
        # Проверяем БД
        thread_id = self._get_thread_from_db(user_id)
        if thread_id:
            self.threads[user_id] = thread_id
            logger.info(f"✅ Loaded thread from DB for user {user_id}: {thread_id}")
            return thread_id
        
        # Создаем новый thread
        logger.info(f"💬 Creating new thread for user {user_id}...")
        
        try:
            metadata = {
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
            if persona_code:
                metadata["persona_code"] = persona_code
            
            thread = self.client.beta.threads.create(metadata=metadata)
            
            # Сохраняем в кэш и БД
            self.threads[user_id] = thread.id
            self._save_thread_to_db(user_id, thread.id, persona_code)
            
            logger.info(f"✅ Created thread for user {user_id}: {thread.id}")
            return thread.id
            
        except Exception as e:
            logger.error(f"❌ Failed to create thread for user {user_id}: {e}")
            raise
    
    async def archive_thread(self, user_id: str) -> bool:
        """
        Архивировать старый thread (при смене персоны)
        
        Args:
            user_id: ID пользователя
        
        Returns:
            True если успешно
        """
        
        if user_id in self.threads:
            old_thread_id = self.threads[user_id]
            
            # Удаляем из кэша
            del self.threads[user_id]
            
            # Архивируем в БД
            self._archive_thread_in_db(user_id, old_thread_id)
            
            logger.info(f"📦 Archived thread for user {user_id}: {old_thread_id}")
            return True
        
        return False
    
    # ========================================================================
    # MESSAGE GENERATION
    # ========================================================================
    
    async def generate_reply(
        self,
        user_id: str,
        persona_code: str,
        message: str,
        additional_context: Optional[Dict] = None,
        response_format: Optional[Dict] = None
    ) -> str:
        """
        Генерация ответа через Agents API
        
        Args:
            user_id: ID пользователя
            persona_code: Код персоны (elif, lara, mila)
            message: Сообщение пользователя
            additional_context: Дополнительный контекст (memory, day_story, etc)
            response_format: Формат ответа (например: {"type": "json_object"})
        
        Returns:
            Ответ агента (текст или JSON строка)
        """
        
        try:
            # 1. Получаем агента и thread
            assistant_id = await self.get_or_create_assistant(
                persona_code,
                self._get_instructions(persona_code)
            )
            thread_id = await self.get_or_create_thread(user_id, persona_code)
            
            # 2. Формируем дополнительные инструкции
            additional_instructions = self._build_additional_instructions(additional_context)
            
            # 3. Добавляем сообщение в thread
            logger.info(f"📤 Adding message to thread {thread_id}")
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )
            
            # 4. Запускаем Run
            logger.info(f"🧠 Running assistant {assistant_id}...")
            
            run_params = {
                "thread_id": thread_id,
                "assistant_id": assistant_id,
                "temperature": 0.85,  # Ваш текущий параметр
            }
            
            if additional_instructions:
                run_params["additional_instructions"] = additional_instructions
                logger.debug(f"   Additional instructions: {len(additional_instructions)} chars")
            
            if response_format:
                run_params["response_format"] = response_format
                logger.debug(f"   Response format: {response_format}")
            
            run = self.client.beta.threads.runs.create(**run_params)
            
            # 5. Ждем завершения
            run = await self._wait_for_run_completion(thread_id, run.id)
            
            # 6. Проверяем статус
            if run.status != "completed":
                raise Exception(f"Run failed with status: {run.status}")
            
            # 7. Логируем использование токенов
            if run.usage:
                logger.info(f"💰 Tokens - Input: {run.usage.prompt_tokens}, Output: {run.usage.completion_tokens}")
                
                # TODO: Интегрировать с вашим cost_tracker
                self._log_cost(
                    user_id=user_id,
                    persona_code=persona_code,
                    tokens_input=run.usage.prompt_tokens,
                    tokens_output=run.usage.completion_tokens
                )
            
            # 8. Получаем ответ
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order="desc",
                limit=1
            )
            
            if not messages.data:
                raise Exception("No messages found in thread")
            
            reply = messages.data[0].content[0].text.value
            
            logger.info(f"✅ Generated reply: {len(reply)} chars")
            return reply
            
        except Exception as e:
            logger.error(f"❌ Failed to generate reply: {e}")
            raise
    
    async def generate_reply_with_functions(
        self,
        user_id: str,
        persona_code: str,
        message: str,
        available_functions: Dict,
        additional_context: Optional[Dict] = None
    ) -> tuple[str, List[Dict]]:
        """
        Генерация ответа с поддержкой function calling
        
        Args:
            user_id: ID пользователя
            persona_code: Код персоны
            message: Сообщение пользователя
            available_functions: Словарь доступных функций
            additional_context: Дополнительный контекст
        
        Returns:
            Tuple[ответ, список вызванных функций]
        """
        
        # TODO: Реализовать function calling
        # См. примеры в MIGRATION_TO_OPENAI_AGENTS_API.md
        raise NotImplementedError("Function calling not implemented yet")
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _build_additional_instructions(self, context: Optional[Dict]) -> str:
        """
        Построение динамических инструкций из контекста
        
        Args:
            context: Контекст (memory, day_story, current_activity, time, etc)
        
        Returns:
            Строка с дополнительными инструкциями
        """
        
        if not context:
            return ""
        
        parts = []
        
        # Memory context
        if context.get("memory_context"):
            parts.append(f"🧠 MEMORY:\n{context['memory_context']}")
        
        # Day story
        if context.get("day_story"):
            parts.append(f"📅 TODAY:\n{context['day_story']}")
        
        # Current activity
        if context.get("current_activity"):
            parts.append(f"⏰ NOW:\n{context['current_activity']}")
        
        # Time of day
        if context.get("time_context"):
            parts.append(f"🕐 TIME:\n{context['time_context']}")
        
        # Flow instructions (onboarding, topic control)
        if context.get("flow_instructions"):
            parts.append(f"📋 FLOW RULES:\n{context['flow_instructions']}")
        
        # Voice mode
        if context.get("is_voice_response"):
            parts.append("""
🎤 VOICE MODE:
- Speak naturally, conversationally
- Short sentences (easier to speak)
- No emojis (voice only)
""")
        
        return "\n\n".join(parts) if parts else ""
    
    async def _wait_for_run_completion(
        self,
        thread_id: str,
        run_id: str,
        max_wait_time: int = 30,
        poll_interval: float = 0.5
    ):
        """
        Ждать завершения Run
        
        Args:
            thread_id: ID thread
            run_id: ID run
            max_wait_time: Максимальное время ожидания (сек)
            poll_interval: Интервал проверки (сек)
        
        Returns:
            Run объект
        """
        
        start_time = asyncio.get_event_loop().time()
        
        while True:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            if run.status not in ["queued", "in_progress"]:
                return run
            
            # Проверяем таймаут
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > max_wait_time:
                logger.error(f"⏰ Run timeout after {max_wait_time}s")
                # Пытаемся отменить
                self.client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
                raise TimeoutError(f"Run did not complete in {max_wait_time}s")
            
            await asyncio.sleep(poll_interval)
    
    def _get_instructions(self, persona_code: str) -> str:
        """
        Получить инструкции для персоны
        
        TODO: Интегрировать с вашей системой загрузки промптов
        (db_postgres.get_persona_prompt, enriched_personas, etc)
        """
        
        # Заглушка - нужно заменить на реальную загрузку
        return f"You are {persona_code}..."
    
    def _log_cost(self, user_id: str, persona_code: str, tokens_input: int, tokens_output: int):
        """
        Логировать стоимость запроса
        
        TODO: Интегрировать с вашим cost_tracker
        """
        
        cost_input = tokens_input * 0.150 / 1_000_000
        cost_output = tokens_output * 0.600 / 1_000_000
        cost_total = cost_input + cost_output
        
        logger.info(f"💵 Cost: ${cost_total:.6f} (in: ${cost_input:.6f}, out: ${cost_output:.6f})")
        
        # TODO: Сохранить в БД через log_api_usage()
    
    @staticmethod
    def _increment_version(version: str) -> str:
        """Increment semantic version (e.g. 1.0 -> 1.1)"""
        try:
            major, minor = map(int, version.split('.'))
            return f"{major}.{minor + 1}"
        except:
            return "1.0"
    
    # ========================================================================
    # DATABASE INTEGRATION (TODO)
    # ========================================================================
    
    def _get_assistant_from_db(self, persona_code: str) -> Optional[str]:
        """
        Получить Assistant ID из БД
        
        TODO: Реализовать запрос к таблице assistant_mappings
        
        SQL:
            SELECT assistant_id FROM assistant_mappings
            WHERE persona_code = ?
        """
        # Заглушка
        return None
    
    def _save_assistant_to_db(self, persona_code: str, assistant_id: str):
        """
        Сохранить Assistant ID в БД
        
        TODO: Реализовать INSERT в таблицу assistant_mappings
        
        SQL:
            INSERT INTO assistant_mappings (persona_code, assistant_id, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (persona_code) DO UPDATE SET
                assistant_id = EXCLUDED.assistant_id,
                updated_at = CURRENT_TIMESTAMP
        """
        pass
    
    def _get_thread_from_db(self, user_id: str) -> Optional[str]:
        """
        Получить Thread ID из БД
        
        TODO: Реализовать запрос к таблице user_threads
        
        SQL:
            SELECT thread_id FROM user_threads
            WHERE user_id = ?
        """
        return None
    
    def _save_thread_to_db(self, user_id: str, thread_id: str, persona_code: Optional[str]):
        """
        Сохранить Thread ID в БД
        
        TODO: Реализовать INSERT в таблицу user_threads
        
        SQL:
            INSERT INTO user_threads (user_id, thread_id, created_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id) DO UPDATE SET
                thread_id = EXCLUDED.thread_id,
                last_used = CURRENT_TIMESTAMP
        """
        pass
    
    def _archive_thread_in_db(self, user_id: str, thread_id: str):
        """
        Архивировать Thread в БД
        
        TODO: Реализовать UPDATE в таблице user_threads
        
        SQL:
            UPDATE user_threads
            SET archived_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND thread_id = ?
        """
        pass


# ========================================================================
# USAGE EXAMPLE
# ========================================================================

async def example_usage():
    """Пример использования AgentService"""
    
    # Инициализация
    service = AgentService(api_key="your-openai-api-key")
    
    # Генерация ответа
    reply = await service.generate_reply(
        user_id="user_123",
        persona_code="elif",
        message="Привет! Как дела?",
        additional_context={
            "memory_context": "User likes coffee in the morning",
            "day_story": "It's raining today, stayed home",
            "current_activity": "Evening, reading a book",
            "time_context": "19:30, evening",
        }
    )
    
    print(f"Reply: {reply}")


if __name__ == "__main__":
    # Тест
    import asyncio
    asyncio.run(example_usage())


