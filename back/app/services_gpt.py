from typing import List, Dict
from openai import OpenAI
from .config import get_settings
from .personas import Persona


class GPTService:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"

    def generate_reply(self, persona: Persona, messages: List[Dict[str, str]]) -> str:
        system_content = (
            f"[TR]\n{persona.system_tr}\n\n"
            f"[RU]\n{persona.system_ru}\n\n"
            "Talimat / Инструкция: Tüm yanıtlarını önce Türkçe, sonra aynı mesajda Rusça kopyasıyla yaz."
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_content},
                *messages,
            ],
            temperature=0.8,
        )
        return response.choices[0].message.content or ""
