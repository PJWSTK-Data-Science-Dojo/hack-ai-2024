import os
from datetime import datetime
import logging
import uvicorn
import pathlib
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from uuid import uuid4
from processing import Processing
import shutil
from pydantic import BaseModel
from typing import List

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)-s %(message)s")

jobs = []
workspace_dir = pathlib.Path(
    "/project/data"
)
workspace_dir.mkdir(parents=True, exist_ok=True)


class AnalysisResponse(BaseModel):
    process_id: str


@app.post("/api/v1/analysis", response_model=AnalysisResponse, tags=["Analysis"])
async def upload_video(video_file: UploadFile = File(...)):
    global jobs

    # Create a processing object
    processor = Processing()
    jobs.append(processor)

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


@app.get("/api/v1/analysis/stage/{process_id}")
async def get_processing_status(process_id: str):
    global jobs
    for job in jobs:
        if str(job.id) == process_id:
            return await job.get_processing_stage()
    raise HTTPException(status_code=404, detail="Process not found.")


# class AnalysisDataResponse(BaseModel):


@app.get("/api/v1/analysis/data/{process_id}")
async def get_processing_status(process_id: str):
    global jobs
    for job in jobs:
        if str(job.id) == process_id:
            return job.get_processing_data()
    raise HTTPException(status_code=404, detail="Process not found.")


@app.post("/api/v1/analysis/ask/{process_id}")
async def ask_about_video(process_id: str, request: Request):
    global jobs
    for job in jobs:
        if str(job.id) == process_id:
            query = await request.json()
            # Process the query and generate a response
            response = job.ask_llm(query["user_query"])
            return {"response": response}
    raise HTTPException(status_code=404, detail="Process not found.")

@app.post("/api/v1/register")
async def register():
    pass

@app.post("/api/v1/login")
async def login():
    pass

# Run the FastAPI application on port 5000
if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False, access_log=False)
