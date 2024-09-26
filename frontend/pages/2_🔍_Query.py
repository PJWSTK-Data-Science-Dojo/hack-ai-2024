import streamlit as st
from components import video_player
from mockups.videos import get_user_videos, get_video_by_id
from utils.auth import check_auth


def querying():
    videos = get_user_videos()

    st.title("Querying")
    st.header("Search and Explore Processed Data")

    selected_video = st.selectbox("Select a video:", videos, key="selected_video")
    if selected_video:
        video_buffer = get_video_by_id(selected_video)

        if video_buffer is None:
            st.error(f"Video {selected_video} file not found.")
            return

        video_player.video_player(
            video_buffer,
            timestamps=[
                (10, "Jump to 10 seconds"),
                (30, "Jump to 30 seconds"),
                (60, "Jump to 1 minute"),
                (120, "Jump to 2 minutes"),
            ],
        )


def query_page():
    check_auth()

    if "selected_video" not in st.session_state:
        st.session_state.selected_video = None

    st.set_page_config(layout="wide")
    querying()


if __name__ == "__main__":
    query_page()
