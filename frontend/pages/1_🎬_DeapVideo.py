import time
from jinja2 import Template
import streamlit as st
import enum
import base64
from utils import read_template
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
    uploaded_video = st.file_uploader("Or choose a video...", type=["mp4", "avi", "mov"])

    if uploaded_video:
        st.session_state.app_state = AppState.PROCESSING
        st.session_state.video_file = uploaded_video
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
    video_buffer = download_youtube_video(st.session_state.youtube_url, progress_function)
    
    if video_buffer is None:
        st.session_state.youtube_url = ""
        st.session_state.app_state = AppState.DOWNLOAD_ERROR
        st.rerun()
        return
    
    st.session_state.video_file = video_buffer
    st.session_state.app_state = AppState.PROCESSING
    st.rerun()

def querying():
    st.title("Querying")
    st.header("Search and Explore Processed Data")

    st.write("""
    Query the processed data to extract specific insights from the video and audio.
    You can search for general summaries, dialogs, themes, and highlights based on the media content.
    """)
    
    # Placeholder for querying functionality
    query = st.text_input("Enter your query:")
    if query:
        st.write(f"Fetching results for: {query}")


def deep_video():
    st.title("DeepVideo")
    st.header(f"Video and Audio Processing - {st.session_state.app_state.value.capitalize()}")
    current_state = st.session_state.app_state.value
    
    if current_state == AppState.DOWNLOAD_ERROR.value:
        st.error(f"Error downloading video. Please check the URL {st.session_state.youtube_url} and try again.")
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
        st.write("Processing complete!")
        st.write("You can now explore the processed data.")
        if 'video_file' in st.session_state and st.session_state.video_file:
            template_str = read_template("video_player")
            template = Template(template_str)
            timestamps = [
                (10, "Jump to 10 seconds"),
                (30, "Jump to 30 seconds"),
                (60, "Jump to 1 minute"),
                (120, "Jump to 2 minutes")
            ]
            # Render the template with dynamic data
            html_output = template.render(
                video_url=f"data:video/mp4;base64,{base64.b64encode(st.session_state.video_file.getvalue()).decode()}",
                subtitle_url="",
                timestamps=timestamps
            )
            
            st.components.v1.html(html_output, height=600)
        else:
            st.warning("No video file found to display.")
            
        querying()
        return

if __name__ == "__main__":
    deep_video()