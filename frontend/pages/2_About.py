import streamlit as st

def about():
    st.title("About DeepVideo")
    st.write("""
    **DeepVideo** was developed for the HackAI - Dell and NVIDIA Challenge. This project leverages cutting-edge AI technologies to analyze video and audio content, generate insightful summaries, and allow users to query processed data for detailed information.
    """)

    st.subheader("Technologies Used")
    st.write("""
    - **Large Language Models (LLMs)** for text generation and understanding.
    - **LLaVA NexT OV 0.5b** for video analysis.
    - **WhisperX** for audio transcription with speaker IDs.
    - **FAISS** for efficient vector store querying.
    """)

    st.subheader("Team")
    st.write("""
    Developed by a team of AI enthusiasts as part of the HackAI competition.
    """)
    
if __name__ == "__main__":
    about()