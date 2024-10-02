import time
import streamlit as st
from components.upload import upload_video
from utils import AppState
from utils.youtube import download_youtube_video


if st.session_state.get("app_state") is None:
    st.session_state.app_state = AppState.UPLOAD


def deep_video():
    st.set_page_config(layout="wide")

    st.title("DeepVideo")
    st.header(
        f"Video and Audio Processing - {st.session_state.app_state.value.capitalize()}"
    )
    upload_tab, analysis_tab, query_tab = st.tabs(["📁Upload", "📈Analysis", "🔍Query"])

    with upload_tab:
        upload_video()

    with analysis_tab:
        st.title("Analysis")
        with st.spinner("Waiting for video to process..."):
            while st.session_state.app_state != AppState.COMPLETE:
                time.sleep(1)

    with query_tab:
        st.title("Query")
        with st.spinner("Waiting for video to process..."):
            while st.session_state.app_state != AppState.COMPLETE:
                time.sleep(1)


if __name__ == "__main__":
    deep_video()
