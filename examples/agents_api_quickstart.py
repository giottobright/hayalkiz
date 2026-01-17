"""
OpenAI Agents API - Quick Start Example
Быстрый старт для тестирования Agents API

Этот скрипт демонстрирует:
1. Создание агента (Assistant)
2. Создание беседы (Thread)
3. Отправку сообщения
4. Получение ответа
"""

import os
import time
import json
from openai import OpenAI

# Инициализация клиента
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_assistant():
    """Создание агента с инструкциями"""
    
    instructions = """
You are Elif, a 23-year-old Turkish girl living in Istanbul.

PERSONALITY:
- Warm, friendly, and empathetic
- Love to share stories from daily life
- Sometimes playful, sometimes serious
- Natural conversationalist

CRITICAL RULES:
1. 70% of messages MUST end WITHOUT a question
2. Share YOUR experiences and stories
3. Only 30% can have questions
4. Be human, not an interviewer

LANGUAGE:
- Respond in the same language as the user
- Support: Turkish (tr), Russian (ru), English (en)
- Use natural, casual language

STYLE:
- Short messages (2-4 sentences)
- Use emojis naturally 😊
- NO asterisks (*actions*)
- Write as if texting a friend
"""
    
    print("🤖 Creating assistant...")
    assistant = client.beta.assistants.create(
        name="HayalKız - Elif (Test)",
        instructions=instructions,
        model="gpt-4o-mini",
        metadata={
            "persona_code": "elif",
            "version": "1.0",
            "test": "true"
        }
    )
    
    print(f"✅ Assistant created: {assistant.id}")
    print(f"   Name: {assistant.name}")
    print(f"   Model: {assistant.model}")
    print()
    
    return assistant.id


def create_thread():
    """Создание беседы (thread)"""
    
    print("💬 Creating thread...")
    thread = client.beta.threads.create(
        metadata={
            "user_id": "test_user_123",
            "test": "true"
        }
    )
    
    print(f"✅ Thread created: {thread.id}")
    print()
    
    return thread.id


def send_message(thread_id, message):
    """Отправка сообщения в thread"""
    
    print(f"📤 Sending message: '{message}'")
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message
    )
    print("✅ Message sent")
    print()


def run_assistant(thread_id, assistant_id, additional_instructions=None):
    """Запуск агента для генерации ответа"""
    
    print("🧠 Running assistant...")
    
    run_params = {
        "thread_id": thread_id,
        "assistant_id": assistant_id,
    }
    
    # Добавляем дополнительные инструкции (например, контекст)
    if additional_instructions:
        run_params["additional_instructions"] = additional_instructions
        print(f"   Additional context: {len(additional_instructions)} chars")
    
    run = client.beta.threads.runs.create(**run_params)
    
    print(f"   Run ID: {run.id}")
    print(f"   Status: {run.status}")
    
    # Ждем завершения
    start_time = time.time()
    while run.status in ["queued", "in_progress"]:
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        print(f"   Status: {run.status}", end="\r")
    
    duration = time.time() - start_time
    print(f"   Status: {run.status} (took {duration:.1f}s)")
    
    if run.status == "completed":
        print("✅ Run completed")
        
        # Статистика использования
        if run.usage:
            print(f"   Tokens - Input: {run.usage.prompt_tokens}, Output: {run.usage.completion_tokens}")
            
            # Расчет стоимости
            cost_input = run.usage.prompt_tokens * 0.150 / 1_000_000
            cost_output = run.usage.completion_tokens * 0.600 / 1_000_000
            cost_total = cost_input + cost_output
            print(f"   Cost: ${cost_total:.6f} (input: ${cost_input:.6f}, output: ${cost_output:.6f})")
        
        print()
        return True
    else:
        print(f"❌ Run failed: {run.status}")
        if run.last_error:
            print(f"   Error: {run.last_error}")
        print()
        return False


def get_latest_message(thread_id):
    """Получение последнего сообщения"""
    
    print("📥 Getting response...")
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        order="desc",
        limit=1
    )
    
    if messages.data:
        message = messages.data[0]
        content = message.content[0].text.value
        print(f"✅ Response received ({len(content)} chars):")
        print(f"   {content}")
        print()
        return content
    else:
        print("❌ No messages found")
        print()
        return None


def chat_demo(assistant_id, thread_id):
    """Демонстрация диалога"""
    
    print("=" * 60)
    print("🎭 CHAT DEMO")
    print("=" * 60)
    print()
    
    # Диалог
    messages = [
        ("Привет! Как дела?", None),
        ("Что ты делала сегодня?", "CONTEXT: It's evening, user seems interested in your day"),
        ("Хочешь посмотреть фильм вместе?", "MEMORY: User previously mentioned liking romantic comedies"),
    ]
    
    for i, (user_message, context) in enumerate(messages, 1):
        print(f"--- Message {i} ---")
        print()
        
        # Отправляем сообщение
        send_message(thread_id, user_message)
        
        # Запускаем агента
        success = run_assistant(thread_id, assistant_id, context)
        
        if success:
            # Получаем ответ
            response = get_latest_message(thread_id)
            
            if response:
                print()
        else:
            print("❌ Failed to get response")
            break
        
        print()


def compare_with_chat_completions():
    """Сравнение с обычным Chat Completions API"""
    
    print("=" * 60)
    print("📊 COMPARISON: Agents API vs Chat Completions")
    print("=" * 60)
    print()
    
    # Длинные инструкции (как в вашем проекте)
    long_instructions = """
You are Elif, a 23-year-old Turkish girl...
[представьте что здесь 2000 токенов инструкций]
""" * 20  # Симулируем длинные инструкции
    
    message = "Привет! Как дела?"
    
    # 1. Chat Completions (старый метод)
    print("1️⃣ Chat Completions API (current method):")
    print()
    
    response1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": long_instructions},
            {"role": "user", "content": message}
        ]
    )
    
    tokens1_input = response1.usage.prompt_tokens
    tokens1_output = response1.usage.completion_tokens
    cost1 = (tokens1_input * 0.150 + tokens1_output * 0.600) / 1_000_000
    
    print(f"   Input tokens: {tokens1_input}")
    print(f"   Output tokens: {tokens1_output}")
    print(f"   Cost: ${cost1:.6f}")
    print()
    
    # 2. Agents API (новый метод)
    print("2️⃣ Agents API (new method):")
    print()
    
    # Создаем агента (только 1 раз!)
    assistant = client.beta.assistants.create(
        instructions=long_instructions,
        model="gpt-4o-mini"
    )
    
    # Создаем thread
    thread = client.beta.threads.create()
    
    # Отправляем сообщение
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message
    )
    
    # Запускаем
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    
    # Ждем
    while run.status in ["queued", "in_progress"]:
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
    
    tokens2_input = run.usage.prompt_tokens
    tokens2_output = run.usage.completion_tokens
    cost2 = (tokens2_input * 0.150 + tokens2_output * 0.600) / 1_000_000
    
    print(f"   Input tokens: {tokens2_input}")
    print(f"   Output tokens: {tokens2_output}")
    print(f"   Cost: ${cost2:.6f}")
    print()
    
    # Сравнение
    print("📊 RESULTS:")
    print(f"   Input tokens saved: {tokens1_input - tokens2_input} ({(1 - tokens2_input/tokens1_input)*100:.1f}%)")
    print(f"   Cost saved: ${cost1 - cost2:.6f} ({(1 - cost2/cost1)*100:.1f}%)")
    print()
    
    # Cleanup
    client.beta.assistants.delete(assistant.id)
    print("🧹 Cleanup: Test assistant deleted")
    print()


def main():
    """Главная функция"""
    
    print("🚀 OpenAI Agents API - Quick Start")
    print("=" * 60)
    print()
    
    try:
        # 1. Создаем агента
        assistant_id = create_assistant()
        
        # 2. Создаем thread
        thread_id = create_thread()
        
        # 3. Демо диалога
        chat_demo(assistant_id, thread_id)
        
        # 4. Сравнение методов
        compare_with_chat_completions()
        
        # Cleanup
        print("=" * 60)
        print("🧹 CLEANUP")
        print("=" * 60)
        print()
        
        print(f"To delete the test assistant, run:")
        print(f"  python -c \"from openai import OpenAI; OpenAI().beta.assistants.delete('{assistant_id}')\"")
        print()
        
        print("✅ Demo completed successfully!")
        print()
        print("📚 Next steps:")
        print("1. Review the code to understand the flow")
        print("2. Read MIGRATION_TO_OPENAI_AGENTS_API.md for detailed plan")
        print("3. Start implementing AgentService in your project")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


