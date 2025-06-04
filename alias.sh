#!/bin/bash

# Get the current working directory
current_dir=$(pwd)

# Define the alias with the dynamic path
alias_command='alias ask='"'"'function _ask() { \
  source '"$current_dir"'/llm/Scripts/activate; \
  model="${1:-gpt4o}"; \
  python '"$current_dir"'/ask.py --model "$model"; \
  deactivate; \
}; _ask'"'"''

# Append the alias command to .bashrc
echo "$alias_command" >> ~/.bashrc
