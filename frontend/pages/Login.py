import streamlit as st

from mockups.auth import authenticate, register


def login_form():
    with st.form(key="login_form"):
        st.markdown("## Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submit_button = st.form_submit_button(label="Login")

    if submit_button:
        auth_token = authenticate(username, password)
        if auth_token is not None:
            st.session_state.auth_token = auth_token
            st.switch_page("pages/1_🎬_DeapVideo.py")
        else:
            st.error("Invalid username or password")


def register_form():
    with st.form(key="register_form"):
        st.markdown("## Register")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        submit_button = st.form_submit_button(label="Register")

    if submit_button:
        auth_token, message = register(username, password)
        if auth_token is not None:
            st.session_state.auth_token = auth_token
            st.switch_page("pages/1_🎬_DeapVideo.py")
        else:
            st.error(message)


# @st.dialog("Signin") # There is no option to prevent user from closing the dialog
def login_page():
    if "auth_token" not in st.session_state:
        st.session_state.auth_token = None

    if st.session_state.auth_token:
        st.warning("You've been logged out!")

    st.session_state.auth_token = None

    c1, c2 = st.columns([1, 1])
    with c1:
        login_form()

    with c2:
        register_form()


if __name__ == "__main__":
    login_page()
