import whisperx

YOUR_HF_TOKEN = "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"


class whisperx_endpoint:
    def __init__(self):
        self.device = "cuda"
        self.batch_size = 16  # reduce if low on GPU mem
        compute_type = (
            "int8"  # change to "int8" if low on GPU mem (may reduce accuracy)
        )
        # 1. Transcribe with original whisper (batched)
        model_dir = "/tmp/whisparx"
        self.model = whisperx.load_model(
            "large-v2", self.device, compute_type=compute_type, download_root=model_dir, 
        )

    def inference(self, audio_file):
        audio = whisperx.load_audio(audio_file)
        result = self.model.transcribe(audio, batch_size=self.batch_size, max_new_tokens=512, )
        # print(result["segments"])  # before alignment

        # delete model if low on GPU resources
        # import gc; gc.collect(); torch.cuda.empty_cache(); del model

        # 2. Align whisper output
        model_a, metadata = whisperx.load_align_model(
            language_code=result["language"], device=self.device
        )
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            self.device,
            return_char_alignments=False,
        )

        # print(result["segments"])  # after alignment

        # delete model if low on GPU resources
        # import gc; gc.collect(); torch.cuda.empty_cache(); del model_a

        # 3. Assign speaker labels
        diarize_model = whisperx.DiarizationPipeline(
            use_auth_token=YOUR_HF_TOKEN, device=self.device
        )

        # add min/max number of speakers if known
        diarize_segments = diarize_model(audio)
        # diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

        result = whisperx.assign_word_speakers(diarize_segments, result)
        # print(diarize_segments)
        # print(result["segments"])  # segments are now assigned speaker IDs
        return result["segments"]
