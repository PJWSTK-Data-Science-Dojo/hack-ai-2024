import logging
from typing import List, Union
import json
from jsonschema import validate
import jsonschema
import requests
from utils import Video, User, States


# from the server i would like to have get_info(user_id), which returns json object. Based on which we can create
# User dataclass

# my_videos -> WAITING_FOR_VIDEO, user needs to choose video from the list, after info -> VIEWING_SUMMARY uses llm
# summarize + ctx(video link, or video file )  -> WAITING_FOR_PROCESSED_DATA (works only for new videos)
# summary ctx(id of the video) ->  WAITING_FOR_VIDEO after we got info -> VIEWING_SUMMARY which directly uses llm

# IDLE - User class has just been created.
# DOESN'T_EXISTS - We checked both the local cache and the db for the user info, but the user still doesn't exist, We won't waste resources for next checks.
# WAITING_FOR_VIDEO_ID - The User has used /my_videos command and is currently selecting the video for inference
# WAITING_FOR_PROCESSED_DATA - The User has chosen a video, and we are now waiting for the data from the server. This state is also used when a user requests a new video summary.
# VIEWING_SUMMARY - We have received the data from the server for the selected video. In this state, the user can ask questions to the LLM.
# VIEWING_SUMMARY - can only be interrupted with the stop command, i dont have ideas how to do it the other way


class UserManager:
    def __init__(self, logger: 'Logger', user_schema: dict, video_schema: dict):
        self.user_contexts = {}
        self.logging = logger
        self.user_schema = user_schema
        self.video_schema = video_schema
        self._using_llm = {}  # we store every user_id->process_id that currently llm

    def is_using_llm(self, user_id: int) -> bool:
        return user_id in self._using_llm

    def add_llm_user(self, user_id: int, process_id: int) -> bool:
        if user_id not in self._using_llm:
            self._using_llm[user_id] = process_id
            return True
        return False

    def delete_llm_user(self, user_id) -> bool:
        if user_id in self._using_llm:
            del self._using_llm[user_id]
            return True
        return False

    def get_llm_process(self, user_id: int) -> int:
        if not self.is_using_llm(user_id):
            return -1
        return self._using_llm.get(user_id)

    def validate_user_data(self, user_data) -> bool:
        """Validate the JSON data using the JSON schema."""
        try:
            validate(instance=user_data, schema=self.user_schema)
            logging.info("[validate_user_data] User data validation went okay")
            return True
        except jsonschema.exceptions.ValidationError as e:
            self.logging.error(f"[validate_user_data] Schema validation error: {e}")
            return False

    def create_user_from_data(self, data: Union[str, dict]) -> User | None:
        try:
            if isinstance(data, str):
                data = json.loads(data)

            if not self.validate_user_data(data):
                return None

            data['state'] = States.IDLE

            # Handle video if present
            videos_data = data.get('videos', [])
            validated_videos = []
            for video in videos_data:
                validated_videos.append(Video(**video))

            user = User(
                id=data['user_id'],
                state=data['state'],
                videos=validated_videos,
                allowed_to_use=data.get('allowed_to_use', True)
            )
            self.logging.info(f"[create_user_from_data] User(ID: {user.id}) was created successfully")
            return user

        except json.JSONDecodeError as e:
            self.logging.error(f"[create_user_from_data] Error decoding JSON: {e}")
            return None
        except (TypeError, ValueError) as e:
            self.logging.error(f"[create_user_from_data] Error creating User from data: {e}")
            return None
        except Exception as e:
            self.logging.error(f"[create_user_from_data] Unknown Error: {e}")

    def get_user(self, user_id: int) -> User:
        if user_id in self.user_contexts:
            self.logging.info(f"[get_user] User(ID: {user_id} received from cache)")
            return self.user_contexts.get(user_id)

        user = self.fetch_user_from_api(user_id)

        if user:
            self.logging.info(f"[get_user] User(ID: {user_id}) received from api")
            self.user_contexts[user_id] = user  # Cache the user
            return user

        # If the user is both not in the db nor in the cache, we create a User with DOESNT_EXISTS state
        user = User(id=user_id, state=States.DOESNT_EXISTS, allowed_to_use=False)
        self.logging.warning(f"[get_user] User(ID: {user_id}) Doesn't exists. Creating an empty object")
        self.user_contexts[user_id] = user
        return user

    def fetch_user_from_api(self, user_id: int) -> User | None:
        # query api.
        data = '{"user_id":' + str(
            user_id) + ',"videos": [{"title": "Sample Video","process_id": "123","stage": "started_initialized"},{"title": "Sample Video2","process_id": "1234","stage": "started_initialized", "bullet_points": ["bullet1","bullet2","bullet3"]},{"title": "Sample Video3","process_id": "1234","stage": "started_initialized"},{"title": "Sample Video4","process_id": "1234","stage": "started_initialized"},{"title": "Sample Video5","process_id": "1234","stage": "started_initialized"},{"title": "Sample Video6","process_id": "1234","stage": "started_initialized"}],"allowed_to_use": true}'

        user = self.create_user_from_data(data)

        if not user:
            self.logging.error(f"[fetch_user_from_api] Failed to validate user data {user_id}")
            return None

        return user
        # Simulate API call to fetch user data
        # response = requests.get(f"{API_ENDPOINT}/user/{user_id}")
        # if response.status_code == 200:
        #     return response.json()
        # else:
        #     return None

    def validate_video_data(self, video_data: Union[dict, str]) -> bool:
        """Validate the structure of video data before adding it to the user."""
        try:
            if isinstance(video_data, str):
                video_data = json.loads(video_data)

            validate(instance=video_data, schema=self.video_schema)
            self.logging.info("[validate_video_data] Video data validation completed")
            return True
        except jsonschema.exceptions.ValidationError as e:
            self.logging.error(f"[validate_video_data] Schema validation error: {e}")
            return False

    def add_video_to_user(self, user_id: int, video_data: Union[str, dict]) -> bool:
        if not self.validate_video_data(video_data):
            self.logging.error(f"[add_video_to_user] Invalid video data for User(ID: {user_id}).")
            return

        user = self.get_user(user_id)

        if user.state == States.DOESNT_EXISTS:
            self.logging.warning(f"[add_video_to_user] Since User(ID: {user_id}) doesn't exists, can`t add video data.")
            return False

        try:
            video = Video(**video_data)
            user.videos.append(video)
            self.logging.info(f"[add_video_to_user] Video '{video.title}' added to User(ID: {user_id}).")
            return True
        except (TypeError, ValueError) as e:
            self.logging.error(f"[add_video_to_user] Error creating Video object for User(ID: {user_id}): {e}")
            return False


# def test_1():
#     from settings import get_logger, user_schema, video_scheme
#     logger = get_logger()
#     usm = UserManager(logger, user_schema, video_scheme)
#     string_data_user_str = '{"user_id": 12345,"videos": [{"title": "Sample Video","process_id": "123","stage": "VIEWING"}],"allowed_to_use": true}'
#     string_data_user_dict = {"user_id": 12345,
#                              "videos": [{"title": "Sample Video", "process_id": "123", "stage": "VIEWING"}],
#                              "allowed_to_use": True}
#     user = usm.create_user_from_data(string_data_user_dict)
#     print(user)
#     video_data_str = '{"title": "Sample Video","process_id": "1234","stage": "VIEWING"}'
#     video_data_dict = {"title": "Sample Video", "process_id": "1234", "stage": "VIEWING"}
#     usm.add_video_to_user(user.id, video_data_str)
#     print(usm.validate_video_data(video_data_dict))
#
#
# def test_2():
#     from settings import get_logger, user_schema, video_scheme
#     logger = get_logger()
#     usm = UserManager(logger, user_schema, video_scheme)
#     user_id = 302459865081577473
#     user = usm.get_user(user_id)
#     print(user)
#     print(user.videos)


if __name__ == '__main__':
    from settings import get_logger, user_schema, video_scheme
    usm = UserManager(get_logger("bot"), user_schema, video_scheme)
    print(usm.add_llm_user(123, 1))
    print(usm.is_using_llm(123))
    print(usm.delete_llm_user(123))
    print(usm.is_using_llm(123))
    # test_1()
    # test_2()
