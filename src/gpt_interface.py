import logging
import os
import time
from typing import Any, Optional
from dotenv import load_dotenv
import tiktoken
from openai import OpenAI, APIError, RateLimitError  # Imports spécifiques

load_dotenv()
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENAI_API_KEY"),
)

# Set the organization
#openai.organization = os.getenv("OPENAI_ORGANIZATION_ID")
#prompt for Negation, Paraphrasing, and Bayes’ rule consistency check
DEFAULT_SYSTEM_PROMPT = (
   "The user needs help on a few prediction market questions. You should always output a single best"
   "probability estimate, without any intervals. It is important that you do not output the probability outright."
   "Rather, you should consider multiple views, along with the intermediate estimates; and only then"
   "produce the final numerical answer in the last line, like this: [Answer] 0.5"
)

def chat_message(role: str, content: str):
    return {"role": role, "content": content}


def gpt_query(
    prompt: str,
    system_prompt: Optional[str] = None,
    model_name: str = "gpt-3.5-turbo",
    max_tokens: int = 200,
    temperature: float = 0.0,
    **kwargs: Any,
):
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    num_seconds_to_wait_max = 300

    if "gpt-3.5" in model_name or "gpt-4" in model_name:
        messages = [
            chat_message("system", system_prompt),
            chat_message("user", prompt),
        ]

        time_waited = 0
        wait_time_seconds = 5
        while time_waited < num_seconds_to_wait_max:
            try:
                completion = client.chat.completions.create(
                    extra_body={},
                    model=model_name,
                    messages=messages,
                    temperature=temperature
                )
                
                break
            except APIError as e:
                logging.info(f"APIError: {e}. Waiting {wait_time_seconds} seconds...")
                time.sleep(wait_time_seconds)
                time_waited += wait_time_seconds
            except RateLimitError as e:
                logging.info(f"RateLimitError: {e}. Waiting {wait_time_seconds} seconds...")
                time.sleep(wait_time_seconds)
                time_waited += wait_time_seconds
                wait_time_seconds *= 2
        else:
            raise TimeoutError(
                f"Timed out waiting for {model_name} to respond after"
                f" {num_seconds_to_wait_max} seconds."
            )

        return completion.choices[0].message.content

    else:
        raise NotImplementedError
