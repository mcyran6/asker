import os
from dotenv import load_dotenv
import anthropic
from anthropic import Anthropic
import mimetypes
import base64
from typing import List, Union, Dict
import datetime
import PyPDF2  # Add this line
from io import BytesIO

class ClaudeClient:

    def __init__(self, api_key: str = None):
        
        """Initialize Claude API client with authentication"""
        # Load environment variables from .env file
        load_dotenv(verbose=True)  # Added verbose flag for debugging
        
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError(
                "API key not found. Ensure either:\n"
                "1. ANTHROPIC_API_KEY is set in your .env file\n"
                "2. ANTHROPIC_API_KEY is set as an environment variable\n"
                "3. API key is passed directly to the constructor"
            )

        self.client = Anthropic(api_key=self.api_key)
        self.message_list = []
        self.models = {
            'opus': 'claude-3-opus-20240229',
            'v1': 'claude-v1',
            'instant': 'claude-instant-v1',
            'v1.2': 'claude-v1.2',
            'v1.3': 'claude-v1.3',
            'sonnet': 'claude-3-5-sonnet-20241022',
            'haiku': 'claude-3-haiku-20240307'
        }
        self.limit = 512 
        self.model = self.models['haiku']  # Default model

    def set_model(self, model_key: str):
        if model_key in self.models:
            self.model = self.models[model_key]
        else:
            raise ValueError(f"Invalid model key: {model_key}")

    def set_limit(self, lim: int):
        self.limit = lim

    def print_log(self):
        # Create the "conv" directory if it doesn't exist
        if not os.path.exists("conv"):
            os.makedirs("conv")

        # Generate a unique filename based on the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.log"

        # Construct the full file path
        file_path = os.path.join("conv", filename)

        # Write the conversation log to the file
        with open(file_path, "w") as file:
            for message in self.message_list:
                try:
                    file.write(f"{message}")
                except UnicodeEncodeError as e:
                    print(f"Error encoding string: {e}")

        print(f"Conversation log saved to: {file_path}")

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response from Claude
        
        Args:
            prompt: Input text to send to Claude
            model: Model identifier to use
            max_tokens: Maximum tokens in the response
            
        Returns:
            str: Claude's response text
        """
        user_input={"role":"user","content":prompt}
        self.message_list.append(user_input)
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.limit,
                messages=self.message_list
            )
            computer_response={"role":"assistant","content":message.content[0].text}
            self.message_list.append(computer_response)
            return message.content[0].text
            
        except anthropic.APIError as e:
            raise Exception(f"API error occurred: {str(e)}")

    def stream_response(self, prompt: str):
        """
        Stream a response from Claude
        
        Args:
            prompt: Input text to send to Claude
            model: Model identifier to use
            
        Yields:
            str: Chunks of Claude's response text
        """
        user_input={"role":"user","content":prompt}
        self.message_list.append(user_input)
        try:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=self.limit,
                messages=self.message_list
            ) as stream:
                full_text = ""
                for text in stream.text_stream:
                    full_text += text
                    yield text
                
                computer_response={"role":"assistant","content":full_text}
                self.message_list.append(computer_response)
        except anthropic.APIError as e:
            raise Exception(f"API error occurred: {str(e)}")
    
    def _prepare_file_content(self, file_path: str) -> dict:
        """
        Prepare a file for sending to Claude API

        Args:
            file_path: Path to the file

        Returns:
            dict: File content object ready for API submission
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        with open(file_path, 'rb') as f:
            content = f.read()

        if mime_type.startswith('image/'):
            # Handle image files
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64.b64encode(content).decode('utf-8')
                }
            }
        elif mime_type == 'application/pdf':
            # Handle PDF files
            try:
                # Extract text from PDF
                pdf_reader = PyPDF2.PdfReader(BytesIO(content))
                text_content = ''.join([page.extract_text() for page in pdf_reader.pages])
                return {
                    "type": "text",
                    "text": f"[I am pasting the contents of file {file_path}. For the rest of the conversation, refer to the following data by its file name]=>\n{text_content}"
                }
            except Exception as e:
                raise ValueError(f"Error processing PDF file {file_path}: {str(e)}")
        else:
            # Handle text files and other file types
            try:
                text_content = content.decode('utf-8')
                return {
                    "type": "text",
                    "text": f"[I am pasting the contents of file {file_path}. For the rest of the conversation, refer to the following data by its file name] =>\n{text_content}"
                }
            except UnicodeDecodeError:
                raise ValueError(f"File {file_path}appears to be binary and not an image. Only text and image files are supported.")

    def attach_file(self, file_paths: Union[str,List[str]]):
        """
        Add the file to the message_list before the prompt gets sent
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
            
        try:
            content_list = []
            # Add each file's content
            for file_path in file_paths:
                content_list.append(self._prepare_file_content(file_path)) 
            
            file_input = {
                "role":"user",
                "content":content_list
            }
            self.message_list.append(file_input)
            confirm = {
                "role":"assistant",
                "content":"Thank you for sharing "+file_path+" with me. I understand it to be a file named "+file_path+" from your computer, and copied into the message window. However, I will consider to it as being 'imported'. What else can I help you with?"
            }
            self.message_list.append(confirm)
        except Exception as e:
            raise Exception(f"Error processing files: {str(e)}")

    def send_file(self, prompt: str, file_paths: Union[str, List[str]], max_tokens: int = 1024) -> str:
        """
        Generate a response from Claude with file attachments
        
        Args:
            prompt: Input text to send to Claude
            file_paths: Single file path or list of file paths to attach
            model: Model identifier to use
            max_tokens: Maximum tokens in the response
            
        Returns:
            str: Claude's response text
        """
        if isinstance(file_paths, str):
            file_paths = [file_paths]
            
        try:
            content_list = []
            # Add each file's content
            for file_path in file_paths:
                content_list.append(self._prepare_file_content(file_path)) 
            
            file_input = {
                "role":"user",
                "content":content_list
                #"metadata":{
                #    "file_name":file_paths
                #}
            }
            self.message_list.append(file_input)
            confirm = {
                "role":"assistant",
                "content":"Thank you for sharing "+file_path+" with me. I understand it to be a file named "+file_path+" from your computer, and copied into the message window. However, I will consider to it as being 'imported'. What else can I help you with?"
            }
            #confirm = {
            #    "role":"assistant",
            #    "content":"Thank you for sharing "+file_path+" What else can I help you with?"
            #}
            self.message_list.append(confirm)
            prompt_input = {
                "role":"user",
                "content": prompt
            }
            self.message_list.append(prompt_input)
            # Create message with files
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.limit,
                messages=self.message_list
            )
            computer_response={"role":"assistant","content":message.content[0].text}
            self.message_list.append(computer_response)
            return message.content[0].text
            
        except anthropic.APIError as e:
            raise Exception(f"API error occurred: {str(e)}")
        except Exception as e:
            raise Exception(f"Error processing files: {str(e)}")
