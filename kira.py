from .. import loader, utils
import requests

@loader.tds
class KiraAssistant(loader.Module):
    """A simple assistant module that responds to commands using Hugging Face Transformers."""
    
    strings = {
        "name": "KiraAssistant",
        "running": "<emoji document_id=5870718740236079262>🌟</emoji> <b>Обработка запроса...</b>",
        "error": "<emoji document_id=🚫</emoji> <b>Произошла ошибка:</b> <code>{error}</code>",
        "voice_recorded": "<emoji document_id=📥</emoji> <b>Голосовое сообщение записано!</b>",
        "response": "<emoji document_id=💬</emoji> <b>Ответ:</b> <code>{response}</code>",
    }

    strings_ru = {
        "running": "<emoji document_id=5870718740236079262>🌟</emoji> <b>Обработка запроса...</b>",
        "error": "<emoji document_id=🚫</emoji> <b>Произошла ошибка:</b> <code>{error}</code>",
        "voice_recorded": "<emoji document_id=📥</emoji> <b>Голосовое сообщение записано!</b>",
        "response": "<emoji document_id=💬</emoji> <b>Ответ:</b> <code>{response}</code>",
    }

    async def client_ready(self, client, db):
        self.client = client

    async def kiracmd(self, message):
        """Используйте 'Кира <ваш запрос>' для получения ответа."""
        await utils.answer(message, self.strings("running"))

        query = message.text.split(' ', 1)
        if len(query) > 1:
            user_query = query[1]
            try:
                response = await self.get_ai_response(user_query)
                await utils.answer(message, self.strings("response").format(response=response))
            except Exception as e:
                await utils.answer(message, self.strings("error").format(error=str(e)))
        else:
            await utils.answer(message, self.strings("error").format(error="Необходим запрос после 'Кира'."))

    async def kirasaycmd(self, message):
        """Используйте 'Кира скажи <ваше сообщение>' для записи голосового сообщения."""
        await utils.answer(message, self.strings("running"))

        user_message = message.text.split(' ', 2)[-1]  
        await utils.answer(message, self.strings("voice_recorded"))

    async def get_ai_response(self, query):
        headers = {
            "Authorization": "Bearer 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"
        }
        
        payload = {
            "inputs": query,
        }

        response = requests.post('https://api-inference.huggingface.co/models/gpt2', headers=headers, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result[0]['generated_text']
        else:
            raise Exception("Ошибка API: " + response.text)
            
