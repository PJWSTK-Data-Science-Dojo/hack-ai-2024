import json
from json import JSONDecodeError
from pydantic import ValidationError
from typing import Optional

import ollama

from schemas import AudioVSQueryResponse, VideoVSQueryResponse

ollama_client = ollama.Client(host="192.168.1.42:11435")

video_schema = VideoVSQueryResponse.model_json_schema()
video_schema_json = json.dumps(video_schema, indent=2)

audio_schema = AudioVSQueryResponse.model_json_schema()
audio_schema_json = json.dumps(audio_schema, indent=2)


def get_relevant_data_video(vs, query):
    vq: Optional[VideoVSQueryResponse] = None
    while vq is None:
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
            vq = None
        except JSONDecodeError as e:
            print("JSON decode error.")
            print(str(e))
            vq = None

    vision_vs_q_res = vs.similarity_search(
        vq.result.query,
        k=10,
        filter=vq.result.filters,
    )
    return vision_vs_q_res


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
    except JSONDecodeError as e:
        print("JSON decode error.")
        print(str(e))
        return get_relevant_data_audio(vs, query)

    audio_vs_q_res = vs.similarity_search(
        aq.result.query,
        k=10,
        filter=aq.result.filters,
    )
    return audio_vs_q_res


def query_vs_llm(vs_audio, vs_video, user_query):
    audio_res = "\n".join(
        [
            f"{res.page_content} - {res.metadata}"
            for res in get_relevant_data_audio(vs_audio, user_query)
        ]
    )

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
        prompt=f"""
        # Task
        Without prior knownledge respond to user.
        # Knowledge
        ## Transcription 
        ---
        {audio_res} 
        ---
        ## Vision description 
        ---
        {video_res}
        ---. 


        # User question\n{user_query}
        """,
    )["response"]

    return res
