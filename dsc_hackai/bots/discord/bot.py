from discord.ext import commands
import discord
import settings
from cogs import api_interaction
from user import UserManager

logger = settings.logging.getLogger("bot")


# async def process_user_interaction(user_id, user_message, ctx):
#     # Be careful!!!! same user can send commands twice, therefore u need to check context, if context is waiting do
#     # nothing for that user.
#
#     # Retrieve user context
#     async with user_context_lock:
#         if user_id not in user_contexts:
#             user_contexts[user_id] = []
#
#         user_context = user_contexts[user_id]
#
#     # Simulate an API call with a delay
#     await ctx.send(f"before {user_id}")
#     await asyncio.sleep(2)
#     await ctx.send(f"after {user_id}")


def allowed_channel(ctx):
    if not settings.DISCORD_BOT_CHAT_ID:
        return True
    return ctx.channel.id == settings.DISCORD_BOT_CHAT_ID


def run():
    intents = discord.Intents.default()
    intents.message_content = True
    # intents.members = True
    USM = UserManager(logger, settings.user_schema, settings.video_scheme)

    bot = commands.Bot(command_prefix="/", intents=intents)

    @bot.event
    async def on_ready():
        logger.info(f"Bot: {bot.user} (ID: {bot.user.id}) is up")
        await bot.add_cog(api_interaction.API_interaction(bot, logger, USM))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            logger.error(f"User(ID: {ctx.user.id}) when typing a command missed an argument")
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

        await bot.process_commands(message)

    # @bot.command()
    # async def embed(ctx):
    #     my_embed = CustomEmbed()
    #     my_embed.populate_info(ctx)
    #     await ctx.send(embed=my_embed)
    #
    #     # Useful ctx variables
    #     # User's display name in the server
    #     # ctx.author.display_name
    #     # User's avatar URL
    #     # ctx.author.avatar_url

    bot.run(settings.DISCORD_API_SECRET)


if __name__ == "__main__":
    run()
