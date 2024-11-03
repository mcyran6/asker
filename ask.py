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
            if os.path.isfile(arg):
                file_size = os.path.getsize(arg)
                if file_size > 5 * 1024 * 1024:
                    print("File size exceeds 5MB.")
                else:
                    client.attach_file(arg)
        elif words[0] == "model":
            client.set_model(arg)
        elif words[0] == "lim":
            client.set_limit(int(arg))
        elif words[0] == "help":
            print(keywords)
        
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


def parse_file(user_input):
    # Check if the input contains the word "import"
    words = user_input.split()
    if "import" in words[0]:
        # Extract the file path after the word "import"
        file_path = words[1]
        prompt = " ".join(words[2:])
        #print(words)
        #print(prompt)
        # Check if the file exists
        if os.path.isfile(file_path):
            # Get the file size in bytes
            file_size = os.path.getsize(file_path)
            
            # Check if the file size is larger than 5MB (5 * 1024 * 1024 bytes)
            if file_size > 5 * 1024 * 1024:
                print("File size exceeds 5MB.")
            else:
                return file_path, prompt
                #with open(file_path, 'r') as file:
                #    file_contents = file.read()
                #    print("File contents:")
                #    print(file_contents)
        else:
            print("File does not exist.")
    return "",user_input

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
