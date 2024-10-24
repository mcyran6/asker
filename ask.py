from chatapi import ClaudeClient
import os
import re

lim=512

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

    # Regular expression pattern to match Python code blocks
    code_pattern = r"```python\n(.*?)\n```"

    # Find all Python code blocks in the API response
    code_blocks = re.findall(code_pattern, api_response, re.DOTALL)

    # Save each code block as a separate file
    for i, code_block in enumerate(code_blocks):
        file_name = f"code_artifact_{i+1}.py"
        file_path = os.path.join(artifact_dir, file_name)

        with open(file_path, "w") as file:
            file.write(code_block.strip())

        print(f"Code artifact saved: {file_path}")

def main():
    client = ClaudeClient()
    while True:
        prompt = input("How can claude help you today?")    
        
        # Check if the user wants to exit
        if prompt.lower() in ["exit", "quit", "thank you", "thanks"]:
            print("Goodbye!")
            client.print_log() 
            break

        file, after_prompt = parse_file(prompt)
        if not file=="":
            #print("File to be imported:",file)
            #print("Prompt:",after_prompt)
            client.send_file(after_prompt,file,max_tokens=lim)
        #response = client.generate_response(prompt,max_tokens=lim)
        #print(response)
        response = ""
        for chunk in client.stream_response(prompt,max_tokens=lim):
            response += chunk
            print(chunk, end='', flush=True)

        save_code_artifacts(response)

if __name__ == "__main__":
    main()
