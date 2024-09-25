from typing import Callable
from pytubefix import YouTube
import io
from . import save_buffer_to_file

def download_youtube_video(youtube_url, progress_function: Callable):
    """
    Simulates processing a YouTube URL.
    
    :param youtube_url: The YouTube URL to "process".
    :return: A mock result that mimics the backend response.
    """
    try:
        yt = YouTube(youtube_url)
                
        video_stream = yt.streams.first()

        buffer = io.BytesIO()
        
        yt.register_on_progress_callback(progress_function)

        video_stream.stream_to_buffer(buffer)
        video_stream.download()
        buffer.seek(0)
        
        save_buffer_to_file(buffer, f"{yt.video_id}.mp4")
        return buffer
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None
