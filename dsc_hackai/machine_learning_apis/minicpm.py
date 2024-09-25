import av
import numpy as np
from huggingface_hub import hf_hub_download
from typing import List
import time
import torch
from transformers import AutoProcessor, LlavaOnevisionForConditionalGeneration


class llava_next_endpoint:
    def __init__(self):
        self.model = LlavaOnevisionForConditionalGeneration.from_pretrained(
            "llava-hf/llava-onevision-qwen2-7b-ov-hf",
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self.processor = AutoProcessor.from_pretrained(
            "llava-hf/llava-onevision-qwen2-7b-ov-hf"
        )

    def read_video_pyav(self, container, indices):
        """
        Decode the video with PyAV decoder.
        Args:
            container (`av.container.input.InputContainer`): PyAV container.
            indices (`List[int]`): List of frame indices to decode.
        Returns:
            result (np.ndarray): np array of decoded frames of shape (num_frames, height, width, 3).
        """
        frames = []
        container.seek(0)
        start_index = indices[0]
        end_index = indices[-1]
        for i, frame in enumerate(container.decode(video=0)):
            if i > end_index:
                break
            if i >= start_index and i in indices:
                frames.append(frame)
        return np.stack([x.to_ndarray(format="rgb24") for x in frames])

    def inference(self, video_path, queries) -> List[str]:
        # Load the video as an np.array, sampling uniformly 8 frames (can sample more for longer videos, up to 32 frames)
        container = av.open(video_path)
        total_frames = container.streams.video[0].frames
        indices = np.arange(0, total_frames, total_frames / 8).astype(int)
        video = self.read_video_pyav(container, indices)

        responses = []
        query = "Tell me: " + ", ".join(queries)
        print(f"Asking for: {query} for {video_path}")
        # For videos we have to feed a "video" type instead of "image"
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "video"},
                    {"type": "text", "text": query},
                ],
            },
        ]
        start_time = time.time()
        prompt = self.processor.apply_chat_template(
            conversation, add_generation_prompt=True
        )
        inputs = self.processor(
            videos=list(video), text=prompt, return_tensors="pt"
        ).to("cuda:0", torch.float16)

        out = self.model.generate(**inputs, max_new_tokens=512)
        res = self.processor.batch_decode(
            out, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        end_time = time.time()
        delta_time = end_time - start_time
        print(res)
        print(f"Time spent: {delta_time:.2f}")
        responses.append(res)

        return responses


# Pillow==10.1.0
# torch==2.1.2
# torchvision==0.16.2
# transformers==4.40.0
# sentencepiece==0.1.99
# decord

import torch
from PIL import Image
from transformers import AutoModel, AutoTokenizer
from decord import VideoReader, cpu  # pip install decord

model = AutoModel.from_pretrained(
    "openbmb/MiniCPM-V-2_6",
    trust_remote_code=True,
    attn_implementation="sdpa",
    torch_dtype=torch.bfloat16,
)  # sdpa or flash_attention_2, no eager
model = model.eval().cuda()
tokenizer = AutoTokenizer.from_pretrained(
    "openbmb/MiniCPM-V-2_6", trust_remote_code=True
)

MAX_NUM_FRAMES = 64  # if cuda OOM set a smaller number


def encode_video(video_path):
    def uniform_sample(l, n):
        gap = len(l) / n
        idxs = [int(i * gap + gap / 2) for i in range(n)]
        return [l[i] for i in idxs]

    vr = VideoReader(video_path, ctx=cpu(0))
    sample_fps = round(vr.get_avg_fps() / 1)  # FPS
    frame_idx = [i for i in range(0, len(vr), sample_fps)]
    if len(frame_idx) > MAX_NUM_FRAMES:
        frame_idx = uniform_sample(frame_idx, MAX_NUM_FRAMES)
    frames = vr.get_batch(frame_idx).asnumpy()
    frames = [Image.fromarray(v.astype("uint8")) for v in frames]
    print("num frames:", len(frames))
    return frames


video_path = "video_test.mp4"
frames = encode_video(video_path)
question = "Describe the video"
msgs = [
    {"role": "user", "content": frames + [question]},
]

# Set decode params for video
params = {}
params["use_image_id"] = False
params["max_slice_nums"] = 2  # use 1 if cuda OOM and video resolution >  448*448

answer = model.chat(image=None, msgs=msgs, tokenizer=tokenizer, **params)
print(answer)
