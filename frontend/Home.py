# app.py (Main controller, doesn't appear in navigation)
import streamlit as st


def main():
    st.set_page_config(layout="wide")

    st.title("DeepVideo - VisualAudio Flow")
    st.header("HackAI - Dell and NVIDIA Challenge")

    st.subheader("Project Overview")
    st.write(
        """
    **DeepVideo** is a video and audio summarization project developed for the HackAI - Dell and NVIDIA Challenge. The goal of the project is to analyze video and audio content, extract meaningful insights, and generate summaries using advanced AI techniques, including Large Language Models (LLMs).
    
    This project processes video content by segmenting it into 10-second chunks and analyzing each chunk for various aspects, such as:
    - Object recognition
    - Motion analysis
    - Camera movement
    - Emotional detection

    For audio, the project performs transcription with speaker identification and detects loud/quiet ranges.

    All processed data is saved in a vector store (FAISS) for fast querying, allowing users to search for specific information in the video and audio content.
    """
    )

    st.subheader("Process Flow")
    st.write(
        """
    1. **Video Analysis**: The video is segmented into chunks of 10 seconds. Each chunk is analyzed using `LLaVA NexT OV 0.5b` to detect objects, motion, camera behavior, emotions, and changes in view.
    2. **Audio Analysis**: The audio track is extracted from the video and analyzed using WhisperX to transcribe the dialogue with timestamps and detect loud and quiet segments.
    3. **Overlay & Summarization**: The results from both video and audio are combined into a unified summary that includes general insights, dialogs, themes, and highlights.
    4. **Querying**: Users can query the processed data for specific insights using an interactive interface.
    """
    )

    # Competition details
    st.subheader("About the Challenge")
    st.write(
        """
    This project was developed as part of the **HackAI - Dell and NVIDIA Challenge**. The competition focuses on developing AI solutions that can leverage Dell and NVIDIA hardware for high-performance computing in video and audio analysis.
    """
    )

    # Footer or additional notes
    st.write(
        """
    Explore the video and audio analysis features by uploading your own content, and start querying for detailed insights into the media.
    """
    )


if __name__ == "__main__":
    main()
