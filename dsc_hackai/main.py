import os
import shutil
from datetime import datetime
import logging
import pathlib
from pydantic import BaseModel
from typing import List
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Depends
from fastapi.responses import FileResponse

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from database import Video, User, Base, SessionLocal
from processing import Processing
from process_llm import query_vs_llm


app = FastAPI()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


logging.basicConfig(level=logging.INFO, format="%(asctime)-s %(message)s")

jobs = []
workspace_dir = pathlib.Path("./project/data")
workspace_dir.mkdir(parents=True, exist_ok=True)


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    user_id: int
    allowed_to_use: bool


class UserLoginResponse(UserResponse):
    videos: List[dict] = []


class AnalysisResponse(BaseModel):
    process_id: str


@app.post("/api/v1/start_analysis", response_model=AnalysisResponse, tags=["Analysis"])
async def upload_video_for_analysis(user_id: int, video_file: UploadFile = File(...)):
    # Create a processing object
    processor = Processing(get_db, user_id)

    # Start the asynchronous processing and return the ID
    try:
        process_id = await processor.start(video_file, workspace_dir)
    except Exception as e:
        raise HTTPException(status_code=503, detail=e)

    return {"process_id": process_id}


class AnalysisStage(BaseModel):
    stage: str
    time: datetime


class AnalysisStageResponse(BaseModel):
    frames_processed: int
    frames_all: int
    stages: List[AnalysisStage]


@app.get("/api/v1/analysis/stage/{process_id}", tags=["Response Data"])
async def get_processing_stage(process_id: str, db: Session = Depends(get_db)):
    job = db.query(Video).filter(Video.process_id == process_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Process not found.")
    return {"stage": job.stage, "perc": job.perc}


@app.get("/api/v1/analysis/data/audio/transcription", tags=["Response Data"])
async def get_srt_file(process_id: str):
    """
    Get the audio transcription from the processing job.
    """
    file_path = pathlib.Path(workspace_dir, process_id, "audio", f"subtitles.srt")
    if file_path.exists():
        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/octet-stream",
        )
    else:
        raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/v1/analysis/data/audio", tags=["Response Data"])
async def get_audio_data_for_process(process_id: str):
    job = db.query(Video).filter(Video.process_id == process_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Process not found.")
    # TODO: After creating all fields in DB


@app.get("/api/v1/analysis/data/video", tags=["Response Data"])
async def get_video_data_for_process(process_id: str):
    job = db.query(Video).filter(Video.process_id == process_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Process not found.")
    # TODO: After creating all fields in DB


@app.post("/api/v1/analysis/ask/{process_id}", tags=["Response Data"])
async def ask_about_video(process_id: str, request: Request):
    for process_id_dir in pathlib.Path(workspace_dir, process_id):
        if str(process_id_dir) == process_id:
            query = await request.json()
            # Process the query and generate a response
            response = query_vs_llm(
                pathlib.Path(workspace_dir, process_id, "audio_vector_store"),
                pathlib.Path(workspace_dir, process_id, "video_vector_store"),
                600,
                query["user_query"],
            )
            return {"response": response}
    raise HTTPException(status_code=404, detail="Process not found.")


@app.post("/api/v1/register", response_model=UserResponse, tags=["Account"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(username=user.username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(
        user_id=new_user.id,
        allowed_to_use=new_user.allowed_to_use,
    )


@app.get("/api/v1/user", tags=["Account"])
async def get_user_data(username: str, user_id: int, db: Session = Depends(get_db)):
    if not username and not user_id:
        raise HTTPException(status_code=401)
    if username:
        existing_user = db.query(User).filter(User.username == username).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
    # if user_id:
    #     existing_user = db.query(User).filter(User.id == user_id).first()
    #     if not existing_user:
    #         raise HTTPException(status_code=404, detail="User not found")

    videos_data = []
    for video in existing_user.videos:
        video_info = {
            "title": video.title,
            "process_id": video.process_id,
            "stage": video.stage,
        }
        videos_data.append(video_info)

    response = UserLoginResponse(
        user_id=existing_user.id,
        allowed_to_use=existing_user.allowed_to_use,
        videos=videos_data,
    )
    return response


# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False, access_log=False)
