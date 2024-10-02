import logging
import threading
import pathlib

from video._process_video import VideoProcessing
from audio._process_audio import AudioProcessing

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

import asyncio
from uuid import uuid4
from database import User, Video


class Processing:
    def __init__(self, get_db, user_id):
        self.db_session = get_db
        self.user_id = user_id
        self.process_id = str(uuid4())
        self.vision_processing = VideoProcessing()
        self.audio_processing = AudioProcessing()

    async def get_processing_stage(self):
        sess = next(self.db_session())
        video = sess.query(Video).filter_by(process_id=self.process_id).first()
        if video is not None:
            return {
                "video_frames_processed": len(
                    self.vision_processing.video_processing_results
                ),
                "video_frames_all": self.vision_processing.video_processing_all_frames_count,
                "stages": video.stage,
            }

    def update_db_stage(self, stage: str, perc: float = 0.0):
        sess = next(self.db_session())
        # Query the video with the given process_id
        video = sess.query(Video).filter_by(process_id=self.process_id).first()
        if video is not None:
            # Update the stage of the video
            video.stage = stage
            video.perc = perc
            sess.commit()

    def get_processing_audio(self):
        return self.audio_processing.audio_processing_results

    def get_processing_video(self):
        return self.vision_processing.video_processing_results

    async def start(self, video_file, workspace_dir):
        sess = next(self.db_session())
        # Save video data to the database
        video = Video(
            title=video_file.filename,  # Assuming title is the filename
            process_id=self.process_id,
            stage="processing",
            user_id=self.user_id,
        )
        sess.add(video)
        sess.commit()
        sess.refresh(video)
        # Generate a unique filename
        filename = self.process_id + "." + video_file.filename.split(".")[-1]
        self.process_workdir = pathlib.Path(workspace_dir, self.process_id)
        self.process_workdir.mkdir(parents=True, exist_ok=False)

        # Save the uploaded video to a specified directory
        self.video_path = pathlib.Path(self.process_workdir, filename)
        with open(self.video_path, "wb") as file:
            file.write(await video_file.read())

        logging.info(f"Process started. ID: {self.process_id}")
        # await self.process_audio_visual()
        threading.Thread(target=self.process_audio_visual).start()
        return self.process_id

    def process_audio_visual(self):
        # Processing audio
        self.update_db_stage("started_audio_processing", 0.25)
        logging.info(f"started_audio_processing - {self.process_id}")

        self.audio_processing.process_audio(self.video_path)

        self.update_db_stage("done_audio_processing", 0.5)
        logging.info(f"done_audio_processing - {self.process_id}")

        # Processing video
        self.update_db_stage("started_video_processing", 0.75)
        logging.info(f"started_video_processing - {self.process_id}")

        self.vision_processing.process_video(self.video_path, self.process_workdir)

        self.update_db_stage("done", 1.0)
        logging.info(f"done - {self.process_id}")
