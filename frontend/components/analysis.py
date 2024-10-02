import time
import streamlit as st

from utils import AppState, api


def analysis_page():
    st.title("Analysis")
    with st.spinner("Waiting for video to process..."):
        while (
            st.session_state.app_state.value != AppState.PROCESSING.value
            and st.session_state.app_state.value != AppState.COMPLETE.value
        ):
            time.sleep(1)

