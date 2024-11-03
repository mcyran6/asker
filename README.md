## Ask Claude
This app integrates claude into the command line so that your files are at your fingertips. Instead of copying from a website into a file and saved, this will automatically save code artifacts so they could be run immediately. It also takes command like arguments to run tasks parallel to the prompt. For help, type help into the prompt

#### Setting up Environment
I recommend using virtualenv to manage different runtimes, you can also just use the third line to install requirements.
```
python -m virtualenv VE
source VE/Scripts/activate
pip install -r requirements.txt
```
You will also need an API key from [anthropic](https://www.anthropic.com/api) and store it in a .env file in this directory as
```
ANTHROPIC_API_KEY=your_api_key
```

#### Run chat interface
```
python ask.py
```
