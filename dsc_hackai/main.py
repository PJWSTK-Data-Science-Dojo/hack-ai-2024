import os
import tempfile
import argparse
from pathlib import Path
from dsc_hackai.process_vision import process_vision


def process(video_path):
    process_vision(video_path)


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

    process(args.source_video_path)
