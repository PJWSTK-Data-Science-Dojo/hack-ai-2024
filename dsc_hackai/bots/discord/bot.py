from discord.ext import commands
import discord
import settings
from cogs import api_interaction
from user import UserManager
from typing import TYPE_CHECKING
from utils import States

if TYPE_CHECKING:
    from user import User

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


class CustomContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = None


def allowed_channel(ctx):
    if not settings.DISCORD_BOT_CHAT_ID:
        return True
    return ctx.channel.id == settings.DISCORD_BOT_CHAT_ID


async def validate_user_basic_perms(ctx: commands.Context):
    if not ctx.user.is_allowed():
        logger.error(f"[validate_user_basic_perms] User(ID: {ctx.user.id}) doesn't have rights to use the service")
        return False

    if ctx.command.name == "stop":
        if ctx.user.state != States.VIEWING_SUMMARY:
            logger.warning(
                f"[validate_user_basic_perms] User(ID: {ctx.user.id}) is not viewing a summary, cannot stop.")
            await ctx.reply("You're not viewing a summary, nothing to stop.")
            return False
        return True

    if ctx.user.state == States.VIEWING_SUMMARY:
        logger.warning(
            f"[validate_user_basic_perms] User(ID: {ctx.user.id}) is currently viewing the summary and cannot access other service unless /stop is used")
        await ctx.reply(
            "Please use the **/stop** command to stop viewing the summary. Otherwise, you won't be able to use other commands")
        return False
    return True  # meaning can use the command otherwise no.


def run():
    intents = discord.Intents.default()
    intents.message_content = True

    USM = UserManager(logger, settings.user_schema, settings.video_scheme)
    bot = commands.Bot(command_prefix="/", intents=intents)

    async def get_custom_context(message, *, cls=CustomContext):
        return await super(commands.Bot, bot).get_context(message, cls=cls)

    bot.get_context = get_custom_context

    @bot.event
    async def on_ready():
        logger.info(f"Bot: {bot.user} (ID: {bot.user.id}) is up")
        await bot.add_cog(api_interaction.API_interaction(bot, logger, USM))

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            logger.error(f"[on_command_error] User(ID: {ctx.user.id}) when typing a command missed an argument")
            await ctx.send("Missing argument")
            return
        logger.error(f"[on_command_error] User(ID: {ctx.user.id}): {error}")

    # noinspection PyAsyncCall
    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user:
            return  # Ignore bot's own messages
        if not allowed_channel(message):
            return

        ctx = await bot.get_context(message, cls=CustomContext)
        # asyncio.create_task(process_user_interaction(user_id, user_message, message.channel))

        if ctx.valid:  # means it is a command
            user = USM.get_user(message.author.id)
            ctx.user = user
            if not await validate_user_basic_perms(ctx):
                return False # all logging is done in the function higher

            await bot.invoke(ctx)
            return

        if USM.is_using_llm(message.author.id):
            api_cog = bot.get_cog('API_interaction')
            await api_cog.handle_llm_interaction(ctx)
            return

    @bot.command()
    async def kys(ctx):
        exit()

    bot.run(settings.DISCORD_API_SECRET)


if __name__ == "__main__":
    run()
