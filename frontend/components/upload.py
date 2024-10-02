import streamlit as st

from utils import AppState, remove_ansi_codes, save_buffer_to_file
from utils.mockups import process_video
from utils.youtube import download_youtube_video


def upload_input(disabled=False):
    youtube_url = st.text_input(
        "Enter a YouTube video URL", key="youtube_url", disabled=disabled
    )

    uploaded_video = st.file_uploader(
        "Or choose a video...", type=["mp4", "avi", "mov"], disabled=disabled
    )

    if uploaded_video:
        if st.session_state.app_state.value != AppState.UPLOAD.value:
            return

        st.session_state.app_state = AppState.PROCESSING
        st.session_state.video_file = uploaded_video
        st.session_state.video_title = uploaded_video.name
        print("Uploaded video:", uploaded_video.name)
        save_buffer_to_file(uploaded_video, uploaded_video.name)
        st.rerun()

    elif youtube_url:
        if st.session_state.app_state.value != AppState.UPLOAD.value:
            return
        st.session_state.app_state = AppState.DOWNLOAD
        st.rerun()


def download_video():
    progress_bar = st.progress(0)

    def progress_function(stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        progress = bytes_downloaded / total_size
        progress_bar.progress(progress, text=f"Downloading: {int(progress * 100)}%")

    st.spinner("Downloading video...")
    try:
        video_buffer, video_title = download_youtube_video(
            st.session_state.youtube_url, progress_function
        )
    except Exception as e:
        st.session_state.youtube_url = ""
        st.session_state.app_state = AppState.DOWNLOAD_ERROR
        st.session_state.error_message = remove_ansi_codes(str(e)).strip()
        print("Error downloading video:", st.session_state.error_message)
        st.rerun()
        return

    st.session_state.video_file = video_buffer
    st.session_state.video_title = video_title

    st.session_state.app_state = AppState.PROCESSING
    st.rerun()


def upload_video():
    st.title("Upload")
    current_state = st.session_state.app_state.value

    is_disabled_upload = (
        current_state != AppState.UPLOAD.value
        and current_state != AppState.DOWNLOAD_ERROR.value
    )

    if current_state == AppState.DOWNLOAD_ERROR.value:
        st.error(
            f"""Error downloading video.\n
            {st.session_state.error_message}.\n
            Please check the URL {st.session_state.youtube_url} and try again."""
        )
        st.session_state.youtube_url = ""
        st.session_state.app_state = AppState.UPLOAD
        current_state = AppState.UPLOAD.value

    upload_input(is_disabled_upload)

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

    if current_state == AppState.COMPLETE.value:
        st.success("Processing complete!")
        st.info("Go to the Analysis tab to view the results!")
