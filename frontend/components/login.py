import streamlit as st

from mockups.auth import authenticate, register

DEFAULT_USERNAME = "Anonymous"


def login_form():
    with st.form(key="login_form"):
        st.markdown("## Username")

        username = st.text_input("Username", value=st.session_state.username)

        submit_button = st.form_submit_button(label="Save")

    if submit_button:
        ok = authenticate(username)
        if ok:
            st.session_state.username = username
        else:
            st.error("Invalid username or password")


@st.dialog("Signin")
def login_page():

    if "username" not in st.session_state:
        st.session_state.username = DEFAULT_USERNAME

    if not st.session_state.username:
        st.session_state.username = DEFAULT_USERNAME

    login_form()


if __name__ == "__main__":
    login_page()
