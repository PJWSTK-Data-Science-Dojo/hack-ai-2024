from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from dsc_hackai.api.llava_next import llava_next_endpoint
from dsc_hackai.api.gemma import gemma_endpoint

llava_inferencing = llava_next_endpoint()
gamma_inferencing = gemma_endpoint()


# Enum for emotions
class EmotionsEnum(str, Enum):
    happy = "happy"
    sad = "sad"
    angry = "angry"
    surprised = "surprised"
    scared = "scared"
    disgusted = "disgusted"
    neutral = "neutral"


# BaseModel Schema
class VideoAnalysis(BaseModel):
    video_chunk: str  # Description of what's in the video chunk
    objects_in_scene: str  # Description of objects present in the scene
    object_movements: str  # How the objects are moving in the scene
    camera_movements: str  # How the camera is moving (e.g., panning, zooming, etc.)
    emotions_shown: List[EmotionsEnum]  # List of emotions shown in the video
    multiple_view_changes: bool  # Whether there were multiple changes in view


video_analysis_schema_json = VideoAnalysis.schema_json()
video_questions = [
    "what is in video",
    "what objects are there",
    "how object are moving there",
    "how camera is moving",
    "what emotions are shown",
    "were there multiple changes in view",
]


def analyze(video_chunk_file_path):
    """
    Analyzes a video chunk and returns a VideoAnalysis
    """
    llava_res = llava_inferencing.inference(video_chunk_file_path, video_questions)
    # Now parse responses to JSON using gemma
    # for single_llava_res in llava_res:
