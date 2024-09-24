import requests
import logging


class whisperx_endpoint:
    def inference(self, audio_file):
        res = requests.post(
            "http://jerboa-gpu:7006/v1/audio/transcriptions_whisperx",
            headers={"User-Agent": "dsc_hackai"},
            files={"file": open(audio_file, "rb")},
        )
        if res.status_code == 200:
            return res.json()["text"]
        else:
            logging.error(
                "Could not process audio " + str(res.status_code) + " " + res.text
            )
            return None
