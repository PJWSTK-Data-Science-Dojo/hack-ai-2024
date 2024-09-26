import time
from jinja2 import Template
import streamlit as st
import enum
import base64
from utils import save_buffer_to_file
from utils.auth import check_auth
from utils.mockups import process_video
from utils.youtube import download_youtube_video


class AppState(enum.Enum):
    UPLOAD = "UPLOAD"
    DOWNLOAD = "DOWNLOAD"
    DOWNLOAD_ERROR = "DOWNLOAD_ERROR"
    PROCESSING = "PROCESSING"
    COMPLETE = "COMPLETE"


if st.session_state.get("app_state") is None:
    st.session_state.app_state = AppState.UPLOAD


def upload_video():
    youtube_url = st.text_input("Enter a YouTube video URL", key="youtube_url")
    uploaded_video = st.file_uploader(
        "Or choose a video...", type=["mp4", "avi", "mov"]
    )

    if uploaded_video:
        st.session_state.app_state = AppState.PROCESSING
        st.session_state.video_file = uploaded_video
        st.session_state.video_title = uploaded_video.name
        print("Uploaded video:", uploaded_video.name)
        save_buffer_to_file(uploaded_video, uploaded_video.name)
        st.rerun()

    elif youtube_url:
        st.session_state.app_state = AppState.DOWNLOAD
        st.rerun()


def download_video():
    progress_bar = st.progress(0)

    def progress_function(stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        progress = bytes_downloaded / total_size
        progress_bar.progress(progress, text=f"Downloading: {int(progress * 100)}%")

    time.sleep(2)
    st.spinner("Downloading video...")
    video_buffer, video_title = download_youtube_video(
        st.session_state.youtube_url, progress_function
    )

    if video_buffer is None:
        st.session_state.youtube_url = ""
        st.session_state.app_state = AppState.DOWNLOAD_ERROR
        st.rerun()
        return

    st.session_state.video_file = video_buffer
    st.session_state.video_title = video_title

    st.session_state.app_state = AppState.PROCESSING
    st.rerun()


def deep_video():
    check_auth()

    st.title("DeepVideo")
    st.header(
        f"Video and Audio Processing - {st.session_state.app_state.value.capitalize()}"
    )
    current_state = st.session_state.app_state.value

    if current_state == AppState.DOWNLOAD_ERROR.value:
        st.error(
            f"Error downloading video. Please check the URL {st.session_state.youtube_url} and try again."
        )
        st.session_state.youtube_url = ""
        st.session_state.app_state = AppState.UPLOAD
        current_state = AppState.UPLOAD.value

    if current_state == AppState.UPLOAD.value:
        upload_video()
        return

    if current_state == AppState.DOWNLOAD.value:
        download_video()
        return

    if current_state == AppState.PROCESSING.value:
        progress_bar = st.progress(0)

        def progress_update(percent, message=None):
            progress_bar.progress(percent, text=message)

        process_video(st.session_state.video_file, progress_update)

        st.session_state.app_state = AppState.COMPLETE
        st.rerun()
        return

    if current_state == AppState.COMPLETE.value:
        st.switch_page("pages/2_🔍_Query.py")


if __name__ == "__main__":
    deep_video()
