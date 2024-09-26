import requests
import logging
import whisperx
import os
import torch


class whisperx_transcriber:
    def __init__(self):
        self.device = "cuda"
        self.hf_token = os.getenv("HF_TOKEN", None)
        self.batch_size = 16
        self.compute_type = "int8"
        self.model_a = None
        logging.info("Loading WhisperX model")
        self.model = whisperx.load_model(
            "small",
            self.device,
            compute_type=self.compute_type,
            download_root="/project/models/",
        )
        logging.info("Loaded WhisperX model")

        if self.hf_token:
            logging.info("Loading Diarize model")
            self.diarize_model = whisperx.DiarizationPipeline(
                model_name="pyannote/speaker-diarization@2.1",
                use_auth_token=self.hf_token,
                device=self.device,
            )
            logging.info("Loaded Diarize model")
        else:
            logging.warning("No HF_TOKEN env - diarize model will be not accessible!")

    def clear_cache(self):
        import gc

        gc.collect()
        torch.cuda.empty_cache()
        del self.model_a

    def run_transcription(self, audio_file):
        try:
            audio = whisperx.load_audio(audio_file)

            # 1. Transcribe audio with whisper
            result = self.model.transcribe(audio, batch_size=self.batch_size)
            if result is None:
                return None

            # 2. Align whisper output
            self.model_a, metadata = whisperx.load_align_model(
                language_code=result["language"], device=self.device
            )

            result = whisperx.align(
                result["segments"],
                self.model_a,
                metadata,
                audio,
                self.device,
                return_char_alignments=False,
            )
            return result, audio
        except Exception as e:
            self.clear_cache()
            return None, None

    def transcribe_openai(self, audio_file: str = None):
        result, audio = self.run_transcription(audio_file)
        if result:
            all_text = ""
            for mini_trans in result["segments"]:
                all_text += mini_trans["text"]
            return all_text
        return ""

    def transcibe_whisperx(self, audio_file: str = None):
        result, audio = self.run_transcription(audio_file)
        if result:
            if self.diarize_model:
                # Adding speakers IDs
                diarize_segments = self.diarize_model(audio)
                try:
                    result = whisperx.assign_word_speakers(diarize_segments, result)
                    self.clear_cache()
                    return result
                except Exception as e:
                    self.clear_cache()
                    return None
            else:
                self.clear_cache()
                return None
        else:
            self.clear_cache()
            return ""


class whisperx_endpoint:
    def __init__(self):
        pass

    def inference(self, audio_file):
        wt = whisperx_transcriber()
        transcription_response = wt.transcibe_whisperx(audio_file)
        return transcription_response

class whisperx_endpoint_test:
    def __init__(self):
        pass

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
