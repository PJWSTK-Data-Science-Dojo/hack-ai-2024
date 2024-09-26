import asyncio
import requests
from discord.ext import commands
import discord
import os
from typing import TYPE_CHECKING, List
from classes_toolkit import States, Video

if TYPE_CHECKING:
    from ..user import UserManager
API_ENDPOINT = os.getenv("endpoint")


class VideoPaginationView(discord.ui.View):
    def __init__(self, videos: List['Video'], ctx: commands.Context):
        super().__init__(timeout=60)
        self.videos = videos
        self.ctx = ctx
        self.current_page = 0
        self.max_pages = (len(videos) - 1) // 5
        self.message = None  # Will hold the message object for editing
        self.embed = None

    def populate_embed(self):
        """Helper function to populate the embed with paginated video data."""
        start_index = self.current_page * 5
        end_index = start_index + 5
        paginated_videos = self.videos[start_index:end_index]

        # Clear any old fields and populate the embed with the new page of videos
        self.embed.clear_fields()
        for index, video in enumerate(paginated_videos, start=start_index + 1):
            self.embed.add_field(
                name=f"**{index}. {video.title}**",
                value=f"This is the value for video {index}.",  # CHANGE
                inline=False
            )

    async def update_embed(self):
        # Create a new embed
        # embed = discord.Embed(description="Say **/summary {video_id}**\n__Example:__ **/summary 1**", color=0x109319)
        # embed.set_author(name="Deep Video", url="https://github.com/PJWSTK-Data-Science-Dojo/hack-ai-2024",
        #                  icon_url=self.ctx.bot.user.avatar)

        # Populate the embed with the current page of videos
        self.populate_embed()

        # Update button states (disable if on first or last page)
        self.children[0].disabled = self.current_page == 0  # Disable "Previous" on the first page
        self.children[1].disabled = self.current_page == self.max_pages  # Disable "Next" on the last page

        # Edit the original message with the updated embed
        await self.message.edit(embed=self.embed, view=self)

    @discord.ui.button(label="⮜", style=discord.ButtonStyle.primary, custom_id="prev")
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_embed()
        await interaction.response.defer()

    @discord.ui.button(label="⮞", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_pages:
            self.current_page += 1
            await self.update_embed()
        await interaction.response.defer()

    def create_embed(self):
        embed = discord.Embed(description="Say **/summary {video_id}**\n__Example:__ **/summary 1**", color=0x109319)
        embed.set_author(name="Deep Video", url="https://github.com/PJWSTK-Data-Science-Dojo/hack-ai-2024",
                         icon_url=self.ctx.bot.user.avatar)
        embed.set_footer(text="Information requested by: {}".format(self.ctx.author.display_name))
        self.embed = embed
        self.populate_embed()
        return self.embed


def make_api_call(data):
    response = requests.post(API_ENDPOINT, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return f"API call failed with status {response.status_code}"


class API_interaction(commands.Cog):
    def __init__(self, bot, logger: 'Logger', USM):
        self.bot = bot
        self.logging = logger
        self.USM: UserManager = USM

    @commands.command()
    async def my_videos(self, ctx: commands.Context):
        user_id = ctx.message.author.id
        user = self.USM.get_user(user_id)

        if user.state == States.DOESNT_EXISTS:
            self.logging.warning(f"[/my_videos] User(ID: {user_id}) doesn't have rights to use the service")
            await ctx.reply(f"You don't have access to the service.\n(requested by {user_id}")
            return

        videos: List[Video] = user.videos

        if not videos:
            self.logging.warning(f"[/my_videos] User(ID: {user_id}) doesn't have videos preprocessed")
            await ctx.reply(f'No videos available for {user_id}\n Use /summarize command first.')
            return

        user.state = States.WAITING_FOR_VIDEO_ID
        self.logging.info(f"[/my_videos] Successfully generated embed for user(ID: {user_id})")
        view = VideoPaginationView(videos, ctx)
        embed = view.create_embed()
        view.message = await ctx.send(embed=embed, view=view)

    @commands.command()
    async def show_state(self, ctx: commands.Context):
        user = self.USM.get_user(ctx.message.author.id)
        await ctx.send(user.state.name)

    @commands.command()
    async def summary(self, ctx: commands.Context, id: int):
        self.logging.info(f"[/summary] {ctx.author.id} with argument {id}, type {type(id)}")
        user = self.USM.get_user(user_id=ctx.author.id)



async def setup(bot, logger, USM):
    await bot.add_cog(API_interaction(bot, logger, USM))
