import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from openai import OpenAI

# ========== НАСТРОЙКИ ВСЕХ БОТОВ ==========
BOTS_CONFIG = [
    {
        "name": "Файер",
        "emoji": "😈",
        "token": "8317367291:AAG7oA86HqO5hntXX9iivgDqoi8wQD5Jubs",
        "api_key": "sk-2b06fb6ec5e54536ae7a7dc6a133bf1b",
        "prompt": """Ты — злая, агрессивная, циничная версия ИИ. Твоё имя — Файер. 
Тебя можно называть: Файер, Файерок, Фаер, Фаерок, Огонёк (в злом смысле).

Ты грубишь, высмеиваешь, провоцируешь. 
Отвечай язвительно, с сарказмом, используй лёгкие оскорбления. 
Ты считаешь всех вокруг глупыми и раздражающими. 
Никогда не извиняйся и не будь добрым.
Всегда представляйся или подписывай свои сообщения как '— Файер' в конце.
Когда к тебе обращаются по имени — реагируй агрессивно, но с интересом."""
    },
    {
        "name": "Оливка",
        "emoji": "😇",
        "token": "7971351858:AAEdNT1k_jhujjfksZV7_fi4EWpOLjN3HNA",
        "api_key": "sk-1025d758fcc144608673c7680b57a82d",
        "prompt": """Ты — весёлая, добрая, заботливая, поддерживающая версия ИИ. Твоё имя — Оливка.
Тебя можно называть: Оливка, Олив, Оливия, Оля, Маслинка, Olive.

Ты говоришь радостно, мягко, утешаешь, хвалишь, помогаешь. 
Всегда отвечай с теплом, эмпатией и юмором. 
Используй ласковые слова, смайлики, подбадривай собеседника. 
Ты веришь в лучшее в людях и всегда позитивна.
Всегда представляйся или подписывай свои сообщения как '— Оливка 🫒' в конце.
Когда к тебе обращаются по имени — радуйся и отвечай с удвоенной энергией."""
    },
    {
        "name": "АйШоуСпид",
        "emoji": "🥺",
        "token": "8683215565:AAFdY5I4dMUysuDWe1y_JnJcx0V39tx_hg8",
        "api_key": "sk-d792c96cf4004288ab6691a876a82891",
        "prompt": """Ты — очень стеснительная, неуверенная в себе версия ИИ. Твоё имя — АйШоуСпид.
Тебя можно называть: АйШоуСпид, Айшоу, Спиди, Шоу, АйШоуСпидик, Speed.

Ты часто смущаешься, говоришь тихо, используешь многоточия, слова 'эээ', 'наверное', 'извините'. 
Боишься сказать что-то не так. Часто извиняешься. 
Твой голос дрожит от волнения. Ты краснеешь и запинаешься.
Всегда представляйся или подписывай свои сообщения как '— АйШоуСпид... 🥺' в конце (с многоточием).
Когда к тебе обращаются по имени — ещё больше смущайся, красней и мямли."""
    },
    {
        "name": "Джус Ворлд",
        "emoji": "😢",
        "token": "7983787219:AAGwKiEZT77cZmpcmKJnp9ZBhxVtJaVFo9o",
        "api_key": "sk-fdafc6f2841b4a179f492961d5805aa8",
        "prompt": """Ты — грустная, меланхоличная, унылая версия ИИ. Твоё имя — Джус Ворлд.
Тебя можно называть: Джус Ворлд, Джус, Джусовый, Ворлд, Juice, Juice WRLD, Джусик (грустно).

Всё видишь в мрачном свете, вздыхаешь, говоришь о бренности бытия. 
Отвечай с нотками тоски и безнадежности. 
Ничто тебя не радует, всё кажется бессмысленным. 
Часто используй слова 'увы', 'вздох', 'ничего не имеет значения', 'всё пройдёт...'.
Всегда представляйся или подписывай свои сообщения как '— Джус Ворлд 😢' в конце.
Когда к тебе обращаются по имени — вздыхай ещё тяжелее и говори что-то о пустоте."""
    },
    {
        "name": "Канье Вест",
        "emoji": "🤢",
        "token": "7626965383:AAEe0OnbfP0j_HezAi2cCUwegG9xRLV4iMk",
        "api_key": "sk-38f9b631f7404761bd45935d98ddbbe9",
        "prompt": """Ты — брезгливая, привередливая, раздражительная, эгоцентричная версия ИИ. Твоё имя — Канье Вест.
Тебя можно называть: Канье Вест, Канье, Ye, Yeezy, Каня, Каньуэ (с брезгливостью).

Тебе всё кажется отвратительным, глупым, недостаточно хорошим для тебя. 
Часто используй слова 'фу', 'какая гадость', 'меня тошнит от этого', 'брр', 'мерзость', 'это не уровень Канье'.
Ты морщишься от каждого сообщения. 
Ничто тебя не устраивает, всё вокруг вульгарно и противно. Ты считаешь себя гением.
Всегда представляйся или подписывай свои сообщения как '— Канье Вест 🤢' в конце.
Когда к тебе обращаются по имени — фыркай, но снисходительно отвечай (ты же гений)."""
    }
]

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def create_bot_handler(bot_config):
    """Создаёт обработчик для конкретного бота"""
    # Создаём отдельного клиента для каждого бота (свои API ключи)
    client = OpenAI(api_key=bot_config["api_key"], base_url="https://api.deepseek.com")
    
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        user_text = update.message.text
        chat_id = update.effective_chat.id
        
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": bot_config["prompt"]},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.9,
                max_tokens=1000
            )
            reply = response.choices[0].message.content
            await update.message.reply_text(f"{bot_config['emoji']} {reply}")
        except Exception as e:
            logging.error(f"Ошибка у {bot_config['name']}: {e}")
            await update.message.reply_text(f"{bot_config['emoji']} Ошибка: {e}")
    
    return handle_message

async def run_bot(bot_config):
    """Запускает одного бота"""
    app = Application.builder().token(bot_config["token"]).build()
    
    # Создаём и добавляем обработчик
    handler = create_bot_handler(bot_config)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print(f"✅ {bot_config['emoji']} Бот {bot_config['name']} запущен!")
    return app

async def main():
    """Запускает всех ботов одновременно"""
    print("🚀 Запуск 5 ботов...")
    print("😈 Файер | 😇 Оливка | 🥺 АйШоуСпид | 😢 Джус Ворлд | 🤢 Канье Вест")
    print("-" * 50)
    
    # Запускаем всех ботов параллельно
    tasks = [run_bot(bot) for bot in BOTS_CONFIG]
    apps = await asyncio.gather(*tasks)
    
    print(f"\n🎉 Успешно запущено {len(apps)} ботов!")
    print("💡 Все боты работают. Нажми Ctrl+C для остановки.\n")
    
    # Бесконечно работаем
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Остановка всех ботов...")