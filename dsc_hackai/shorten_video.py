import subprocess
from pathlib import Path

def shorten_video(video_path: Path, output_path: Path):
    """
    Remove duplicate frames from the video using mpdecimate.
    
    Args:
        video_path (Path): Path to the original video file.
        output_path (Path): Path to the output video file.
    """
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-threads", "4",
        "-vf", "mpdecimate=hi=12800:lo=1200:frac=0.33,setpts=N/FRAME_RATE/TB",
        "-map", "0:v",
        "-vsync", "vfr",
        "-preset", "ultrafast",
        "-y", str(output_path + ".mp4")
    ]

    subprocess.run(ffmpeg_cmd, check=True)

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", str(output_path + ".mp4"),
        "-threads", "4",
        "-c:v", "libvpx",
        "-c:a", "libvorbis",
        "-preset", "ultrafast",
        "-y", str(output_path + ".webm")
    ]

    subprocess.run(ffmpeg_cmd, check=True)
