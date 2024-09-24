import logging
import threading
import pathlib

from dsc_hackai.process_vision import VisionProcessing
from dsc_hackai.process_audio import AudioProcessing
from dsc_hackai.processing_llm import query_llm
import ollama

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

import asyncio
from uuid import uuid4


class Processing:
    def __init__(self):
        self.id = str(uuid4())
        self.stages = [
            {
                "stage": "started_initialized",
                "time": datetime.now().strftime("%H:%M:%S"),
            }
        ]
        self.vision_processing = VisionProcessing()
        self.audio_processing = AudioProcessing()

        self._data = {}

    async def get_processing_stage(self):
        return {
            "video_frame_processed": len(
                self.vision_processing.video_processing_results
            ),
            "all_video_frames": self.vision_processing.video_processing_all_frames_count,
            "stages": self.stages,
        }

    async def start(self, video_file, workspace_dir):

        # Generate a unique filename
        filename = self.id + "." + video_file.filename.split(".")[-1]
        self.process_workdir = pathlib.Path(workspace_dir, self.id)
        self.process_workdir.mkdir(parents=True, exist_ok=False)

        # Save the uploaded video to a specified directory
        self.video_path = pathlib.Path(self.process_workdir, filename)
        with open(self.video_path, "wb") as file:
            file.write(await video_file.read())
        self.stages = [
            {"stage": "done_initialized", "time": datetime.now().strftime("%H:%M:%S")}
        ]
        logging.info(f"Process started. ID: {self.id}")
        # await self.process_audio_visual()
        threading.Thread(target=self.process_audio_visual).start()
        return self.id

    def process_audio_visual(self):
        # Processing audio
        self.stages.append(
            {"stage": "started_audio", "time": datetime.now().strftime("%H:%M:%S")}
        )
        logging.info(f"{self.stages[-1]['stage']} - {self.id}")
        self.audio_processing.process_audio(self.video_path)
        self.stages.append(
            {"stage": "done_audio", "time": datetime.now().strftime("%H:%M:%S")}
        )
        logging.info(f"{self.stages[-1]['stage']} - {self.id}")
        # Processing video
        self.stages.append(
            {"stage": "started_visual", "time": datetime.now().strftime("%H:%M:%S")}
        )
        logging.info(f"{self.stages[-1]['stage']} - {self.id}")
        self.vision_processing.process_vision(self.video_path, self.process_workdir)
        self.stages.append(
            {"stage": "done_visual", "time": datetime.now().strftime("%H:%M:%S")}
        )
        logging.info(f"{self.stages[-1]['stage']} - {self.id}")

    def ask_llm(self, query):
        return query_llm(
            self.audio_processing.audio_vector_store,
            self.vision_processing.video_vector_store,
            600,
            query,
        )
