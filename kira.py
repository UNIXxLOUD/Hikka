import logging
from g4f.client import Client
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class Kira(loader.Module):
    """ИИ-девушка Кира. Реагирует только на сообщения от владельца, начинающиеся с 'Кира ' и отвечает прямо в это сообщение."""

    strings = {"name": "Kira"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "model", "gpt-4o", lambda: "Модель ChatGPT"
            ),
            loader.ConfigValue(
                "role", "user", lambda: "Кто ты для ChatGPT?"
            ),
        )

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    async def watcher(self, message):
        # Только реагировать на сообщения пользователя
        if message.sender_id != (await self._client.get_me()).id:
            return

        if not message.text or not message.text.lower().startswith("кира "):
            return

        query = message.text[5:].strip()
        if not query:
            return await message.edit("Не могу ответить: запрос пустой.")

        try:
            client = Client()
            response = client.chat.completions.create(
                model=self.config["model"],
                messages=[{"role": self.config["role"], "content": query}],
                stream=False,
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Кира: ошибка — {e}"

        await message.edit(answer)
        
