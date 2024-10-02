import streamlit as st

from components.login import login_page


def check_auth():
    if "user_id" not in st.session_state:
        login_page()
        return False

    return True
