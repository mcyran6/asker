#!/bin/bash

# Get the current working directory
current_dir=$(pwd)

# Define the alias with the dynamic path
alias_command="alias ask='source $current_dir/llm/Scripts/activate && python $current_dir/ask.py && deactivate'"

# Append the alias command to .bashrc
echo "$alias_command" >> ~/.bashrc
