import os
import tempfile
import argparse
from pathlib import Path
import json
import logging

from dsc_hackai.process_vision import process_vision
from dsc_hackai.process_audio import process_audio

logging.basicConfig(level=logging.INFO, format="%(asctime)-s %(message)s")


def process(video_path: Path):
    logging.info("Processing Audio")
    res_audio_dict, vs_audio = process_audio(video_path)
    vs_audio.save_local("faiss_audio")

    logging.info("Processing Vision")
    res_video = process_vision(video_path)


def main():
    parser = argparse.ArgumentParser(description="Process video file.")
    parser.add_argument(
        "--source_video_path", help="The path to the source video file."
    )
    parser.add_argument(
        "--audio_desc",
        action="store_true",
        help="Include audio description in the output.",
    )
    parser.add_argument(
        "--video_desc",
        action="store_true",
        help="Include video description in the output.",
    )

    args = parser.parse_args()

    print(f"Source video path: {args.source_video_path}")
    if args.audio_desc:
        print("Include audio description")
    if args.video_desc:
        print("Include video description")

    process(Path(args.source_video_path))
