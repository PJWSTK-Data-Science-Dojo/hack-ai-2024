import json
from typing import Callable
from pytubefix import YouTube
import io
from . import save_buffer_to_file

import enum
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Callable

# from pytubefix import YouTube
from yt_dlp import YoutubeDL


def download_youtube_video(
    user_id: int, youtube_url: str, progress_function: Callable | None = None
):
    """
    Simulates processing a YouTube URL.

    :param youtube_url: The YouTube URL to "process".
    :return: 0,1,2 - 0 = no errors, 1 = age restricted, 2 = something else
    """
    try:
        videos_dir = Path.cwd() / "videos"
        videos_dir.mkdir(parents=True, exist_ok=True)

        downloaded_filename = None

        def progress_hook(d):
            nonlocal downloaded_filename
            if d["status"] == "finished":
                downloaded_filename = d["filename"]

            total = d["total_bytes"]
            downl = d.get("downloaded_bytes", total / 2)

            perc = downl / total

            if progress_function:
                progress_function(perc, f"Downloading video... {perc:.2%}")

        args = {
            # 'quiet': True,
            "noplaylist": True,
            "outtmpl": str(
                videos_dir / f"{user_id}_%(id)s.%(ext)s"
            ),  # Save with video ID as the filename
            "format": "best",  # Download the best available quality
            "progress_hooks": [progress_hook],  # Attach our custom progress hook,
        }

        with YoutubeDL(args) as ydl:
            ydl.download(youtube_url)
            if downloaded_filename:

                return open(file=downloaded_filename), downloaded_filename

        return None, None
    except Exception as e:
        print(f"Error downloading video: {e}")
        raise e
