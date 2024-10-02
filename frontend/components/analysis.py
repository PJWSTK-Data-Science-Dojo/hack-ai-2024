import time
import streamlit as st

from utils import AppState, api


def analysis_page():
    st.title("Analysis")
    with st.spinner("Waiting for video to process..."):
        while st.session_state.app_state != AppState.COMPLETE:
            time.sleep(1)

    srt_file = api.get_srt_file(st.session_state.video_id)
