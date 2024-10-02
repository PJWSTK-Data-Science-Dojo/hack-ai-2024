import os
import logging
import pathlib

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse

from sqlalchemy.orm import Session

from database import Video, User, SessionLocal
from processing import Processing
from process_llm import query_vs_llm
from schemas import (
    AnalysisResponse,
    QueryBody,
    UserCreate,
    UserLoginResponse,
    UserResponse,
    VideoAnalysisStage,
    VideoStage,
)


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


@app.get("/api/v1/analysis/stage/{process_id}", tags=["Response Data"])
async def get_processing_stage(process_id: str, db: Session = Depends(get_db)):
    video: Video = db.query(Video).filter(Video.process_id == process_id).first()
    if video is None:
        raise HTTPException(status_code=404, detail="Process not found.")

    return VideoStage(
        video_stage=video.stage,
        perc=video.perc,
        analysis_stages=[
            VideoAnalysisStage.model_validate(vstage)
            for vstage in video.analysis_stages
        ],
    )


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
async def get_audio_data_for_process(process_id: str, db: Session = Depends(get_db)):
    job = db.query(Video).filter(Video.process_id == process_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Process not found.")
    # TODO: After creating all fields in DB


@app.get("/api/v1/analysis/data/video", tags=["Response Data"])
async def get_video_data_for_process(process_id: str, db: Session = Depends(get_db)):
    job = db.query(Video).filter(Video.process_id == process_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Process not found.")
    # TODO: After creating all fields in DB


@app.post("/api/v1/analysis/ask/{process_id}", tags=["Response Data"])
async def ask_about_video(process_id: str, query: QueryBody):
    process_dir = pathlib.Path(workspace_dir) / process_id

    if not process_dir.is_dir():
        raise HTTPException(status_code=404, detail="Process not found.")

    response = query_vs_llm(
        process_dir / "audio_vector_store",
        process_dir / "video_vector_store",
        query.user_query,
    )
    return {"response": response}


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
async def get_user_data(
    username: str | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
):
    if not username and not user_id:
        raise HTTPException(status_code=401)

    existing_user: User = None
    if username:
        existing_user = db.query(User).filter(User.username == username).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

    if user_id:
        existing_user = db.query(User).filter(User.id == user_id).first()
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    videos_data = []
    for video in existing_user.videos:
        video: Video

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
