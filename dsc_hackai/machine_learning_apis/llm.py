from typing import List
from transformers import AutoModel, AutoTokenizer
from transformers import AutoModelForCausalLM, AutoProcessor, GenerationConfig
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

    def run_inference(self, image_path: str, question: str):
        # load the processor
        processor = AutoProcessor.from_pretrained(
            "allenai/Molmo-7B-D-0924",
            trust_remote_code=True,
            torch_dtype="auto",
            device_map="auto",
        )

        # load the model
        model = AutoModelForCausalLM.from_pretrained(
            "allenai/Molmo-7B-D-0924",
            trust_remote_code=True,
            torch_dtype="auto",
            device_map="auto",
        )

        model.save_pretrained("molmo_model")

        # process the image and text
        inputs = processor.process(
            images=[Image.open(image_path)],
            text=question,
        )

        # move inputs to the correct device and make a batch of size 1
        inputs = {k: v.to(model.device).unsqueeze(0) for k, v in inputs.items()}

        # generate output; maximum 200 new tokens; stop generation when <|endoftext|> is generated
        output = model.generate_from_batch(
            inputs,
            GenerationConfig(max_new_tokens=200, stop_strings="<|endoftext|>"),
            tokenizer=processor.tokenizer,
        )

        # only get generated tokens; decode them to text
        generated_tokens = output[0, inputs["input_ids"].size(1) :]
        generated_text = processor.tokenizer.decode(
            generated_tokens, skip_special_tokens=True
        )

    def inference_text(self):
        pass

    def inference_image(self, image_path: str, question: str):
        return self.run_inference(image_path, question)


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
