import subprocess
from pathlib import Path

def shorten_audio(video_path: Path, output_path: Path):
    """
    Remove silence from an audio file using ffmpeg.
    
    Args:
        video_path (Path): Path to the input video file.
        output_path (Path): Path to the output audio file.
    """

    audio_temp_path = video_path.with_suffix('.wav')

    extract_audio_cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-q:a", "0",
        "-map", "a",
        "-y", str(audio_temp_path)
    ]

    subprocess.run(extract_audio_cmd, check=True)

    silence_threshold = "-60dB"
    min_silence_duration = 0.5

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", str(audio_temp_path),
        "-threads", "4",
        "-af", f"silenceremove=start_duration={min_silence_duration}:start_threshold={silence_threshold}",
        "-preset", "ultrafast",
        "-y", str(output_path + ".mp3")
    ]
    subprocess.run(ffmpeg_cmd, check=True)
