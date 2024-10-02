from datetime import datetime
from pydantic import BaseModel, validator
from typing import List, Optional


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


class AnalysisStage(BaseModel):
    stage: str
    time: datetime


class AnalysisStageResponse(BaseModel):
    frames_processed: int
    frames_all: int
    stages: List[AnalysisStage]


class QueryBody(BaseModel):
    user_query: str


# Video
class VideoVSFilters(BaseModel):
    start: Optional[int] = None
    end: Optional[int] = None

    @validator("start", "end", pre=True)
    def validate_ts(cls, value):
        if value is not None:
            return int(value)
        return value


class VideoVSResult(BaseModel):
    query: str
    filters: VideoVSFilters


class VideoVSQueryResponse(BaseModel):
    result: VideoVSResult


# Audio
class AudioVSFilters(BaseModel):
    speaker_id: Optional[str] = None
    start: Optional[float] = None
    end: Optional[float] = None

    @validator("start", "end", pre=True)
    def validate_ts(cls, value):
        if value is not None:
            return float(value)
        return value


class AudioVSResult(BaseModel):
    query: str
    filters: AudioVSFilters


class AudioVSQueryResponse(BaseModel):
    result: AudioVSResult
