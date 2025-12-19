import openai
import time
import random
import os
import base64
from openai import OpenAI
import time
import json
import pathlib


# Read and cache once
_CFG_PATH = pathlib.Path(__file__).with_name("api_config.json")
with _CFG_PATH.open("r", encoding="utf-8") as _f:
    _CFG = json.load(_f)


def cfg(svc: str, key: str, default=None):
    return os.getenv(f"{svc}_{key}".upper(), _CFG.get(svc, {}).get(key, default))


def generate_log_id():
    """Generate a log ID with 'tkb' prefix and current timestamp."""
    return f"tkb{int(time.time() * 1000)}"


def request_claude(prompt, log_id=None, max_tokens=16384, max_retries=3):
    base_url = cfg("claude", "base_url")
    api_key = cfg("claude", "api_key")
    client = OpenAI(base_url=base_url, api_key=api_key)

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    retry_count = 0
    while retry_count < max_retries:
        try:
            response = client.chat.completions.create(
                model="claude-4-opus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)


def request_claude_token(prompt, log_id=None, max_tokens=10000, max_retries=3):
    base_url = cfg("claude", "base_url")
    api_key = cfg("claude", "api_key")
    client = OpenAI(base_url=base_url, api_key=api_key)

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}
    usage_info = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model="claude-4-opus",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )
            # --- MODIFIED: token usage ---
            if completion.usage:
                usage_info["prompt_tokens"] = completion.usage.prompt_tokens
                usage_info["completion_tokens"] = completion.usage.completion_tokens
                usage_info["total_tokens"] = completion.usage.total_tokens
            return completion, usage_info

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)

    return None, usage_info


def request_gemini_with_video(prompt: str, video_path: str, log_id=None, max_tokens: int = 10000, max_retries: int = 3):
    """
    Makes a multimodal request to the Gemini-2.5 model using video + text.

    Args:
        prompt (str): The user instruction, e.g., "Please evaluate and suggest improvements for this educational animation."
        video_path (str): Local path to the video file (MP4 preferred, <20MB recommended).
        log_id (str, optional): Tracking ID
        max_tokens (int): Max response token length
        max_retries (int): Max retry attempts

    Returns:
        dict: The Gemini model response
    """
    base_url = cfg("gemini", "base_url")
    api_version = cfg("gemini", "api_version")
    api_key = cfg("gemini", "api_key")
    model_name = cfg("gemini", "model")

    client = OpenAI(
        azure_endpoint=base_url,
        api_key=api_key,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    # Load and base64-encode video
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    with open(video_path, "rb") as f:
        video_bytes = f.read()

    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
    data_url = f"data:video/mp4;base64,{video_base64}"

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}, "media_type": "video/mp4"},
                        ],
                    }
                ],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )
            return completion

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")
            delay = (2**retry_count) * 0.2 + random.random() * 0.2
            print(f"Retry {retry_count}/{max_retries} after error: {e}, waiting {delay:.2f}s...")
            time.sleep(delay)


def request_gemini_video_img(
    prompt: str, video_path: str, image_path: str, log_id=None, max_tokens: int = 10000, max_retries: int = 3
):
    """
    Makes a multimodal request to the Gemini-2.5 model using video & ref img + text.

    Args:
        prompt (str): The user instruction, e.g., "Please evaluate and suggest improvements for this educational animation."
        video_path (str): Local path to the video file (MP4 preferred, <20MB recommended).
        log_id (str, optional): Tracking ID
        max_tokens (int): Max response token length
        max_retries (int): Max retry attempts

    Returns:
        dict: The Gemini model response
    """
    base_url = cfg("gemini", "base_url")
    api_version = cfg("gemini", "api_version")
    api_key = cfg("gemini", "api_key")
    model_name = cfg("gemini", "model")

    client = OpenAI(
        azure_endpoint=base_url,
        api_key=api_key,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    # Load and base64-encode video
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
    video_data_url = f"data:video/mp4;base64,{video_base64}"

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    image_data_url = f"data:image/png;base64,{base64_image}"

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": video_data_url, "detail": "high"},
                                "media_type": "video/mp4",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_data_url, "detail": "high"},
                                "media_type": "image/png",
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )
            return completion

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")
            delay = (2**retry_count) * 0.2 + random.random() * 0.2
            print(f"Retry {retry_count}/{max_retries} after error: {e}, waiting {delay:.2f}s...")
            time.sleep(delay)
    return None


def request_gemini_video_img_token(
    prompt: str, video_path: str, image_path: str, log_id=None, max_tokens: int = 10000, max_retries: int = 3
):
    """
    Makes a multimodal request to the Gemini-2.5 model using video & ref img + text.

    Args:
        prompt (str): The user instruction, e.g., "Please evaluate and suggest improvements for this educational animation."
        video_path (str): Local path to the video file (MP4 preferred, <20MB recommended).
        log_id (str, optional): Tracking ID
        max_tokens (int): Max response token length
        max_retries (int): Max retry attempts

    Returns:
        dict: The Gemini model response
    """
    base_url = cfg("gemini", "base_url")
    api_version = cfg("gemini", "api_version")
    api_key = cfg("gemini", "api_key")
    model_name = cfg("gemini", "model")

    client = OpenAI(
        azure_endpoint=base_url,
        api_key=api_key,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    usage_info = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    # Load and base64-encode video
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
    video_data_url = f"data:video/mp4;base64,{video_base64}"

    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    image_data_url = f"data:image/png;base64,{base64_image}"

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": video_data_url, "detail": "high"},
                                "media_type": "video/mp4",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_data_url, "detail": "high"},
                                "media_type": "image/png",
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )
            # return completion

            if completion.usage:
                usage_info["prompt_tokens"] = completion.usage.prompt_tokens
                usage_info["completion_tokens"] = completion.usage.completion_tokens
                usage_info["total_tokens"] = completion.usage.total_tokens
            return completion, usage_info

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")
            delay = (2**retry_count) * 0.2 + random.random() * 0.2
            print(f"Retry {retry_count}/{max_retries} after error: {e}, waiting {delay:.2f}s...")
            time.sleep(delay)
    return None, usage_info


def request_gemini(prompt, log_id=None, max_tokens=8000, max_retries=3):
    """
    Makes a request to the gemini-2.5-pro-preview-03-25 model with retry functionality.

    Args:
        prompt (str): The text prompt to send to the model
        log_id (str, optional): The log ID for tracking requests, defaults to tkb+timestamp
        max_tokens (int, optional): Maximum tokens for response, default 8000
        max_retries (int, optional): Maximum number of retry attempts, default 3

    Returns:
        dict: The model's response
    """
    base_url = cfg("gemini", "base_url")
    api_version = cfg("gemini", "api_version")
    api_key = cfg("gemini", "api_key")
    model_name = cfg("gemini", "model")

    client = OpenAI(
        azure_endpoint=base_url,
        api_key=api_key,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )
            return completion
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)


def request_gemini_token(prompt, log_id=None, max_tokens=8000, max_retries=3):
    """
    Makes a request to the gemini-2.5-pro-preview-03-25 model with retry functionality.

    Args:
        prompt (str): The text prompt to send to the model
        log_id (str, optional): The log ID for tracking requests, defaults to tkb+timestamp
        max_tokens (int, optional): Maximum tokens for response, default 8000
        max_retries (int, optional): Maximum number of retry attempts, default 3

    Returns:
        dict: The model's response
    """

    base_url = cfg("gemini", "base_url")
    api_version = cfg("gemini", "api_version")
    api_key = cfg("gemini", "api_key")
    model_name = cfg("gemini", "model")

    client = OpenAI(
        azure_endpoint=base_url,
        api_key=api_key,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    usage_info = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )

            if completion.usage:
                usage_info["prompt_tokens"] = completion.usage.prompt_tokens
                usage_info["completion_tokens"] = completion.usage.completion_tokens
                usage_info["total_tokens"] = completion.usage.total_tokens
            return completion, usage_info

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)
    return None, usage_info


def request_gpt4o(prompt, log_id=None, max_tokens=8000, max_retries=3):
    """
    Makes a request to the gpt-4o-2024-11-20 model with retry functionality.

    Args:
        prompt (str): The text prompt to send to the model
        log_id (str, optional): The log ID for tracking requests, defaults to tkb+timestamp
        max_tokens (int, optional): Maximum tokens for response, default 8000
        max_retries (int, optional): Maximum number of retry attempts, default 3

    Returns:
        dict: The model's response
    """

    base_url = cfg("gpt4o", "base_url")
    api_version = cfg("gpt4o", "api_version")
    ak = cfg("gpt4o", "api_key")
    model_name = cfg("gpt4o", "model")

    client = openai.AzureOpenAI(
        azure_endpoint=base_url,
        api_version=api_version,
        api_key=ak,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )
            return completion.choices[0].message.content
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)


def request_gpt4o_token(prompt, log_id=None, max_tokens=8000, max_retries=3):
    """
    Makes a request to the gpt-4o model with retry functionality.
    Args:
        prompt (str): The text prompt to send to the model
        log_id (str, optional): The log ID for tracking requests, defaults to tkb+timestamp
        max_tokens (int, optional): Maximum tokens for response, default 8000
        max_retries (int, optional): Maximum number of retry attempts, default 3
    Returns:
        dict: The model's response
    """
    base_url = cfg("gpt4o", "base_url")
    ak = cfg("gpt4o", "api_key")
    model_name = cfg("gpt4o", "model")

    # --- MODIFIED: Use standard OpenAI client & 5 min timeout ---
    client = OpenAI(
        base_url=base_url,
        api_key=ak,
        timeout=300.0,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    usage_info = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                timeout=300.0
            )

            if completion.usage:
                usage_info["prompt_tokens"] = completion.usage.prompt_tokens
                usage_info["completion_tokens"] = completion.usage.completion_tokens
                usage_info["total_tokens"] = completion.usage.total_tokens
            return completion, usage_info

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Failed after {max_retries} attempts. Last error: {str(e)}")
                return None, usage_info

            # Exponential backoff with jitter
            delay = (2**retry_count) * 1.0 + (random.random() * 0.5)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)
    return None, usage_info


def request_o4mini(prompt, log_id=None, max_tokens=8000, max_retries=3, thinking=False):
    """
    Makes a request to the o4-mini-2025-04-16 model with retry functionality.

    Args:
        prompt (str): The text prompt to send to the model
        log_id (str, optional): The log ID for tracking requests, defaults to tkb+timestamp
        max_tokens (int, optional): Maximum tokens for response, default 8000
        max_retries (int, optional): Maximum number of retry attempts, default 3
        thinking (bool, optional): Whether to enable thinking mode, default False

    Returns:
        dict: The model's response
    """
    base_url = cfg("gpt4omini", "base_url")
    api_version = cfg("gpt4omini", "api_version")
    ak = cfg("gpt4omini", "api_key")
    model_name = cfg("gpt4omini", "model")

    client = openai.AzureOpenAI(
        azure_endpoint=base_url,
        api_version=api_version,
        api_key=ak,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    # Configure extra_body for thinking if enabled
    extra_body = None
    if thinking:
        extra_body = {"thinking": {"type": "enabled", "budget_tokens": 2000}}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                extra_body=extra_body,
            )
            return completion
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)


def request_o4mini_token(prompt, log_id=None, max_tokens=8000, max_retries=3, thinking=False):
    """
    Makes a request to the o4-mini-2025-04-16 model with retry functionality.

    Args:
        prompt (str): The text prompt to send to the model
        log_id (str, optional): The log ID for tracking requests, defaults to tkb+timestamp
        max_tokens (int, optional): Maximum tokens for response, default 8000
        max_retries (int, optional): Maximum number of retry attempts, default 3
        thinking (bool, optional): Whether to enable thinking mode, default False

    Returns:
        dict: The model's response
    """
    base_url = cfg("gpt4omini", "base_url")
    api_version = cfg("gpt4omini", "api_version")
    ak = cfg("gpt4omini", "api_key")
    model_name = cfg("gpt4omini", "model")

    client = openai.AzureOpenAI(
        azure_endpoint=base_url,
        api_version=api_version,
        api_key=ak,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    usage_info = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    # Configure extra_body for thinking if enabled
    extra_body = None
    if thinking:
        extra_body = {"thinking": {"type": "enabled", "budget_tokens": 2000}}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                extra_body=extra_body,
            )

            if completion.usage:
                usage_info["prompt_tokens"] = completion.usage.prompt_tokens
                usage_info["completion_tokens"] = completion.usage.completion_tokens
                usage_info["total_tokens"] = completion.usage.total_tokens
            return completion, usage_info

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)
    return None, usage_info


def request_gpt5(prompt, log_id=None, max_tokens=1000, max_retries=3):
    """
    Makes a request to the gpt-5 model via standard OpenAI client.
    (No token usage return, just the completion object)
    """
    # 1. 读取配置
    base_url = cfg("gpt5", "base_url")
    ak = cfg("gpt5", "api_key")
    model_name = cfg("gpt5", "model")

    # 2. ✅ 修正点：改为标准 OpenAI 客户端
    client = OpenAI(
        base_url=base_url,
        api_key=ak,
        timeout=300.0,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                timeout=300.0
            )
            return completion
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)

def request_gpt5_token(prompt, log_id=None, max_tokens=1000, max_retries=3):
    """
    Makes a request to the gpt-5 model via standard OpenAI client.
    """
    # 1. 读取配置
    base_url = cfg("gpt5", "base_url")
    ak = cfg("gpt5", "api_key")
    model_name = cfg("gpt5", "model")

    # 2. ✅ 修正点：标准 OpenAI 客户端使用 base_url，而不是 azure_endpoint
    client = OpenAI(
        base_url=base_url,  # 👈 注意这里改成了 base_url
        api_key=ak,
        timeout=300.0,      # 设置 5 分钟超时
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}
    usage_info = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                timeout=300.0
            )

            if completion.usage:
                usage_info["prompt_tokens"] = completion.usage.prompt_tokens
                usage_info["completion_tokens"] = completion.usage.completion_tokens
                usage_info["total_tokens"] = completion.usage.total_tokens
            return completion, usage_info

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Failed after {max_retries} attempts. Last error: {str(e)}")
                return None, usage_info

            delay = (2**retry_count) * 1.0 + (random.random() * 0.5)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)
    return None, usage_info

def request_gpt5_img(prompt, image_path=None, log_id=None, max_tokens=1000, max_retries=3):
    """
    Makes a request to the gpt-5 model with optional image input.
    Uses standard OpenAI client.
    """
    # 1. 读取配置
    base_url = cfg("gpt5", "base_url")
    ak = cfg("gpt5", "api_key")
    model_name = cfg("gpt5", "model")

    # 2. 初始化标准客户端
    client = OpenAI(
        base_url=base_url,
        api_key=ak,
        timeout=300.0,
    )
    
    if log_id is None:
        log_id = generate_log_id()
    
    # 部分中转商可能不支持自定义 header，如果报错可注释掉
    extra_headers = {"X-TT-LOGID": log_id}

    # 3. 构建消息体
    if image_path:
        # 检查图片是否存在
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # 读取并转为 Base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url", 
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high" # 强制高清模式
                        }
                    },
                ],
            }
        ]
    else:
        # 如果没有图片，就当普通对话处理
        messages = [{"role": "user", "content": prompt}]

    # 4. 发送请求
    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                timeout=300.0
            )
            return completion
            
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")
            
            delay = (2**retry_count) * 1.0 + (random.random() * 0.5)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)

def request_gpt41(prompt, log_id=None, max_tokens=1000, max_retries=3):
    """
    Makes a request to the gpt-4.1-2025-04-14 model with retry functionality.

    Args:
        prompt (str): The text prompt to send to the model
        log_id (str, optional): The log ID for tracking requests, defaults to tkb+timestamp
        max_tokens (int, optional): Maximum tokens for response, default 1000
        max_retries (int, optional): Maximum number of retry attempts, default 3

    Returns:
        dict: The model's response
    """
    base_url = cfg("gpt41", "base_url")
    api_version = cfg("gpt41", "api_version")
    api_key = cfg("gpt41", "api_key")
    model_name = cfg("gpt41", "model")

    client = openai.AzureOpenAI(
        azure_endpoint=base_url,
        api_version=api_version,
        api_key=api_key,
    )

    if log_id is None:
        log_id = generate_log_id()

    extra_headers = {"X-TT-LOGID": log_id}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )
            return completion
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")

            # Exponential backoff with jitter
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)


def request_gpt41_token(prompt, log_id=None, max_tokens=1000, max_retries=3):
    # 读取配置
    base_url = cfg("gpt41", "base_url")
    ak = cfg("gpt41", "api_key")
    model_name = cfg("gpt41", "model")

    # --- MODIFIED: Use standard OpenAI client & 5 min timeout ---
    client = OpenAI(
        base_url=base_url,
        api_key=ak,
        timeout=300.0,
    )
    # ------------------------------------

    if log_id is None:
        log_id = generate_log_id()

    # 某些中转站不支持自定义 header，如果报错可以把 extra_headers 删掉
    extra_headers = {"X-TT-LOGID": log_id} 
    usage_info = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                extra_headers=extra_headers,
                timeout=300.0
            )

            if completion.usage:
                usage_info["prompt_tokens"] = completion.usage.prompt_tokens
                usage_info["completion_tokens"] = completion.usage.completion_tokens
                usage_info["total_tokens"] = completion.usage.total_tokens
            return completion, usage_info

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                # 即使失败也返回，以免程序崩溃
                print(f"Failed after {max_retries} attempts. Last error: {str(e)}")
                return None, usage_info
            
            # 增加重试等待时间
            delay = (2**retry_count) * 1.0 + (random.random() * 0.5)
            print(f"Retry {retry_count} error: {str(e)}. Waiting {delay:.2f}s...")
            time.sleep(delay)

    return None, usage_info


def request_gpt41_img(prompt, image_path=None, log_id=None, max_tokens=1000, max_retries=3):
    """
    Makes a request to the gpt-4.1-2025-04-14 model with optional image input and retry functionality.
    Args:
        prompt (str): The text prompt to send to the model
        image_path (str, optional): Absolute path to an image file to include
        log_id (str, optional): The log ID for tracking requests, defaults to tkb+timestamp
        max_tokens (int, optional): Maximum tokens for response, default 1000
        max_retries (int, optional): Maximum number of retry attempts, default 3
    Returns:
        dict: The model's response
    """
    base_url = cfg("gpt41", "base_url")
    api_version = cfg("gpt41", "api_version")
    ak = cfg("gpt41", "api_key")
    model_name = cfg("gpt41", "model")

    client = openai.AzureOpenAI(
        azure_endpoint=base_url,
        api_version=api_version,
        api_key=ak,
    )
    if log_id is None:
        log_id = generate_log_id()
    extra_headers = {"X-TT-LOGID": log_id}

    if image_path:
        # 检查图片路径是否存在
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                ],
            }
        ]

    else:
        messages = [{"role": "user", "content": prompt}]
    retry_count = 0
    while retry_count < max_retries:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                extra_headers=extra_headers,
            )
            return completion
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} attempts. Last error: {str(e)}")
            delay = (2**retry_count) * 0.1 + (random.random() * 0.1)
            print(
                f"Request failed with error: {str(e)}. Retrying in {delay:.2f} seconds... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(delay)


if __name__ == "__main__":

    # Gemini
    # response_gemini = request_gemini("上海天气怎么样？")
    # print(response_gemini.model_dump_json())

    # # GPT-4o
    # response_gpt4o = request_gpt4o("上海天气怎么样？")
    # print(response_gpt4o)

    # # o4-mini
    # response_o4mini = request_o4mini("上海天气怎么样？")
    # print(response_o4mini.model_dump_json())

    # # GPT-4.1
    #response_gpt41 = request_gpt41("上海天气怎么样？")
    #print(response_gpt41.model_dump_json())

    # GPT-5
    # response_gpt5 = request_gpt5("新加坡天气怎么样？")
    # print(response_gpt5.model_dump_json())

    # # Claude
    # response_claude = request_claude_token("新加坡天气怎么样？")
    # print(response_claude)
    print("🚀 正在测试 GPT-5 连接...")
    
    # 测试 prompt
    prompt = "你是谁？请用中文简短回答，并告诉我你现在的版本型号。"
    
    start_time = time.time()
    
    # 调用我们在上面修改过的 request_gpt5_token 函数
    # 注意：这里会使用你 api_config.json 里配置的 key 和 url
    response, usage = request_gpt5_token(prompt)
    
    end_time = time.time()
    
    if response:
        print("\n✅ 测试成功！")
        print(f"⏱️ 耗时: {end_time - start_time:.2f} 秒")
        print("-" * 30)
        # 打印模型返回的原始内容
        print(response.choices[0].message.content)
        print("-" * 30)
        print(f"📊 Token 使用: {usage}")
    else:
        print("\n❌ 测试失败，请检查上方的报错信息。")