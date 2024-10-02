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
from database import User, Video, VideoAnalysis
from sqlalchemy.orm import Session
import enum


class AnalysisStage(enum.Enum):
    STARTED = "started"
    DONE = "done"


class VideoStage(enum.Enum):
    PROCESSING = "processing"
    DONE = "done"


class Processing:
    def __init__(self, get_db, user_id):
        self.db_session = get_db
        self.user_id = user_id
        self.process_id = str(uuid4())
        self.vision_processing = VideoProcessing()
        self.audio_processing = AudioProcessing()

    def _get_video(self) -> Video:
        sess: Session = next(self.db_session())
        video = sess.query(Video).filter_by(process_id=self.process_id).first()
        return video

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

    def start_analysis(self, analysis: str) -> VideoAnalysis:
        sess: Session = next(self.db_session())
        video: Video = self._get_video()
        va = VideoAnalysis(
            video_id=video.id,
            analysis=analysis,
            stage=AnalysisStage.STARTED.value,
        )
        sess.add(va)
        sess.commit()

        return va

    def update_analysis_stage(
        self, analysis: VideoAnalysis, stage: AnalysisStage, perc: float = 0.0
    ):
        sess: Session = next(self.db_session())
        analysis.stage = stage.value

        video = sess.query(Video).filter_by(process_id=self.process_id).first()
        if video is not None:
            video.perc = perc
            sess.commit()

    def get_processing_audio(self):
        return self.audio_processing.audio_processing_results

    def get_processing_video(self):
        return self.vision_processing.video_processing_results

    async def start(self, video_file, workspace_dir):
        sess: Session = next(self.db_session())
        # Save video data to the database
        video = Video(
            title=video_file.filename,  # Assuming title is the filename
            process_id=self.process_id,
            stage=VideoStage.PROCESSING.value,
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

    def done(self):
        sess: Session = next(self.db_session())
        video = self._get_video()
        video.stage = VideoStage.DONE.value
        sess.commit()

    def process_audio_visual(self):
        # Processing audio
        audio_analysis = self.start_analysis("audio")
        logging.info(f"Started udio processing - {self.process_id}")

        self.audio_processing.process_audio(self.video_path)

        self.update_analysis_stage(audio_analysis, AnalysisStage.DONE, 0.5)
        logging.info(f"Done audio processing - {self.process_id}")

        video_analysis = self.start_analysis("video")
        logging.info(f"Started video processing - {self.process_id}")

        self.vision_processing.process_video(self.video_path, self.process_workdir)

        self.update_analysis_stage(video_analysis, AnalysisStage.DONE, 1.0)

        self.done()
        logging.info(f"done - {self.process_id}")
