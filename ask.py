import argparse
from chatapi import LLMClient
import os
import re

lim = 512
keywords = ["import", "model", "lim", "help"]
quitwords = ["exit", "quit", "thanks", "thank you"]

def parse_commands(command, client):
    if command in quitwords:
        print("Goodbye")
        return False

    words = command.split()
    if not words:
        return ""

    if words[0] in keywords:
        arg = words[1] if len(words) > 1 else ""

        if words[0] == "import":
            import_string(arg, client)
        elif words[0] == "model":
            try:
                client.set_model(arg)
            except ValueError as e:
                print(e)
        elif words[0] == "lim":
            client.set_limit(int(arg))
        elif words[0] == "help":
            print_help_message()

        newwords = words[2:] if len(words) > 2 else []
        return parse_commands(" ".join(newwords), client)
    else:
        return command

def import_string(input_string, client):
    files = [f.strip() for f in input_string.split(',')] if ',' in input_string else [input_string]
    for file_path in files:
        if os.path.isfile(file_path):
            if os.path.getsize(file_path) > 5 * 1024 * 1024:
                print("File size exceeds 5MB.")
            else:
                client.attach_file(file_path)
        print(f"Processing: {file_path}")

def print_help_message():
    print("Usage:")
    print("  import <file1>[,<file2>,...]")
    print("    Import one or more files.")
    print("  model <model_name>")
    print("    Override the default model.")
    print("  lim <max_words>")
    print("    Set the limit for the number of words in the response.")
    print("  help")
    print("    Display this help message.")

def save_code_artifacts(api_response):
    artifact_dir = "code_artifacts"
    os.makedirs(artifact_dir, exist_ok=True)

    patterns = {
        "py": r"```python\n(.*?)\n```",
        "txt": r"```text\n(.*?)\n```",
        "sh": r"```bash\n(.*?)\n```",
        "java": r"```java\n(.*?)\n```",
        "md": r"```markdown\n(.*?)\n```",
        "html": r"```html\n(.*?)\n```"
    }

    for file_type, pattern in patterns.items():
        code_blocks = re.findall(pattern, api_response, re.DOTALL)
        for i, code_block in enumerate(code_blocks):
            file_path = os.path.join(artifact_dir, f"code_artifact_{i+1}.{file_type}")
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(code_block.strip())
            print(f"{file_type.upper()} saved to: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Chat with OpenRouter-backed LLMs")
    parser.add_argument("--model", type=str, default="gpt4o", help="Model to use (e.g. gpt4o, claude, mixtral)")
    args = parser.parse_args()

    client = LLMClient()

    try:
        client.set_model(args.model)
    except ValueError as e:
        print(f"⚠️ {e}")
        print("Available models:")
        for key in client.models.keys():
            print(f"  - {key}")
        return

    model_name = args.model
    while True:
        prompt = input(f"How can {model_name} help you today? ")
        prompt = parse_commands(prompt, client)
        if not prompt:
            client.print_log()
            break

        if prompt != "":
            response = ""
            for chunk in client.stream_response(prompt):
                response += chunk
                print(chunk, end='', flush=True)
            save_code_artifacts(response)

if __name__ == "__main__":
    main()
