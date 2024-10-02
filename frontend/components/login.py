import streamlit as st

from utils import api

DEFAULT_USERNAME = "Anonymous"
DEFAULT_USER_ID = 1


def sign_form():
    with st.form(key="login_form"):
        username = st.text_input("Username", value=st.session_state.username)

        submit_button = st.form_submit_button(label="Save")

    if submit_button:
        if not username:
            st.error("Please enter a username!")
            st.rerun()
            return

        user_data = api.get_user(username)
        if user_data:
            st.session_state.username = username
            st.session_state.user_id = user_data["user_id"]
            st.info("User logged in! \n You can close dialog now.")
            st.rerun()

        print("Could not find user, registering...")
        user_data = api.register(username)
        if not user_data:
            st.error("Failed to fetch user!")
            return

        print("Registered user:", user_data)
        st.session_state.username = username
        st.session_state.user_id = user_data["user_id"]
        st.info("User registered successfully!")
        st.rerun()


@st.dialog("Signin")
def login_page():

    if "username" not in st.session_state or "user_id" not in st.session_state:
        st.session_state.username = DEFAULT_USERNAME
        st.session_state.user_id = DEFAULT_USER_ID

    if not st.session_state.username:
        st.session_state.username = DEFAULT_USERNAME
        st.session_state.user_id = DEFAULT_USER_ID

    sign_form()


if __name__ == "__main__":
    login_page()
