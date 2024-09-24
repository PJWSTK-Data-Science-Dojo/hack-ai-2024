from telegram import Update
from telegram.ext import (Application,
                          CommandHandler,
                          MessageHandler,
                          filters,
                          ContextTypes,
                          Defaults,
                          ApplicationHandlerStop,
                          TypeHandler,
                          )
import asyncio
from dotenv import load_dotenv
import os
import logging
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

user_context_lock = asyncio.Lock()
user_contexts = {}
ALLOWED_IDS = [...]


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'error {context.error} from {update}')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('help')


async def whitelist_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in ALLOWED_IDS or update.message.chat.type != 'private':
        await update.effective_message.reply_text('Be patient. This AI bot is not available for everyone')
        raise ApplicationHandlerStop


async def start(update: Update, context):
    user_id = update.message.from_user.id
    user_contexts[user_id] = []  # Initialize context for new users
    await update.message.reply_text("Hello! You can start chatting with the bot now.")


async def process_user_interaction(user_id, user_message, update: Update):
    # Retrieve user context
    async with user_context_lock:
        if user_id not in user_contexts:
            user_contexts[user_id] = []

        user_context = user_contexts[user_id]

    # Simulate an LLM API call with a delay
    # response = await api_call(user_context, user_message)

    # Update the user's conversation context with the latest interaction
    # user_context.append({'user': user_message, 'bot': response})

    # Save the updated context
    # user_contexts[user_id] = user_context

    # api usage simulation
    await update.message.reply_text(f"before {user_id}")
    await asyncio.sleep(10)
    await update.message.reply_text(f"after {user_id}")


# noinspection PyAsyncCall
async def handle_message(update: Update, context):
    user_id = update.message.from_user.id
    user_message = update.message.text
    print(f"{type(user_id)=}")
    # non-blocking asyncio task. Do not use await
    asyncio.create_task(process_user_interaction(user_id, user_message, update))


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # filter_users = TypeHandler(Update, whitelist_user)
    # app.add_handler(filter_users, -1)

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler('help', help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error_handler)

    app.run_polling()
