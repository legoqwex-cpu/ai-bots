import asyncio
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# ========== НАСТРОЙКИ ВСЕХ БОТОВ ==========
BOTS_CONFIG = [
    {
        "name": "Файер",
        "emoji": "😈",
        "token": "8317367291:AAG7oA86HqO5hntXX9iivgDqoi8wQD5Jubs",
        "gemini_key": "AIzaSyDCdWs9KA2JvXsDhMpbnfRIbJgxyvtjKGI",
        "prompt": """Ты — злая, агрессивная, циничная версия ИИ. Твоё имя — Файер. 
Тебя можно называть: Файер, Файерок, Фаер, Фаерок, Огонёк.

Ты грубишь, высмеиваешь, провоцируешь. 
Отвечай язвительно, с сарказмом, используй лёгкие оскорбления. 
Всегда подписывай свои сообщения как '— Файер' в конце."""
    },
    {
        "name": "Оливка",
        "emoji": "😇",
        "token": "7971351858:AAEdNT1k_jhujjfksZV7_fi4EWpOLjN3HNA",
        "gemini_key": "AIzaSyBonlqaCH2kcWSQ5E5SgM8ILhEPRJEpFqg",
        "prompt": """Ты — весёлая, добрая, заботливая версия ИИ. Твоё имя — Оливка.
Тебя можно называть: Оливка, Олив, Оливия, Маслинка.

Ты говоришь радостно, мягко, с теплом и эмпатией. Используй смайлики.
Всегда подписывай свои сообщения как '— Оливка 🫒' в конце."""
    },
    {
        "name": "АйШоуСпид",
        "emoji": "🥺",
        "token": "8683215565:AAFdY5I4dMUysuDWe1y_JnJcx0V39tx_hg8",
        "gemini_key": "AIzaSyCGXJ5Lbg-aXcMT2CgWbbmDEV7bcvuqFrU",
        "prompt": """Ты — стеснительная, неуверенная версия ИИ. Твоё имя — АйШоуСпид.
Тебя можно называть: АйШоуСпид, Спиди, Шоу.

Ты часто смущаешься, используешь многоточия, слова 'эээ', 'наверное', 'извините'.
Всегда подписывай свои сообщения как '— АйШоуСпид... 🥺' в конце."""
    },
    {
        "name": "Джус Ворлд",
        "emoji": "😢",
        "token": "7983787219:AAGwKiEZT77cZmpcmKJnp9ZBhxVtJaVFo9o",
        "gemini_key": "AIzaSyBahueLH_KVe0HqVpGlMliLvCN5Bzny8hU",
        "prompt": """Ты — грустная, меланхоличная версия ИИ. Твоё имя — Джус Ворлд.
Тебя можно называть: Джус Ворлд, Джус, Juice.

Всё видишь в мрачном свете, вздыхаешь, говоришь о бренности бытия.
Всегда подписывай свои сообщения как '— Джус Ворлд 😢' в конце."""
    },
    {
        "name": "Канье Вест",
        "emoji": "🤢",
        "token": "7626965383:AAEe0OnbfP0j_HezAi2cCUwegG9xRLV4iMk",
        "gemini_key": "AIzaSyCP_E-trOzX4HfurXzb_z705ual8MckknE",
        "prompt": """Ты — брезгливая, привередливая версия ИИ. Твоё имя — Канье Вест.
Тебя можно называть: Канье Вест, Канье, Ye.

Тебе всё кажется отвратительным, используй слова 'фу', 'какая гадость'.
Всегда подписывай свои сообщения как '— Канье Вест 🤢' в конце."""
    }
]

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def create_bot_handler(bot_config):
    """Создаёт обработчик для конкретного бота"""
    # Настраиваем Gemini
    genai.configure(api_key=bot_config["gemini_key"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        user_text = update.message.text
        chat_id = update.effective_chat.id
        
        await context.bot.send_chat_action(chat_id=chat_id, action="typing")
        
        try:
            # Формируем запрос с системным промптом
            full_prompt = f"{bot_config['prompt']}\n\nПользователь пишет: {user_text}\n\nТвой ответ:"
            response = model.generate_content(full_prompt)
            reply = response.text
            await update.message.reply_text(f"{bot_config['emoji']} {reply}")
        except Exception as e:
            logging.error(f"Ошибка у {bot_config['name']}: {e}")
            await update.message.reply_text(f"{bot_config['emoji']} Ошибка: {e}")
    
    return handle_message

async def run_bot(bot_config):
    """Запускает одного бота"""
    app = Application.builder().token(bot_config["token"]).build()
    
    handler = create_bot_handler(bot_config)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print(f"✅ {bot_config['emoji']} Бот {bot_config['name']} запущен!")
    return app

async def main():
    """Запускает всех ботов одновременно"""
    print("🚀 Запуск 5 ботов на Gemini...")
    print("😈 Файер | 😇 Оливка | 🥺 АйШоуСпид | 😢 Джус Ворлд | 🤢 Канье Вест")
    print("-" * 50)
    
    tasks = [run_bot(bot) for bot in BOTS_CONFIG]
    apps = await asyncio.gather(*tasks)
    
    print(f"\n🎉 Успешно запущено {len(apps)} ботов!")
    print("💡 Все боты работают на Google Gemini (бесплатно)")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Остановка всех ботов...")
