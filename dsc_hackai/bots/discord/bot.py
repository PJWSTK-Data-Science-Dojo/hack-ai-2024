import asyncio
from discord.ext import commands
import discord
import settings
from cogs import api_interaction

logger = settings.logging.getLogger("bot")
# user_id: object(user)
user_contexts = {}

user_context_lock = asyncio.Lock()


async def process_user_interaction(user_id, user_message, ctx):
    # Be careful!!!!
    # same user can send commands twice, therefore u need to check context, if context is waiting do nothing for that user.

    # Retrieve user context
    async with user_context_lock:
        if user_id not in user_contexts:
            user_contexts[user_id] = []

        user_context = user_contexts[user_id]

    # Simulate an API call with a delay
    await ctx.send(f"before {user_id}")
    await asyncio.sleep(2)
    await ctx.send(f"after {user_id}")


def allowed_channel(ctx):
    if not settings.DISCORD_BOT_CHAT_ID:
        return True
    return ctx.channel.id == settings.DISCORD_BOT_CHAT_ID


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    # intents.members = True

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Bot: {bot.user} (ID: {bot.user.id}) is up")
        await bot.add_cog(api_interaction.API_interaction(bot, logger))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing argument")

    # noinspection PyAsyncCall
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # Ignore bot's own messages
        if not allowed_channel(message):
            return


        user_id = message.author.id
        user_message = message.content
        print(f"{user_id} {user_message} {message.channel}")
        # Process user interaction asynchronously
        # asyncio.create_task(process_user_interaction(user_id, user_message, message.channel))

        # Ensures that commands are still processed
        await bot.process_commands(message)

    bot.run(settings.DISCORD_API_SECRET)


if __name__ == "__main__":
    run()
