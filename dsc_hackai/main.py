import os
import logging
import uvicorn
import pathlib
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from uuid import uuid4
from dsc_hackai.processing import Processing
import shutil

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)-s %(message)s")

jobs = []
workspace_dir = pathlib.Path(
    "/Users/daniel/Developer/_DEVELOPED_APPS/_PJATK/DSC_HACKAI/dsc_hackai/processed_video"
)


def remove_directory(dir_path):
    try:
        shutil.rmtree(dir_path)
        print(f"Directory '{dir_path}' and its contents have been deleted.")
    except OSError as e:
        print(f"Error: {e}")


@app.on_event("startup")
def startup_event():
    remove_directory(str(workspace_dir))
    workspace_dir.mkdir(parents=True, exist_ok=True)


@app.on_event("shutdown")
def shutdown_event():
    remove_directory(str(workspace_dir))


@app.post("/api/v1/analysis")
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


@app.get("/api/v1/analysis/stage/{process_id}")
async def get_processing_status(process_id: str):
    global jobs
    for job in jobs:
        if str(job.id) == process_id:
            return await job.get_processing_stage()
    raise HTTPException(status_code=404, detail="Process not found.")


@app.get("/api/v1/analysis/data/{process_id}")
async def get_processing_status(process_id: str):
    global jobs
    for job in jobs:
        if str(job.id) == process_id:
            return {job._data}
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


# Run the FastAPI application on port 5000
# if __name__ == "__main__":
#   uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False, access_log=False)
