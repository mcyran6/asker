from chatapi import ClaudeClient
import os
import re

lim=512
keywords = ["import", "model", "lim", "help"] 
quitwords = ["exit", "quit", "thanks", "thank you"]

# Define a function to parse the command
def parse_commands(command,client):
    # Split the command into a list of words
    if command in quitwords:
        print("Goodbye")
        return False

    words = command.split()
     
    # Check if the first word is a keyword
    if words[0] in keywords:
        # Get the argument (second word)
        arg = ""
        if len(words)>1:
            arg = words[1]
        
        # Perform the appropriate action based on the keyword
        if words[0] == "import":
            import_string(arg,client)
        elif words[0] == "model":
            client.set_model(arg)
        elif words[0] == "lim":
            client.set_limit(int(arg))
        elif words[0] == "help":
            print_help_message()
        
        # Remove the first two words from the command
        newwords = []
        if len(words)>2:
            newwords = words[2:]
        else:
            return ""
        # Recursively call the function with the remaining words
        return parse_commands(" ".join(newwords),client)
    else:
        return command

def import_string(input_string,client):
    # Check if the input string has commas
    if ',' in input_string:
        # Split the string by commas and process each part individually
        parts = input_string.split(',')
        for part in parts:
            # Run the command on each part
            if os.path.isfile(part):
                file_size = os.path.getsize(part)
                if file_size > 5 * 1024 * 1024:
                    print("File size exceeds 5MB.")
                else:
                    client.attach_file(part)
            print(f"Processing: {part.strip()}")
    else:
        # Run the command on the entire string
        if os.path.isfile(input_string):
            file_size = os.path.getsize(input_string)
            if file_size > 5 * 1024 * 1024:
                print("File size exceeds 5MB.")
            else:
                client.attach_file(input_string)
        print(f"Processing: {input_string}")

def print_help_message():
    """Prints the usage information for the command line app."""
    print("Usage:")
    print("  import <file1>[,<file2>,...]")
    print("    Import one or more files.")
    print("  model <model_name>")
    print("    Override the default haiku model.")
    print("  lim <max_words>")
    print("    Set the limit for the number of words in the response.")
    print("  help")
    print("    Display this help message.")

def save_code_artifacts(api_response):
    # Create a directory to store the code artifacts
    artifact_dir = "code_artifacts"
    os.makedirs(artifact_dir, exist_ok=True)

    # Regular expression patterns to match different file types
    patterns = {
        "py": r"```python\n(.*?)\n```",
        "txt": r"```text\n(.*?)\n```",
        "sh": r"```bash\n(.*?)\n```",
        "java": r"```java\n(.*?)\n```",
        "md": r"```markdown\n(.*?)\n```",
        "html": r"```html\n(.*?)\n```"
    }

    for file_type, pattern in patterns.items():
        # Find all code blocks of the current file type in the API response
        code_blocks = re.findall(pattern, api_response, re.DOTALL)

        # Save each code block as a separate file
        for i, code_block in enumerate(code_blocks):
            file_name = f"code_artifact_{i+1}.{file_type}"
            file_path = os.path.join(artifact_dir, file_name)

            with open(file_path, "w", encoding='utf-8') as file:
                file.write(code_block.strip())

            print(f"{file_type.capitalize()} code artifact saved: {file_path}")

def main():
    client = ClaudeClient()
    while True:
        prompt = input("How can claude help you today?")    
        
        prompt = parse_commands(prompt, client) 
        if not prompt:
            client.print_log()
            break

        if prompt!="":
            response = ""
            for chunk in client.stream_response(prompt):
                response += chunk
                print(chunk, end='', flush=True)
            save_code_artifacts(response)

if __name__ == "__main__":
    main()
