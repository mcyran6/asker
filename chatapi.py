import os
import requests
from dotenv import load_dotenv
from typing import List, Union, Dict
import datetime
import mimetypes
import base64
import PyPDF2
from io import BytesIO
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class LLMClient:
    def __init__(self, api_key: str = None):
        load_dotenv()
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key missing. Set OPENROUTER_API_KEY.")

        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.message_list = []
        self.models = {
            "gpt4o": "openai/gpt-4o",
            "gpt-4": "openai/gpt-4",
            "gpt-3.5": "openai/gpt-3.5-turbo",
            "claude": "anthropic/claude-3-haiku",
            "claude-sonnet": "anthropic/claude-3-sonnet",
            "claude-opus": "anthropic/claude-3-opus",
            "mixtral": "mistralai/mixtral-8x7b",
            "gemini": "google/gemini-pro",
            "command-r": "cohere/command-r",
            "command-r+": "cohere/command-r-plus",
            "llama3-70b": "meta-llama/llama-3-70b-instruct",
            "llama3-8b": "meta-llama/llama-3-8b-instruct",
        }

        self.model = self.models["claude"]
        self.limit = 1000

    def set_model(self, model_key: str):
        if model_key in self.models:
            self.model = self.models[model_key]
        else:
            raise ValueError(f"Invalid model key: {model_key}")

    def set_limit(self, lim: int):
        self.limit = lim

    def generate_response(self, prompt: str) -> str:
        self.message_list.append({"role": "user", "content": prompt})
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://yourapp.com",  # required
            "X-Title": "YourApp/Chat"
        }

        payload = {
            "model": self.model,
            "messages": self.message_list,
            "max_tokens": self.limit
        }

        response = requests.post(self.endpoint, json=payload, headers=headers, verify=False)
        if not response.ok:
            raise Exception(f"OpenRouter API Error: {response.text}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        self.message_list.append({"role": "assistant", "content": content})
        return content

    def stream_response(self, prompt: str):
        self.message_list.append({"role": "user", "content": prompt})
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://yourapp.com",
            "X-Title": "YourApp/Chat"
        }

        payload = {
            "model": self.model,
            "messages": self.message_list,
            "stream": True,
            "max_tokens": self.limit
        }

        with requests.post(self.endpoint, json=payload, headers=headers, stream=True, verify=False) as response:
            if not response.ok:
                raise Exception(f"Stream error: {response.text}")

            full_text = ""
            for line in response.iter_lines():
                if line and line.startswith(b'data: '):
                    chunk = line[len(b'data: '):].decode("utf-8")
                    if chunk == "[DONE]":
                        break
                    try:
                        parsed = json.loads(chunk)
                        delta = parsed["choices"][0]["delta"].get("content", "")
                        full_text += delta
                        yield delta
                    except Exception as e:
                        print(f"Stream parse error: {e}")

            self.message_list.append({"role": "assistant", "content": full_text})


    def _prepare_file_content(self, file_path: str) -> dict:
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        with open(file_path, 'rb') as f:
            content = f.read()

        if mime_type.startswith('image/'):
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64.b64encode(content).decode('utf-8')
                }
            }
        elif mime_type == 'application/pdf':
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(content))
                text_content = ''.join([page.extract_text() or '' for page in pdf_reader.pages])
                return {
                    "type": "text",
                    "text": f"[File: {file_path}]\n{text_content}"
                }
            except Exception as e:
                raise ValueError(f"Error reading PDF: {str(e)}")
        else:
            try:
                text_content = content.decode("utf-8")
                return {
                    "type": "text",
                    "text": f"[File: {file_path}]\n{text_content}"
                }
            except UnicodeDecodeError:
                raise ValueError(f"Unsupported binary file: {file_path}")

    def attach_file(self, file_paths: Union[str, List[str]]):
        if isinstance(file_paths, str):
            file_paths = [file_paths]

        for file_path in file_paths:
            file_msg = self._prepare_file_content(file_path)
            self.message_list.append({"role": "user", "content": file_msg["text"]})
            self.message_list.append({"role": "assistant", "content": f"Imported file: {file_path}"})

    def send_file(self, prompt: str, file_paths: Union[str, List[str]]) -> str:
        self.attach_file(file_paths)
        return self.generate_response(prompt)

    def print_log(self):
        if not os.path.exists("conv"):
            os.makedirs("conv")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join("conv", f"conversation_{timestamp}.log")

        with open(file_path, "w", encoding="utf-8") as f:
            for msg in self.message_list:
                f.write(f"{msg['role']}: {msg['content']}\n")

        print(f"Saved conversation to {file_path}")
