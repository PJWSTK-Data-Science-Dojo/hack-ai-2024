import enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Callable
# from pytubefix import YouTube
from yt_dlp import YoutubeDL


class States(enum.Enum):
    WAITING_FOR_VIDEO_ID = 1
    WAITING_FOR_PROCESSED_DATA = 2
    VIEWING_SUMMARY = 3
    IDLE = 4
    DOESNT_EXISTS = 5


@dataclass
class Video:
    title: str
    process_id: str
    stage: str
    bullet_points: List[str] = field(default_factory=list)


@dataclass
class User:
    user_id: int
    id: int # db id
    state: States = States.IDLE
    videos: Optional[List[Video]] = field(default_factory=list)
    allowed_to_use: bool = True
    currently_viewing: int = -1

    def get_currently_viewing_video(self) -> Optional[Video]:
        """USe this instead of accessing it via '.' (MUST)"""
        if not self.video_exists(self.user_id):
            return None
        return self.videos[self.currently_viewing]

    def is_allowed(self) -> bool:
        return self.state != States.DOESNT_EXISTS and self.allowed_to_use

    def video_exists(self, id: int) -> bool:
        return id in range(len(self.videos))


class VideoDownloadState(enum.Enum):
    NO_VIDEO_ATTACHED = -1
    MULTIPLE_ATTACHMENTS = -2
    FAILED_TO_DOWNLOAD_VIDEO = -3
    VIDEO_YT_LINK_TOGETHER = -4


def download_youtube_video(user_id: int, youtube_url, progress_function: Callable | None = None):
    """
    Simulates processing a YouTube URL.

    :param youtube_url: The YouTube URL to "process".
    :return: 0,1,2 - 0 = no errors, 1 = age restricted, 2 = something else
    """
    try:
        current_dir = Path(__file__).resolve().parent
        videos_dir = current_dir.parents[1] / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)

        downloaded_filename = None

        def progress_hook(d):
            nonlocal downloaded_filename
            if d['status'] == 'finished':
                downloaded_filename = d['filename']
            if progress_function:  # Only call the user-provided progress function if it's not None
                progress_function(d)

        args = {
            # 'quiet': True,
            'noplaylist': True,
            'outtmpl': str(videos_dir / f'{user_id}_%(id)s.%(ext)s'),  # Save with video ID as the filename
            'format': 'best',  # Download the best available quality
            'progress_hooks': [progress_hook],  # Attach our custom progress hook,
        }

        with YoutubeDL(args) as ydl:
            ydl.download(youtube_url)
            if downloaded_filename:
                return 0, downloaded_filename

            return 2, "Unable to determine the downloaded file name."

    except Exception as e:
        return 2, e

if __name__ == '__main__':
    help(YoutubeDL)
