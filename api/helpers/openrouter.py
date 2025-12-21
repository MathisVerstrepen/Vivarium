from openai import (
    OpenAI,
    APIConnectionError,
    RateLimitError,
    APIError,
    InternalServerError,
)
from openai.types.chat import ChatCompletionMessageParam
import os
import json
import time
import random
from typing import cast, Type, TypeVar, Any
from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# --- RETRY CONFIGURATION ---
MAX_RETRIES = 5
BASE_DELAY_SECONDS = 2.0


def _sleep_with_backoff(attempt: int):
    """
    Sleeps for an exponential amount of time with jitter.
    Formula: base * (2^attempt) + random_jitter
    """
    sleep_time = (BASE_DELAY_SECONDS * (2**attempt)) + (random.random() * 1.0)
    sleep_time = min(sleep_time, 60.0)
    print(
        f"[OpenRouter] Request failed. Retrying in {sleep_time:.2f}s... (Attempt {attempt + 1}/{MAX_RETRIES})"
    )
    time.sleep(sleep_time)


def run_llm(user_prompt: str, model: str, system_prompt: str = "") -> str:
    messages: list[ChatCompletionMessageParam] = []
    if system_prompt:
        messages.append(
            cast(
                ChatCompletionMessageParam, {"role": "system", "content": system_prompt}
            )
        )

    messages.append(
        cast(ChatCompletionMessageParam, {"role": "user", "content": user_prompt})
    )

    last_exception: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
            )

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("No content in response from LLM")
            return content

        except (
            APIConnectionError,
            RateLimitError,
            InternalServerError,
            APIError,
        ) as e:
            last_exception = e
            print(f"[OpenRouter Error]: {e}")
            if attempt < MAX_RETRIES - 1:
                _sleep_with_backoff(attempt)
            else:
                print("[OpenRouter] Max retries reached.")

    if last_exception:
        raise last_exception
    raise RuntimeError("Unknown error in run_llm retry loop")


T = TypeVar("T", bound=BaseModel)


def run_llm_with_schema(
    user_prompt: str, model: str, schema: Type[T], system_prompt: str = ""
) -> T:
    messages: list[ChatCompletionMessageParam] = []
    if system_prompt:
        messages.append(
            cast(
                ChatCompletionMessageParam, {"role": "system", "content": system_prompt}
            )
        )

    messages.append(
        cast(ChatCompletionMessageParam, {"role": "user", "content": user_prompt})
    )

    last_exception: Exception | None = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema.__name__,
                        "strict": True,
                        "schema": schema.model_json_schema(),
                    },
                },
            )

            content = response.choices[0].message.content
            if content is None:
                raise ValueError("No content in response")
            return schema.model_validate_json(content)

        except (
            APIConnectionError,
            RateLimitError,
            InternalServerError,
            APIError,
        ) as e:
            last_exception = e
            print(f"[OpenRouter Error]: {e}")
            if attempt < MAX_RETRIES - 1:
                _sleep_with_backoff(attempt)

        except Exception as e:
            last_exception = e
            print(f"[OpenRouter Validation/Schema Error]: {e}")
            if attempt < MAX_RETRIES - 1:
                _sleep_with_backoff(attempt)

    if last_exception:
        raise last_exception
    raise RuntimeError("Unknown error in run_llm_with_schema retry loop")


def generate_image(
    prompt: str,
    model: str,
    input_image_url: str | None = None,
    aspect_ratio: str | None = None,
) -> list[str]:
    """
    Generates or edits images using OpenRouter's image generation models.
    Includes retry logic.
    """
    messages: list[ChatCompletionMessageParam] = []

    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]

    if input_image_url:
        content.append({"type": "image_url", "image_url": {"url": input_image_url}})

    messages.append(
        cast(ChatCompletionMessageParam, {"role": "user", "content": content})
    )

    extra_body: dict[str, Any] = {
        "modalities": ["image", "text"],
    }

    if aspect_ratio:
        extra_body["image_config"] = {"aspect_ratio": aspect_ratio}

    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.with_raw_response.create(
                model=model,
                messages=messages,
                extra_body=extra_body,
            )

            try:
                response_data = json.loads(response.http_response.content)
            except json.JSONDecodeError:
                raise ValueError("Failed to decode response from API")

            choices = response_data.get("choices", [])
            if not choices:
                raise ValueError("No choices returned from API")

            message = choices[0].get("message", {})

            images = message.get("images", [])

            if not images:
                text_content = message.get("content", "")
                raise ValueError(f"No images generated. Model response: {text_content}")

            return [img["image_url"]["url"] for img in images]

        except (
            APIConnectionError,
            RateLimitError,
            InternalServerError,
            APIError,
        ) as e:
            last_exception = e
            print(f"[OpenRouter Image Gen Error]: {e}")
            if attempt < MAX_RETRIES - 1:
                _sleep_with_backoff(attempt)

    if last_exception:
        raise last_exception
    raise RuntimeError("Unknown error in generate_image retry loop")
