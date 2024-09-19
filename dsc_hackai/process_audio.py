import pathlib
import requests
import whisperx
import librosa
import numpy as np
import subprocess
import time
from api.whisperx import whisperx_endpoint


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


def process_audio(video_path: pathlib.Path):
    """
    Run pipeline to get data from audio.
    """
    start_time = time.time()
    wav_audio_path = video_path.with_suffix(".wav")
    print("Splitting audio to chunks")
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
        ]
    )
    print("Splitted audio to chunks")

    #    # Transcribe audio file to text
    whisperx_inf = whisperx_endpoint()
    transcription = whisperx_inf.inference(wav_audio_path)

    # Generate Loud / Silent labels
    loudness_data = analyze_audio(wav_audio_path)
    end_time = time.time()
    delta_time = end_time - start_time
    print(f"Time spent processing audio: {delta_time:.2f}")
    return {"transcription": transcription, "loudness": loudness_data}
