import asyncio
from pathlib import Path

import requests
from discord.ext import commands
import discord
import os
from typing import TYPE_CHECKING, List, Optional, Tuple, Union
from utils import States, Video, download_youtube_video, VideoDownloadState

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

    @commands.command(brief="Shows a list of preprocessed videos", description="Shows a list of preprocessed videos")
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
    async def show_state(self, ctx: commands.Context):  # delete this later, for development purposes only
        await ctx.send(ctx.user.state.name)

    @commands.command(brief="View summary of an already preprocessed video.", description="You can view summary of an already preprocessed video, after that you can directly talk to an llm")
    async def summary(self, ctx: commands.Context, video_id: int):
        self.logging.info(f"[/summary] User(ID: {ctx.author.id}) with argument {video_id}, type {type(video_id)}")
        user = ctx.user
        video_id = video_id - 1
        if not user.video_exists(video_id):
            self.logging.error(f"[/summary] User(ID: {ctx.author.id}) has no videos.")
            await ctx.reply(f"Wrong video id. Use the **/my_videos** to see which ids are available")
            return

        video = user.videos[video_id]

        title, process_id, stage, bullet_points = video.title, video.process_id,video.stage, video.bullet_points

        stage_date = f"Video is currently at the stage of {stage}.\n" if stage else ""
        bullet_points_concat = "\n".join(bullet_point for bullet_point in bullet_points)
        description = stage_date + bullet_points_concat
        embed = discord.Embed(title=title, description=description, color=0x109319)
        embed.set_author(name="Deep Video", url="https://github.com/PJWSTK-Data-Science-Dojo/hack-ai-2024",
                         icon_url=ctx.bot.user.avatar)
        embed.set_footer(text=f"Information requested by: {ctx.author.display_name}")

        await ctx.send(embed=embed)
        # here we should send an embed with pretty short description instead of generic ctx.send
        user.state = States.VIEWING_SUMMARY
        user.currently_viewing = video_id
        self.USM.add_llm_user(user.id, process_id)
        await ctx.send(
            f"You can now successfully query the llm for further questions regarding your video summarization.")

    @commands.command(brief="Stop interacting with the summary of the video.", description="You always need to use /stop command if you want to stop viewing summary of the video.")
    async def stop(self, ctx: commands.Context) -> bool:
        self.logging.info(f"[/stop] User(ID: {ctx.author.id})")

        user = ctx.user
        user.state = States.IDLE
        did_remove = self.USM.delete_llm_user(user.id)
        if not did_remove:
            self.logging.error(
                f"[/stop] User(ID: {ctx.author.id}) somehow this user wasn't removed or he wasn't there in the first place")
            return

        current_video = user.get_currently_viewing_video()
        current_title = current_video.title if current_video else "You're a cheater."

        self.logging.info(f"[/stop] User(ID: {user.id}) Successfully stopped viewing the summary.")
        await ctx.reply(f"You're no longer viewing the summary of a {current_title}")
        return True

    async def process_attachment(self, ctx: commands.Context, video_link: Union[str, None]) -> Tuple[bool, Union[str, VideoDownloadState]]:
        """
            Processes an attachment or YouTube video link, downloading the video if possible.

            :param ctx: The context from the command.
            :param video_link: A YouTube link provided by the user (if any).
            :return: Tuple indicating success/failure and the video filename or error state.
            """

        def log_and_respond(log_level: str, log_message: str, response_message: str, state: VideoDownloadState) -> \
                Tuple[bool, VideoDownloadState]:
            getattr(self.logging, log_level)(log_message)
            asyncio.create_task(ctx.reply(response_message))
            return False, state

        # Check for an attached video file
        video_attachments = [
            attachment for attachment in ctx.message.attachments
            if attachment.content_type and attachment.content_type.startswith("video")
        ]

        # Handle the different cases:
        # 1. User provided both a link and an attachment
        if video_link and video_attachments:
            return log_and_respond(
                "warning",
                f"[process_attachment] User(ID: {ctx.author.id}) provided both YouTube link and video attachment.",
                "Please provide either a YouTube link or an attached video file, not both.",
                VideoDownloadState.VIDEO_YT_LINK_TOGETHER
            )
        # 2. User provided only a YouTube link
        elif video_link:
            self.logging.info(
                f"[process_attachment] User(ID: {ctx.author.id}). Yt link was provided proceeding with download")
            did_download, info = await asyncio.to_thread(download_youtube_video, ctx.author.id, video_link, None)

            if did_download == 1:
                return log_and_respond(
                    "warning",
                    f"[process_attachment] User(ID: {ctx.author.id}) tried to download age-restricted content.",
                    "Prepare yourself. I’m going to tell your mom that you're trying to download 18+ video from YouTube.",
                    VideoDownloadState.FAILED_TO_DOWNLOAD_VIDEO
                )
            if did_download == 2:
                return log_and_respond(
                    "warning",
                    f"[process_attachment] User(ID: {ctx.author.id}) encountered an error during download: {info}.",
                    f"Something strange happened ||{info}||",
                    VideoDownloadState.FAILED_TO_DOWNLOAD_VIDEO
                )

            # in that case it will be a file name
            return True, info
        # 3. User provided multiple video attachments
        elif len(video_attachments) > 1:
            return log_and_respond(
                "warning",
                f"[process_attachment] User(ID: {ctx.author.id}) provided multiple video attachments.",
                "Please provide only one video file at a time.",
                VideoDownloadState.MULTIPLE_ATTACHMENTS
            )
        # 4. User provided only one video file attachment
        elif len(video_attachments) == 1:
            video_attachment = video_attachments[0]
            file_extension = Path(video_attachment.filename).suffix

            current_dir = Path(__file__).resolve().parent
            videos_dir = current_dir.parents[2] / "videos"
            videos_dir.mkdir(parents=True, exist_ok=True)

            file_path = self.create_video_file_path(ctx, file_extension)

            try:
                # Asynchronously save the video file
                await video_attachment.save(file_path)
                self.logging.info(
                    f"[process_attachment] User(ID: {ctx.author.id}) video saved successfully: {file_path.name}")
                return True, file_path.name
            except Exception as e:
                self.logging.error(f"[process_attachment] Failed to save video for User(ID: {ctx.author.id}): {e}")
                return False, VideoDownloadState.FAILED_TO_DOWNLOAD_VIDEO
        # 5. Neither a link nor an attachment provided

        return log_and_respond(
            "error",
            f"[process_attachment] User(ID: {ctx.author.id}) used command without providing any video link or attachment.",
            "Please provide a YouTube link or attach a video file.",
            VideoDownloadState.NO_VIDEO_ATTACHED
        )

    def create_video_file_path(self, ctx: commands.Context, file_extension: str) -> Path:
        """
        Creates and returns a valid file path for saving the video.

        :param ctx: The context from the command, used for user-specific folder names.
        :param file_extension: The extension of the video file to be saved.
        :return: A Path object representing the file path where the video will be saved.
        """
        current_dir = Path(__file__).resolve().parent
        videos_dir = current_dir.parents[2] / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)

        # Use a unique filename with the user's ID and the length of their video collection
        file_name = f"{ctx.author.id}_{len(ctx.user.videos)}{file_extension}"
        return videos_dir / file_name

    @commands.command(brief="Summarize a video of your choice", description="Send a video attachment or yt-link to summarize. (Only one type of media can be sent at once)")
    async def summarize(self, ctx: commands.Context, video_link: Optional[str]):
        self.logging.info(f"[/summarize] User(ID: {ctx.author.id}) with argument {video_link}, type {type(video_link)}")
        user = ctx.user

        try:
            did_download, info = await self.process_attachment(ctx, video_link)

            if not did_download:
                self.logging.error(f"[/summarize] User(ID: {ctx.author.id} failed to process user attachment. Reason: {info}")
                return

            # else everything went ok
            self.logging.info(f"[/summarize] User(ID: {ctx.author.id}). Video has been downloaded successfully {info}")
            user.state = States.WAITING_FOR_PROCESSED_DATA
            # here send this to the server
            # process_id = yadayada
            await ctx.reply(
                f"Your video has been downloaded successfully and now is being processed at the server. Please wait patiently")
            # here we make like data = asyncio.create_task(coro) get the data
            # self.USM.add_video_to_user(user.id, data)
            user.state = States.VIEWING_SUMMARY
            # self.USM.add_llm_user(user.id, process_id)
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
