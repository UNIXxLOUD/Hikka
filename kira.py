import asyncio
import logging

from g4f.client import Client

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class Kira(loader.Module):
    """ИИ девушка для общения и советов."""

    strings = {
        "name": "Kira",

        "no_args": "<emoji document_id=5854929766146118183>❌</emoji> <b>Нужно </b><code>{}{} {}</code>",

        "asking_chatgpt": """<emoji document_id=5334675996714999970>🔄</emoji> <b>Спрашиваю Киру...</b>

<i><emoji document_id=5370869711888194012>👾</emoji> Вы можете задавать вопросы, и я буду отвечать как Кира.</i>""",
        
        "answer_text": """<emoji document_id=5818813162815753343>👨‍💻</emoji> <b>Вопрос:</b> {question}

<emoji document_id=5372981976804366741>🤖</emoji> <b>Ответ:</b> {answer}

<emoji document_id=5424753383741346604>🖥</emoji> <b>Модель</b>: <code>{model}</code>""",
    }

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
                lambda: "Кто ты для ChatGPT?",
            ),
        )

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    @loader.command()
    async def kira(self, message):
        """Задать вопрос Кире."""
        # Ограничим доступ только для пользователя
        if message.from_id != 123456789:  # Замените на свой ID
            return await utils.answer(message, "<emoji document_id=5854929766146118183>❌</emoji> <b>Только для владельца.</b>")

        q = utils.get_args_raw(message)
        if not q:
            return await utils.answer(message, self.strings["no_args"].format(self.get_prefix(), "kira", "[вопрос]"))

        await utils.answer(message, self.strings['asking_chatgpt'].format(prefix=self.get_prefix()))

        client = Client()
        response = client.chat.completions.create(
            model=self.config['model'],
            messages=[{"role": self.config['role'], "content": q}],
            stream=False,
        )

        return await utils.answer(message, self.strings['answer_text'].format(question=q, answer=response.choices[0].message.content.strip(), model=self.config['model']))
