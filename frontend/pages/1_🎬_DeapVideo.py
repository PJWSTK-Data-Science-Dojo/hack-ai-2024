import threading
import time
import concurrent.futures
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
import streamlit as st
from components import video_player
from components.analysis import analysis_page
from components.query import query_page
from components.upload import upload_video
from utils import AppState, api
from utils.auth import check_auth
from utils.youtube import download_youtube_video


if st.session_state.get("app_state") is None:
    st.session_state.app_state = AppState.UPLOAD


def deep_video():
    st.set_page_config(layout="wide")

    if not check_auth():
        st.stop()

    st.title("DeepVideo")
    st.header(
        f"Video and Audio Processing - {st.session_state.app_state.value.capitalize()}"
    )
    
    show_input = True
    if "video_file" in st.session_state and st.session_state.video_file is not None:
        show_input = False
        srt_file = None
        if "video_id" in st.session_state and st.session_state.video_id is not None:
            srt_file = api.get_srt_file(st.session_state.video_id)
        
        video_player.video_player(st.session_state.video_file, srt_file)
        
        
    tabs = ["📁Upload", "🔍Query", "📈Analysis"]
        
    upload_tab, query_tab, analysis_tab = st.tabs(tabs)
    
    with query_tab:
        query_page()  

    with upload_tab:
        upload_video(show_input)

    with analysis_tab:
        analysis_page()
    
    with upload_tab:
        st.write("Upload")        





if __name__ == "__main__":
    deep_video()
