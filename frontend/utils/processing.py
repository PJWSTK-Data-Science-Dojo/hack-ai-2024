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

    st.session_state.process_id = process_data["process_id"]

    while True:
        stage_data = api.get_analysis_stage(st.session_state.process_id)
        if stage_data is None:
            st.error("Error during getting analysis stage.")
            break

        video_stage: str = stage_data["video_stage"]
        perc: str = stage_data["perc"]

        if video_stage == "done":
            progress_function("Processing complete.", perc)
            break

        for stage in stage_data["analysis_stages"]:
            analysis = stage["analysis"]
            stage = stage["stage"]
            if stage == "done":
                continue

            progress_function(f"Processing {analysis} analysis... ({stage})", perc)

        time.sleep(2)
