import ollama
import json
from json import JSONDecodeError
from typing import Dict
from pydantic import BaseModel, validator, ValidationError
from typing import Optional

ollama_client = ollama.Client(host="192.168.1.42:11435")


# Video
class VideoVSFilters(BaseModel):
    start_ts: Optional[int] = None
    end_ts: Optional[int] = None

    @validator("start_ts", "end_ts", pre=True)
    def validate_ts(cls, value):
        if value is not None:
            return int(value)
        return value


class VideoVSResult(BaseModel):
    query: str
    filters: VideoVSFilters


class VideoVSQueryResponse(BaseModel):
    result: VideoVSResult


video_schema = VideoVSQueryResponse.model_json_schema()
video_schema_json = json.dumps(video_schema, indent=2)


def get_relevant_data_video(vs, query):
    vq: Optional[VideoVSQueryResponse] = None
    res = ollama_client.generate(
        model="gemma2:2b",
        options={"temperature": 0.15},
        format="json",
        prompt=f"# Response format\nResponse with JSON\n---\n{video_schema_json}\n---\n# User query\nuser need to find: '{query}' \n# Task: Generate query to filter data that will correspond with user query '{query}'",
    )["response"]
    try:
        res_json = json.loads(res)
        vq = VideoVSQueryResponse.parse_obj(res_json)
        print("Dictionary matches the Pydantic model.")
    except ValidationError as e:
        print("Dictionary does not match the Pydantic model.")
        print(str(e))
        return generate_query_video(vs, query)
    except JSONdecodeError as e:
        print("JSON decode error.")
        print(str(e))
        return generate_query_video(vs, query)

    vision_vs_q_res = vs.similarity_search(
        vq.result.query,
        k=10,
        filter=vq.result.filters,
    )
    return vision_vs_q_res


# Audio
class AudioVSFilters(BaseModel):
    speaker_id: Optional[str] = None
    start_ts: Optional[float] = None
    end_ts: Optional[float] = None

    @validator("start_ts", "end_ts", pre=True)
    def validate_ts(cls, value):
        if value is not None:
            return float(value)
        return value


class AudioVSResult(BaseModel):
    query: str
    filters: AudioVSFilters


class AudioVSQueryResponse(BaseModel):
    result: AudioVSResult


audio_schema = AudioVSQueryResponse.model_json_schema()
audio_schema_json = json.dumps(audio_schema, indent=2)


def get_relevant_data_audio(vs, query):
    aq: Optional[AudioVSQueryResponse] = None
    res = ollama_client.generate(
        model="gemma2:2b",
        options={"temperature": 0.15},
        format="json",
        prompt=f"# Response format\nResponse with JSON\n---\n{video_schema_json}\n---\n# User query\nuser need to find: '{query}' \n# Task: Generate query to filter data that will correspond with user query '{query}'",
    )["response"]
    try:
        res_json = json.loads(res)
        aq = AudioVSQueryResponse.parse_obj(res_json)
        print("Dictionary matches the Pydantic model.")
    except ValidationError as e:
        print("Dictionary does not match the Pydantic model.")
        print(str(e))
        return get_relevant_data_audio(vs, query)
    except JSONdecodeError as e:
        print("JSON decode error.")
        print(str(e))
        return get_relevant_data_audio(vs, query)

    audio_vs_q_res = vs.similarity_search(
        aq.result.query,
        k=10,
        filter=aq.result.filters,
    )
    return audio_vs_q_res


def query_llm(vs_audio, vs_video, video_length, user_query):
    all_data = ""

    # Generate audio data queries with filters
    audio_res = "\n".join(
        [
            f"{res.page_content} - {res.metadata}"
            for res in get_relevant_data_audio(vs_audio, user_query)
        ]
    )
    # Generate video data queries with filters
    video_res = "\n".join(
        [
            f"{res.page_content} - {res.metadata}"
            for res in get_relevant_data_video(vs_video, user_query)
        ]
    )

    # Using obtained data response to user
    ollama_client = ollama.Client(host="192.168.1.42:11435")
    res = ollama_client.generate(
        model="gemma2:2b",
        options={"temperature": 0.07},
        prompt=f"# Task\nWithout prior knownledge respond to user.\n\n# Knowledge\n ## Transcription \n---\n{audio_res} \n---\n ## Vision description \n---\n{video_res}\---\n. \n\n\n# User question\n{user_query}",
    )["response"]

    return res
