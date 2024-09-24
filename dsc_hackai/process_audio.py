import pathlib
import requests
import librosa
import numpy as np
import subprocess
import logging
import time
import json

import faiss
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS, VectorStore

from dsc_hackai.machine_learning_apis.whisperx import whisperx_endpoint

model_name = "intfloat/multilingual-e5-small"
embeddings = HuggingFaceBgeEmbeddings(model_name=model_name)


def analyze_audio(file_path):
    """Analyzes an audio file for loudness and returns a list of chunks with loudness values.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        list: A list of tuples, where each tuple contains the start time, end time, and loudness value for a chunk.
    """

    # Load the audio file
    y, sr = librosa.load(file_path)

    # Calculate the root mean square (RMS) energy of the audio signal
    rms = librosa.feature.rms(y=y)[0]

    # Normalize the RMS values to a range of 0 to 1
    normalized_rms = rms / np.max(rms)

    # Define chunk size in seconds
    chunk_size = 0.5

    # Calculate the number of frames per chunk (based on RMS resolution)
    hop_length = 512  # Default hop_length used by librosa.feature.rms
    frames_per_chunk = int((chunk_size * sr) / hop_length)

    # Divide the audio into chunks and calculate loudness for each chunk
    chunks = []
    for i in range(0, len(normalized_rms), frames_per_chunk):
        end_frame = min(i + frames_per_chunk, len(normalized_rms))
        start_time = float(
            librosa.frames_to_time(i, sr=sr, hop_length=hop_length)
        )  # Convert to native Python float
        end_time = float(
            librosa.frames_to_time(end_frame, sr=sr, hop_length=hop_length)
        )  # Convert to native Python float
        loudness = float(
            np.mean(normalized_rms[i:end_frame])
        )  # Convert to native Python float

        chunks.append([start_time, end_time, loudness])

    return chunks


class AudioProcessing:
    def __init__(self):
        self.audio_vector_store = None
        self.audio_processing_results = {}

    def generate_vector_store(self, segements) -> VectorStore:
        """Generates a vector store from a list of segments."""
        logging.debug("Generating vector store")
        documents = []
        for segment_dict in segements:
            doc = Document(
                page_content=segment_dict["text"],
                metadata={
                    "speaker_id": segment_dict["speaker"],
                    "start_ts": segment_dict["start"],
                    "end_ts": segment_dict["end"],
                },
            )
            documents.append(doc)
        # Setup Model
        vector_store = FAISS.from_documents(documents, embeddings)
        logging.debug("Vector store generated")
        self.audio_vector_store = vector_store

    def process_audio(self, video_path: pathlib.Path):
        """
        Run pipeline to get data from audio.
        """
        start_time = time.time()
        wav_audio_path = video_path.with_suffix(".wav")
        logging.info("Splitting audio to chunks")
        subprocess.run(
            [
                "ffmpeg",
                "-i",
                video_path,
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-y",
                wav_audio_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        logging.info("Splitted audio to chunks")

        # Transcribe audio file to text
        logging.info("Running transcription")
        whisperx_inf = whisperx_endpoint()
        transcription = whisperx_inf.inference(wav_audio_path)
        if transcription is None:
            raise RuntimeError("Transcription failed")
        logging.info("Transcription done")

        # Generate Loud / Silent labels
        logging.info("Generate Loud / Silent labels")
        loudness_data = analyze_audio(wav_audio_path)
        logging.info("Generated Loud / Silent labels")
        end_time = time.time()
        delta_time = end_time - start_time
        logging.info(f"Time spent processing audio: {delta_time:.2f}")

        self.audio_processing_results = {
            "transcription": transcription,
            "loudness": loudness_data,
        }
        self.generate_vector_store(transcription["segments"])
        # vs.save_local(pathlib.Path(video_path.parent, "audio_data_vectore_store"))
