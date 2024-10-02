from typing import List
from transformers import AutoModel, AutoTokenizer
import base64
from io import BytesIO
from PIL import Image

import torch
import ollama


def convert_to_base64(pil_image):
    """
    Convert PIL images to Base64 encoded strings

    :param pil_image: PIL image
    :return: Base64 string
    """
    buffered = BytesIO()
    pil_image.save(buffered, format="JPEG")  # You can change the format if needed
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


class llm_endpoint:
    def __init__(self):
        pass

    def run_minicpmv_generate(self, question: str, image_path: str):
        num_device = 0

        context_length = 2048  # Adjust this value based on MiniCPM-V's requirements
        model_name = "openbmb/MiniCPM-V-2_6"
        model = AutoModel.from_pretrained(
            "openbmb/MiniCPM-V", trust_remote_code=True, torch_dtype=torch.bfloat16
        )
        # For Nvidia GPUs support BF16 (like A100, H100, RTX3090)
        model = model.to(device="cuda", dtype=torch.bfloat16)
        # For Nvidia GPUs do NOT support BF16 (like V100, T4, RTX2080)
        # model = model.to(device='cuda', dtype=torch.float16)
        # For Mac with MPS (Apple silicon or AMD GPUs).
        # Run with `PYTORCH_ENABLE_MPS_FALLBACK=1 python test.py`
        # model = model.to(device='mps', dtype=torch.float16)

        tokenizer = AutoTokenizer.from_pretrained(
            "openbmb/MiniCPM-V", trust_remote_code=True
        )
        model.eval()
        image = Image.open(image_path).convert("RGB")
        msgs = [{"role": "user", "content": question}]

        res, context, _ = model.chat(
            image=image,
            msgs=msgs,
            context=None,
            tokenizer=tokenizer,
            sampling=True,
            temperature=0.7,
        )
        result = res
        return result

    def inference_text(self):
        pass

    def inference_image(self, image_path: str, question: str):
        return self.run_minicpmv_generate(question)


class llm_endpoint_test:
    def __init__(self):
        self.ollama_client = ollama.Client(host="192.168.1.42:11435")

    def inference_text(self):
        pass

    def inference_image(self, image_path: str, question: str):
        res = self.ollama_client.generate(
            model="minicpm-v:8b",
            options={"temperature": 0.07},
            images=[convert_to_base64(Image.open(image_path))],
            prompt=question
            + ". Respond with up to 3 senteces, do not make any additional remarks.",
        )["response"]
        return res
