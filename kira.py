import logging
from g4f.client import Client
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class KiraAssistant(loader.Module):
    """ИИ-ассистент Кира. Отвечает на вопросы, начинающиеся с 'Кира'."""

    strings = {"name": "Kira"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "model",
                "gpt-4o",
                lambda: "Модель ChatGPT",
            ),
            loader.ConfigValue(
                "role",
                "user",
                lambda: "Роль в переписке",
            ),
        )

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    async def watcher(self, message):
        if not message.text:
            return

        if not message.text.lower().startswith("кира "):
            return

        # Только пользователь может использовать
        if message.sender_id != (await self._client.get_me()).id:
            return

        question = message.text[5:].strip()
        if not question:
            return

        client = Client()
        try:
            response = client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": self.config["role"], "content": question}],
                stream=False,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Ошибка: {e}"

        await message.edit(answer)
        
