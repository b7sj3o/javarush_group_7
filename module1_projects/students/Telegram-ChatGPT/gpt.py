from openai import AsyncOpenAI
import base64

class ChatGptService:
    def __init__(self, token):
        self.client = AsyncOpenAI(api_key=token)
        self.message_list = []

    async def send_message_list(self) -> str:
        print("Надсилаємо запит...")
        completion = await self.client.chat.completions.create(
            model="gpt-5-mini", #"gpt-5-mini",   gpt-4o,  gpt-4-turbo,    gpt-3.5-turbo,  GPT-4o mini
            messages=self.message_list,
            max_completion_tokens=3000,
            temperature=1
        )
        message = completion.choices[0].message
        self.message_list.append(message)
        return message.content

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def analyze_image(self, image_bytes: bytes, mime_type: str) -> str:
        # Конвертуємо байти зображення в base64 рядок
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # Формуємо запит до OpenAI з контентом типу image_url
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "Опиши, що на цьому фото українською мовою."}, {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}
                    }, ],
                }
            ],
            max_tokens=500,
        )

        return response.choices[0].message.content