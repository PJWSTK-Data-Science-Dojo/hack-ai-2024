from subprocess import Popen, PIPE, run
import time
import tempfile
import requests
import pathlib
import subprocess
# import ollama
from api.llava_next import llava_next_endpoint


def split_video_to_chunks(video_file_path, tmpdir):
    """
    Split video into 10-second chunks, with exactly 32 frames per chunk, and save them in tmpdir.
    """
    input_video = video_file_path
    output_format = "mp4"
    chunk_duration = 10.0  # in seconds
    target_frame_count = 32  # frames per chunk

    # Get the video frame rate using ffprobe
    probe_cmd = (
        f"ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate "
        f"-of default=noprint_wrappers=1:nokey=1 {input_video}"
    )
    result = subprocess.run(probe_cmd, shell=True, capture_output=True, text=True)
    frame_rate_str = result.stdout.strip()

    # Calculate the target frame rate for each chunk (to distribute 32 frames evenly)
    frame_rate = eval(
        frame_rate_str
    )  # Calculate the actual frame rate from the ratio (e.g., "30000/1001")
    target_fps = (
        target_frame_count / chunk_duration
    )  # Target frame rate to get 32 frames in 10 seconds

    # Construct the ffmpeg command for segmenting the video
    segment_name_template = "video_%04d"  # Template for output filenames
    ffmpeg_cmd = (
        f"ffmpeg -i {input_video} -vf fps={target_fps} -c:v libx264 -crf 23 -preset fast "
        f"-f segment -segment_time {chunk_duration} -reset_timestamps 1 "
        f"{tmpdir}/{segment_name_template}.{output_format}"
    )

    # Execute the ffmpeg command
    subprocess.run(ffmpeg_cmd, shell=True)


VIDEO_QUESTIONS = [
    "what is in video chunk",
    "what objects can you see",
    # "how object are moving",
    # "how camera is moving",
    # "what emotions are shown",
    # "were there multiple changes in view",
]


def process_vision(video_file_path):

    tmpdir_vids = pathlib.Path("test_vid")
    tmpdir_vids.mkdir(exist_ok=True)

    # Whole Video split to chunks
    split_video_to_chunks(video_file_path, tmpdir_vids)

    # Get a list of all frames in the temporary directory
    video_chunks = [str(f) for f in pathlib.Path(tmpdir_vids).glob("*.mp4")]

    results = []
    # Process each video chunk
    llava_next = llava_next_endpoint()
    for video_chunk_file in video_chunks:
        print(f"Processing, {video_chunk_file}")
        results.append(llava_next.inference(video_chunk_file, VIDEO_QUESTIONS))

    tmpdir_vids.cleanup()
    return results
