from dataclasses import dataclass, field
import enum
from typing import List, Tuple
import json
import requests


# from the server i would like to have get_info(user_id), which returns json object. Based on which we can create
# User dataclass

# my_videos -> WAITING_FOR_VIDEO, user needs to choose video from the list, after info -> VIEWING_SUMMARY uses llm
# summarize + ctx(video link, or video file)  -> WAITING_FOR_PROCESSED_DATA (works only for new videos)
# summary ctx(id of the video) ->  WAITING_FOR_VIDEO after we got info -> VIEWING_SUMMARY which directly uses llm


class States(enum.Enum):
    WAITING_FOR_VIDEO = 1
    WAITING_FOR_PROCESSED_DATA = 2

    VIEWING_SUMMARY = 3
    IDLE = 4
    DOESNT_EXISTS = 5


def create_user_from_data(data):
    try:
        json_data = json.loads(data)

        if 'user_id' not in json_data:
            raise ValueError("Missing 'user_id' in data")

        if not isinstance(json_data['user_id'], int):
            raise TypeError(f"Invalid type for user_id: expected int, got {type(json_data['user_id'])}")

        if 'state' in json_data:
            try:
                json_data['state'] = States[json_data['state']]  # Convert to Enum
            except KeyError:
                raise ValueError(f"Invalid state: {json_data['state']}")
        else:
            json_data['state'] = States.IDLE  # Default state

        # Validate and provide default values for optional fields
        json_data['videos'] = json_data.get('videos', [])
        if not isinstance(json_data['videos'], list):
            raise TypeError(f"Invalid type for videos: expected list, got {type(json_data['videos'])}")

        json_data['allowed_to_use'] = json_data.get('allowed_to_use', True)
        if not isinstance(json_data['allowed_to_use'], bool):
            raise TypeError(f"Invalid type for allowed_to_use: expected bool, got {type(json_data['allowed_to_use'])}")

        # Create and return the User object
        return User(**json_data)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except (TypeError, ValueError) as e:
        print(f"Error creating User from data: {e}")
        return None


class UserManager:
    def __init__(self):
        self.user_contexts = {}

    def get_user(self, user_id):
        if user_id in self.user_contexts:
            return self.user_contexts.get(user_id)

        # user_data = self.fetch_user_from_api(user_id)
        #
        # if user_data:
        #     user = self.create_user_from_data(user_data)  # Create user object
        #     self.user_contexts[user_id] = user  # Cache the user
        #     return user
        # else:
        return None

    def fetch_user_from_api(self, user_id):
        return None
        # Simulate API call to fetch user data
        # response = requests.get(f"{API_ENDPOINT}/user/{user_id}")
        # if response.status_code == 200:
        #     return response.json()
        # else:
        #     return None

    def add_video_to_user(self, user_id, video):
        user = self.get_user(user_id)
        user.videos.append(video)

    def get_user_videos(self, user_id):
        user = self.get_user(user_id)
        return user.videos


@dataclass
class User:
    user_id: int
    state: States = States.IDLE
    videos: List[Tuple[int, str]] = field(default_factory=list)  # is a list of video titles
    allowed_to_use: bool = True


if __name__ == '__main__':
    data = '{"user_id": 12345, "state": "IDLE", "videos": [[1, "video1.mp4"]], "allowed_to_use": true}'
    user = create_user_from_data(data)

    # Continue from data encoding/decoding and finish the usermanager