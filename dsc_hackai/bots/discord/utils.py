import enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Callable
from pytubefix import YouTube


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
    id: int
    state: States = States.IDLE
    videos: Optional[List[Video]] = field(default_factory=list)
    allowed_to_use: bool = True
    currently_viewing: int = -1

    def get_currently_viewing_video(self) -> Optional[Video]:
        """USe this instead of accessing it via '.' (MUST)"""
        if not self.video_exists(id):
            return None
        return self.videos[self.currently_viewing]

    def is_allowed(self) -> bool:
        return self.state != States.DOESNT_EXISTS and self.allowed_to_use

    def video_exists(self, id: int) -> bool:
        return id in range(len(self.videos))


class VideoDownloadState(enum.Enum):
    DOWNLOADED_SUCCESSFULLY = 0
    NO_VIDEO_ATTACHED = -1
    ATTACHMENT_IS_NOT_VIDEO = -2
    FAILED_TO_DOWNLOAD_VIDEO = -3


def download_youtube_video(youtube_url, progress_function: Callable | None = None):
    """
    Simulates processing a YouTube URL.

    :param youtube_url: The YouTube URL to "process".
    :return: 0,1,2 - 0 = no errors, 1 = age restricted, 2 = something else
    """
    try:
        current_dir = Path(__file__).resolve().parent
        videos_dir = current_dir.parents[1] / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)

        yt = YouTube(youtube_url)

        if yt.age_restricted:
            return 1, f"video: {youtube_url} is age restricted"

        file_name = f"{yt.video_id}.mp4"

        if progress_function:
            yt.register_on_progress_callback(progress_function)
        video_stream = yt.streams.first()

        video_stream.download(output_path=str(videos_dir), filename=file_name)
        return 0, file_name
    except Exception as e:
        return 2, e
