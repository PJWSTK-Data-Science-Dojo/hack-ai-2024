# pip install accelerate
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


# from langchain_core.output_parsers import JsonOutputParser
# from langchain_core.prompts import PromptTemplate
# from langchain_openai import ChatOpenAI
# from pydantic import BaseModel, Field

# model = ChatOpenAI(temperature=0)


# # Define your desired data structure.
# class Joke(BaseModel):
#     setup: str = Field(description="question to set up a joke")
#     punchline: str = Field(description="answer to resolve the joke")


# # And a query intented to prompt a language model to populate the data structure.
# joke_query = "Tell me a joke."

# # Set up a parser + inject instructions into the prompt template.
# parser = JsonOutputParser(pydantic_object=Joke)

# prompt = PromptTemplate(
#     template="Answer the user query.\n{format_instructions}\n{query}\n",
#     input_variables=["query"],
#     partial_variables={"format_instructions": parser.get_format_instructions()},
# )

# chain = prompt | model | parser

# chain.invoke({"query": joke_query})


class gemma_endpoint:
    def __init__():
        self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-2-2b")
        self.model = AutoModelForCausalLM.from_pretrained(
            "google/gemma-2-2b",
            device_map="auto",
        )

    def inference(input_text):
        input_ids = self.tokenizer(input_text, return_tensors="pt").to("cuda")
        outputs = self.model.generate(**input_ids, max_new_tokens=32)
        return tokenizer.decode(outputs[0])
