import io
import requests

BACKEND_URL = "http://localhost:8000"


def get_user(username: str) -> bool:
    url = f"{BACKEND_URL}/api/v1/user"
    try:
        print(username)
        response = requests.get(url, params={"username": username})

        if response.status_code == 200:
            data = response.json()
            print(data)
            return data
    except Exception as e:
        print(f"Error logging in: {e}")

    return None


def register(username: str) -> bool:
    url = f"{BACKEND_URL}/api/v1/register"
    try:
        response = requests.post(url, json={"username": username})

        if response.status_code == 200:
            data = response.json()
            print(data)
            return data

    except Exception as e:
        print(f"Error registering: {e}")

    return None


def start_analysis(user_id: int, video_buffer: io.BytesIO) -> bool:
    url = f"{BACKEND_URL}/api/v1/start_analysis"
    try:
        response = requests.post(
            url,
            params={"user_id": str(user_id)},
            files=[("video_file", video_buffer)],
        )

        if response.status_code == 200:
            data = response.json()
            print(data)
            return data

    except Exception as e:
        print(f"Error starting analysis: {e}")

    return None


def get_analysis_stage(process_id: int) -> bool:
    url = f"{BACKEND_URL}/api/v1/analysis/stage/{process_id}"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(data)
            return data
    except Exception as e:
        print(f"Error getting analysis stage: {e}")

    return None


def get_srt_file(process_id: int) -> bool:
    url = f"{BACKEND_URL}/api/v1/analysis/data/audio/transcription"
    try:
        response = requests.get(url, params={"process_id": process_id})

        if response.status_code == 200:
            data = response.json()
            print(data)
            return data
    except Exception as e:
        print(f"Error getting srt file: {e}")

    return None
