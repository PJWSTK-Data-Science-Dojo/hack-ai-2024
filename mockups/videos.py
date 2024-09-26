import io
from pathlib import Path


def get_user_videos():
    """
    Get a list of video files uploaded by the user.

    :return: A list of video files.
    """
    videos = Path("videos")
    if not videos.exists():
        return []

    return list(video_path.stem for video_path in videos.glob("*.mp4"))


def get_video_by_id(video_id) -> io.BytesIO:
    """
    Get a video file by its ID.

    :param video_id: The ID of the video file.
    :return: The video file.
    """
    video_path = Path(f"videos/{video_id}.mp4")
    if not video_path.exists():
        return None

    with open(video_path, "rb") as f:
        return f.read()
