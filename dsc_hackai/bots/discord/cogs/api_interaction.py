import asyncio
import requests
from discord.ext import commands
import os

API_ENDPOINT = os.getenv("endpoint")


def make_api_call(data):
    response = requests.post(API_ENDPOINT, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return f"API call failed with status {response.status_code}"


class API_interaction(commands.Cog):
    def __init__(self, bot, logger):
        self.bot = bot
        self.logging = logger

    @commands.command()
    async def my_videos(self, ctx):
        if not API_ENDPOINT:
            self.logging.info("Endpoint is null, you should check the env file. \n For now we will proceed with an "
                              "example data")
        else:
            print("not none")


async def setup(bot, logger):
    await bot.add_cog(API_interaction(bot, logger))
