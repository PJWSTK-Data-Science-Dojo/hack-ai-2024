import streamlit as st

from mockups.auth import validate_token


def check_auth():
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None
        st.switch_page("pages/Login.py")
        return False

    if not st.session_state.auth_token:
        st.switch_page("pages/Login.py")
        return False

    if not validate_token(st.session_state.auth_token):
        st.session_state.auth_token = None
        st.switch_page("pages/Login.py")
        return False

    return True
