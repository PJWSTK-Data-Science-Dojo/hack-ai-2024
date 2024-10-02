import time
from typing import Callable
from pytubefix import YouTube
import io
import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile, UploadedFileRec

from utils import api


def process_video(
    user_id: int,
    video_buffer: io.BytesIO,
    progress_function: Callable | None = None,
):
    """
    Simulates processing an uploaded video file.

    :param video_file: The video file to "process".
    :return: A mock result that mimics the backend response.
    """
    process_data = api.start_analysis(user_id, video_buffer)
    if process_data is None:
        st.error("Error starting analysis.")
        return

    st.session_state.process_id = process_data.get("process_id")

    while True:
        stage_data = api.get_analysis_stage(st.session_state.process_id)
        if stage_data is None:
            st.error("Error during getting analysis stage.")
            break

        stage = stage_data["stage"]
        perc = stage_data["perc"]
        message = f"Processing video... ({stage})"
        progress_function(message, perc)

        if stage == "done_video_processing":
            break

        time.sleep(2)
