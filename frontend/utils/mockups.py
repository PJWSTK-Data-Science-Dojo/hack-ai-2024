import time
from typing import Callable
from pytubefix import YouTube
import io
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile, UploadedFileRec

def process_video(video_buffer: io.BytesIO, progress_function: Callable):
    """
    Simulates processing an uploaded video file.
    
    :param video_file: The video file to "process".
    :return: A mock result that mimics the backend response.
    """
    # Simulate processing time
    for i in range(10):
        time.sleep(2)
        progress_function((i + 1) / 10, f"Processing: {(i + 1) * 10}%")

