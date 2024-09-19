import os
import tempfile
import argparse
from pathlib import Path
import json

from process_vision import process_vision
from process_audio import process_audio


def process(video_path: Path):
    # res_audio = process_audio(video_path)
    # with open(video_path.with_suffix(".json"), "w") as f:
    #     f.write(json.dumps({"audio_data": res_audio}))
    res_video = process_vision(video_path)
    with open(video_path.with_suffix(".json"), "w") as f:
        f.write(json.dumps({"video_data": res_video}))



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


main()
