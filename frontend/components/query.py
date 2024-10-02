import time
import streamlit as st

from utils import AppState


def query_page():
    if "query_history" not in st.session_state:
        print("HEREEE")
        st.session_state.query_history = []
        
    st.title("Query")
    if st.session_state.app_state.value != AppState.COMPLETE.value and st.session_state.app_state.value != AppState.PROCESSING.value:
        with st.form(key="query_form"):
            st.warning("Waiting for uploaded file!")
            button = st.button("Refresh")
            if button:
                st.rerun()
                
            return
    
    
    with st.form(key="query_form", enter_to_submit=True):
        query_input = st.text_input("Enter your question here:", value="Whats the laguage used in the video?")
        submit_button = st.form_submit_button(label="Send question")
        
        if submit_button:
            st.session_state.query_history.append({
                "query": query_input,
                "response": "NO RESPONSE LOL :C"
            })
            st.rerun()
    
    with st.container():
        st.write("Query history:")
        print(st.session_state.query_history)
        for query in st.session_state.query_history:
            st.info(query["query"])        
            

