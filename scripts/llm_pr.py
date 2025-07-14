#!/usr/bin/env python3

import subprocess
import json
import requests
import sys
from pathlib import Path

def load_api_key():
    current_dir = Path(__file__).resolve().parent
    for directory in [current_dir] + list(current_dir.parents):
        env_file = directory / '.env'
        if env_file.is_file():
            with env_file.open() as f:
                for line in f:
                    if line.startswith('GROQ_API_KEY='):
                        return line.strip().split('=', 1)[1]
    raise RuntimeError("GROQ_API_KEY not found in any .env file")

GROQ_API_KEY = load_api_key()
if not GROQ_API_KEY:
    print("Environment variable GROQ_API_KEY is not set.", file=sys.stderr)
    sys.exit(1)

base = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
diff = subprocess.check_output(["git", "diff", f"{base}..."], text=True)

prompt = f"""You are assisting a software engineer in writing a high-quality Pull Request (PR). ...\n{diff}"""

payload = {
    "model": "llama3-70b-8192",
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 1024,
    "temperature": 0.4
}

res = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
    data=json.dumps(payload)
)
res.raise_for_status()
txt = res.json()["choices"][0]["message"]["content"]

title = ""
body_lines = []
for line in txt.splitlines():
    if line.lower().startswith("title:"):
        title = line.split(":", 1)[1].strip()
    elif line.lower().startswith("body:"):
        body_lines.append(line.split(":", 1)[1].strip())
    else:
        body_lines.append(line.strip())

# タイトルが空の場合は現在のブランチ名をフォールバックとして利用
if not title:
    title = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True).strip()

body = "\n".join(body_lines).strip()

subprocess.run(["gh", "pr", "create", "--title", title, "--body", body])

