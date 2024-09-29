import asyncio
import requests
from discord.ext import commands
import discord
import os
from typing import TYPE_CHECKING, List, Optional
from utils import States, Video, download_youtube_video, VideoDownloadState

if TYPE_CHECKING:
    from ..user import UserManager

API_ENDPOINT = os.getenv("endpoint")

# async def download_video(ctx: "commands.Context") -> Tuple[VideoDownloadState, Optional[bytes]]:
#     if not ctx.message.attachments:
#         return -1
#
#     video = ctx.message.attachments[0]  # Assuming the first attachment is the video
#     if video.content_type.startswith("video"):
#         async with aiohttp.ClientSession() as session:
#             async with session.get(video.url) as response:
#                 if response.status == 200:
#                     video_data = await response.read()
#                     await ctx.send(f"Video {video.filename} downloaded successfully!")
#                     return video_data
#                 else:
#                     await ctx.send("Failed to download the video.")
#                     return None
#     else:
#         await ctx.send("The attachment is not a video!")
#         return None

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
        embed.set_footer(text=f"Information requested by: {self.ctx.author.display_name}")
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
        user = ctx.user
        videos: List[Video] = user.videos

        if not videos:
            self.logging.warning(f"[/my_videos] User(ID: {user.id}) doesn't have videos preprocessed")
            await ctx.reply(f'No videos available for {user.id}\n Use the **/summarize** command first.')
            return

        user.state = States.WAITING_FOR_VIDEO_ID
        self.logging.info(f"[/my_videos] Successfully generated embed for user(ID: {user.id})")
        view = VideoPaginationView(videos, ctx)
        embed = view.create_embed()
        view.message = await ctx.send(embed=embed, view=view)

    @commands.command()
    async def show_state(self, ctx: commands.Context): # delete this later, for development purposes only
        await ctx.send(ctx.user.state.name)

    @commands.command()
    async def summary(self, ctx: commands.Context, video_id: int):
        self.logging.info(f"[/summary] User(ID: {ctx.author.id}) with argument {video_id}, type {type(video_id)}")
        user = ctx.user
        video_id = video_id - 1
        if not user.video_exists(video_id):
            self.logging.error(f"[/summary] User(ID: {ctx.author.id}) has no videos.")
            await ctx.reply(f"Wrong video id. Use the **/my_videos** to see which ids are available")
            return

        video = user.videos[video_id]

        title, process_id, bullet_points = video.title, video.process_id, video.bullet_points
        await ctx.send(f"{title}\n{process_id}\n{bullet_points}")
        # here we should send an embed with pretty short description instead of generic ctx.send
        user.state = States.VIEWING_SUMMARY
        user.currently_viewing = video_id
        self.USM.add_llm_user(user.id, process_id)
        await ctx.send(f"You can now successfully query the llm for further questions regarding your video summarization.")

    @commands.command()
    async def stop(self, ctx: commands.Context) -> bool:
        self.logging.info(f"[/stop] User(ID: {ctx.author.id})")

        user = ctx.user
        user.state = States.IDLE
        did_remove = self.USM.delete_llm_user(user.id)
        if not did_remove:
            self.logging.error(f"[/stop] User(ID: {ctx.author.id}) somehow this user wasn't removed or he wasn't there in the first place")
            return

        current_video = user.get_currently_viewing_video()
        current_title = current_video.title if current_video else "You're a cheater."

        self.logging.info(f"[/stop] User(ID: {user.id}) Successfully stopped viewing the summary.")
        await ctx.reply(f"You're no longer viewing the summary of a {current_title}")
        return True

    @commands.command()
    async def summarize(self, ctx: commands.Context, video_link: Optional[str]):
        self.logging.info(f"[/summarize] User(ID: {ctx.author.id}) with argument {video_link}, type {type(video_link)}")
        user = ctx.user

        self.logging.info(f"[/summarize] User(ID: {ctx.author.id}). Downloading of {video_link} started")
        try:
            did_download, info = await asyncio.to_thread(download_youtube_video, video_link, None)
            self.logging.info(f"[/summarize] Download status: {did_download}, Info: {info}")
            if did_download == 1:
                self.logging.warning(f"[/summarize] User(ID: {ctx.author.id}). Tried to download age restricted content")
                await ctx.reply("Prepare yourself. I`m going to tell your mom that you're trying to download 18+ video from youtube")
                return
            if did_download == 2:
                self.logging.warning(f"[/summarize] User(ID: {ctx.author.id}). Error occurred {info}")
                await ctx.reply(f"Something strange happened ||{info}||")
                return

            # else everything went ok
            self.logging.info(f"[/summarize] User(ID: {ctx.author.id}). Video has been downloaded successfully")
            user.state = States.WAITING_FOR_PROCESSED_DATA
            # here send this to the server
            # process_id = yadayada
            await ctx.reply(f"Your video has been downloaded successfully and now it is being processed at the server. Please wait patiently")
            # here we make like data = asyncio.create_task(coro) get the data
            # self.USM.add_video_to_user(user.id, data)
            user.state = States.VIEWING_SUMMARY
            self.USM.add_llm_user(user.id, 1234)
            await ctx.reply(f"You can now freely ask questions regarding your video.")

        except Exception as e:
            self.logging.error(f"[/summarize] User(ID: {ctx.author.id}). Error while downloading video: {str(e)}")
            return

    async def handle_llm_interaction(self, ctx):
        # user = ctx.user
        self.logging.info(f"[LLM Interaction] User(ID: {ctx.author.id}) sent a message: {ctx.message.content}")

        # Perform LLM interaction and respond to user
        llm_response = f"LLM Response to: {ctx.message.content}"
        await ctx.send(llm_response)

    @commands.command()
    async def toggle_llm(self, ctx: commands.Context):
        user = ctx.user
        if user.state != States.VIEWING_SUMMARY:
            user.state = States.VIEWING_SUMMARY
            self.USM.add_llm_user(user.id)
            self.logging.info(f"[/toggle_llm] switched state to viewing summary")
            return
        else:
            user.state = States.IDLE
            self.USM.delete_llm_user(user.id)
            self.logging.info(f"[/toggle+llm] switched state to idle summary")
            return


async def setup(bot, logger, USM):
    await bot.add_cog(API_interaction(bot, logger, USM))
