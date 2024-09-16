from subprocess import Popen, PIPE, run
import time
import tempfile
import requests
import pathlib
import ollama
from gradio_client import Client, handle_file


def describe_chunk_w_llava_next(video_file_path):
    """
    Using LLAVA One V
    https://llava-onevision.lmms-lab.com/?
    """
    client = requests.Session()
    client.headers.update({"Content-Type": "application/json"})
    url = "https://llava-onevision.lmms-lab.com/add_text_1"

    video_file_path = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4"
    files = {"video": handle_file(video_file_path)}
    data = {
        "messages": {"text": "Describe video", "files": []},
        "image_process_mode": "Default",
    }

    response = client.post(url, data=data, files=files)
    result = response.json()
    return result


def split_video_chunks(video_file_path, tmpdir):
    """
    Split video into 10-second chunks and save them in tmpdir.
    """
    input_video = video_file_path
    output_format = "mp4"
    chunk_duration = 10.0  # in seconds

    # Construct the ffmpeg command for segmenting the video
    segment_name_template = "video_%04d"  # Template for output filenames
    ffmpeg_cmd = (
        f"ffmpeg -i {input_video} -c copy -map 0 -f segment "
        f"-segment_time {chunk_duration} -reset_timestamps 1 "
        f"{tmpdir}/{segment_name_template}.{output_format}"
    )

    # Execute the ffmpeg command
    run(ffmpeg_cmd, shell=True)


def describe_each_frame_ollama(frame_file_path):
    res = ollama.chat(
        model="llava",
        messages=[
            {
                "role": "user",
                "content": "Describe this image:",
                "images": [frame_file_path],
            }
        ],
    )
    print(res["message"]["content"])


def split_frames(video_file_path, tmpdir: tempfile.TemporaryDirectory):
    # Use FFmpeg to cut the source video into frames and save them to the temporary directory
    ffmpeg_cmd = [
        "ffmpeg",
        "-i",
        video_file_path,
        "-vf",
        "fps=1",
        str(pathlib.Path(tmpdir.name)) + "/frame_%04d.jpg",
    ]

    run(ffmpeg_cmd, check=True)
    return True


def process_vision(video_file_path):
    tmpdir_vids = pathlib.Path("test_vid")
    tmpdir_vids.mkdir(exist_ok=True)
    # tmpdir_vids = tempfile.TemporaryDirectory(dir="test_vid")
    # Whole Video split to chunks
    split_video_chunks(video_file_path, tmpdir_vids)
    # Get a list of all frames in the temporary director

    video_chunks_frames = [str(f) for f in pathlib.Path(tmpdir_vids).glob("*.mp4")]

    # Send requests with each frame to the phi3-llava model using ollama
    print(tmpdir_vids.name)
    for video_chunk_file in video_chunks_frames:
        print(video_chunk_file)
        print(describe_chunk_w_llava_next(video_chunk_file))

    tmpdir_vids.cleanup()

    # Create a temporary directory to store the video frames
    tmpdir = tempfile.TemporaryDirectory()
    # Frames
    split_frames(video_file_path, tmpdir)

    # Get a list of all frames in the temporary directory
    frame_files = [str(f) for f in pathlib.Path(tmpdir.name).glob("*.jpg")]

    # Send requests with each frame to the phi3-llava model using ollama
    for frame_file in frame_files:
        describe_each_frame_ollama(frame_file)

    tmpdir.cleanup()
