import pathlib
import requests
import librosa
import numpy as np
import subprocess
import logging
import time
import json

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS, VectorStore

import textstat

from machine_learning_apis.whisper import whisperx_endpoint_test

from audio.srt_gen import gen_srt_file
from audio.find_similiar_sentences_transcription import find_similiar_sentences
from audio.ai_textual_report import get_ai_textual_report

model_name = "intfloat/multilingual-e5-small"
embeddings = HuggingFaceBgeEmbeddings(model_name=model_name)


def concat_subtitles(transcription_segments):
    all_text = ""
    for transcription_dict in transcription_segments:
        all_text += transcription_dict["text"]
    return all_text


class AudioProcessing:
    def __init__(self):
        self.audio_processing_results = {}

    def generate_vector_store(
        self, segements, workspace_dir: pathlib.Path
    ) -> VectorStore:
        """Generates a vector store from a list of segments."""
        logging.debug("Generating vector store")
        documents = []
        for segment_dict in segements:
            doc = Document(
                page_content=segment_dict["text"],
                metadata={
                    "speaker_id": segment_dict["speaker"],
                    "start": segment_dict["start"],
                    "end": segment_dict["end"],
                },
            )
            documents.append(doc)
        # Save vector store
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(workspace_dir, "audio_vector_store")
        logging.debug("Vector store generated")

    def process_audio(self, video_path: pathlib.Path):
        """
        Run pipeline to get data from audio.
        - Video to audio
        - Transcription using WhisperX
        - Generates Vector Store from transcription - allows to be queried by user
        - Create output .srt file from WhisperX transcription
        - Find similiar sentences
        - Create LLM textual report
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
        whisperx_inf = whisperx_endpoint_test()
        transcription = whisperx_inf.inference(wav_audio_path)
        if transcription is None:
            raise RuntimeError("Transcription failed")
        logging.info("Transcription done")

        pathlib.Path(video_path.parent, "audio").mkdir(parents=True, exist_ok=True)
        gen_srt_file(
            transcription["segments"],
            pathlib.Path(video_path.parent, "audio", "subtitles.srt"),
        )

        end_time = time.time()
        delta_time = end_time - start_time

        plain_transcription = concat_subtitles(transcription["segments"])
        self.audio_processing_results = {
            "similiar_sentences": find_similiar_sentences(transcription["segments"]),
            "ai_textual_reports": get_ai_textual_report(
                video_path.stem, plain_transcription
            ),
            "index_fog": textstat.gunning_fog(plain_transcription),
            "index_flesch": textstat.flesch_reading_ease(plain_transcription),
        }
        logging.info(f"Time spent processing audio: {delta_time:.2f}")

        self.generate_vector_store(transcription["segments"], video_path.parent)
