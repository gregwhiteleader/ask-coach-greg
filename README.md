Ask Coach Greg

A smart, professional assistant that answers like Coach Greg on Agile (Scrum/Kanban) and Traditional Project Management (PMBOK/Waterfall). Built with Streamlit + OpenAI.

✨ Features

“Coach Greg” voice — practical, professional, approachable.

Agile & Traditional PM aware — responds in the right style based on your question.

Compact comparisons when a question is executive-level or ambiguous.

Streaming responses, Reset Chat, and Download Transcript.

Cost-controlled: locked to gpt-4o-mini.

📂 Project Structure
ask-coach-greg/
├─ Simple_Chatbot.py          # Streamlit entry
├─ helpers/
│  └─ llm_helper.py           # OpenAI client + streaming
├─ config.py                  # System prompt (Coach Greg voice)
├─ requirements.txt
├─ .gitignore                 # includes .env
├─ .env                       # LOCAL ONLY (contains OPENAI_API_KEY), do not commit
└─ coach_greg.jpg/png         # optional headshot in sidebar

🛠️ Requirements

Python 3.10 or 3.11

An OpenAI API key

requirements.txt (pinned):

streamlit==1.38.0
openai==1.40.6
python-dotenv==1.0.1


.gitignore (safe defaults):

# Environment files
.env

# Mac OS
.DS_Store

# Python cache
__pycache__/
**/__pycache__/
*.pyc
*.pyo
*.pyd

# Virtual envs
.venv/
venv/

# IDE
.idea/
.vscode/

⚙️ Local Setup (Windows / PowerShell)
# 1) Go to your project folder
cd C:\Users\<you>\PycharmProjects\ask-coach-greg

# 2) Create & activate a fresh virtual environment
py -m venv .venv
.\.venv\Scripts\Activate

# 3) Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 4) Add your API key to a local .env file (do NOT commit this file)
# In the project root, create .env with this line:
# OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# 5) Run the app
streamlit run Simple_Chatbot.py


Open your browser at http://localhost:8501.

🚀 Deploy to Streamlit Community Cloud

Push to GitHub

cd C:\Users\<you>\PycharmProjects\ask-coach-greg
git init
git add .
git commit -m "Ask Coach Greg - first deploy"
git branch -M main
git remote add origin https://github.com/<your-username>/ask-coach-greg.git
git push -u origin main


Before committing, run git status — .env should not appear.

Create the app

Go to https://share.streamlit.io

New app → select your repo and branch (main)

Main file path: Simple_Chatbot.py

Click Deploy

Set your API key (Secrets)

App Settings → Secrets

Add:

OPENAI_API_KEY = sk-xxxxxxxxxxxxxxxx


Save → Rerun the app

Share your link

You’ll get a URL like:

https://ask-coach-greg-<username>.streamlit.app

💸 Cost Notes (gpt-4o-mini)

Input: ~$0.15 / 1M tokens

Output: ~$0.60 / 1M tokens
Locked to gpt-4o-mini for speed & low cost.

🧪 Quick Smoke Test

Ask: “Give me a simple Sprint Review outline.”

Ask: “How should I handle a baseline schedule variance?”

Click Download Chat Transcript to verify file download.

🧩 Troubleshooting

App can’t find secrets locally

Create .env with OPENAI_API_KEY=... in the project root.

Do not commit .env (it’s ignored by .gitignore).

Pip/venv path mismatch

Create a fresh venv and use python -m pip:

Remove-Item -Recurse -Force .venv
py -m venv .venv
.\.venv\Scripts\Activate
python -m pip install -r requirements.txt


PyCharm running wrong interpreter

Settings → Project: ask-coach-greg → Python Interpreter
Select: ...ask-coach-greg\.venv\Scripts\python.exe

Run/Debug Config → Script path: Simple_Chatbot.py

Image not showing on Cloud

Commit coach_greg.jpg/png to the repo (local-only files won’t deploy).

🔐 Security

Never commit .env.

Rotate your key if it’s ever exposed.

On Cloud, always use Secrets (not environment files).

📜 License

You can choose a license (e.g., MIT) or keep it private.

🙋‍♂️ About

Ask Coach Greg — a lightweight, practical assistant that answers the way Coach Greg would, across Agile and Traditional project delivery.

You said: