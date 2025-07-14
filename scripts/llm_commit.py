#!/usr/bin/env python3

import subprocess
import os
import requests
import json
import textwrap
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

API_KEY = load_api_key()
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL   = "llama3-70b-8192"

if not API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

SYSTEM_PROMPT = textwrap.dedent("""\
You are an AI assistant tasked with helping software developers write Git commit messages that follow both OpenStack's commit message guidelines and the Conventional Commits specification.

Please follow these rules strictly:

## 1. Structure
- Use the Conventional Commits format:  
  `<type>[optional scope]: <summary line>`
- Acceptable types include:  
  `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `chore`, `style`, `ci`, `revert`
- For breaking changes, append `!` to the type or use `BREAKING CHANGE:` in the footer.

## 2. Summary line
- Limit to 50 characters
- Use the imperative mood (e.g., “fix bug”, not “fixed bug”)
- Mention the subsystem as scope if applicable, e.g. `feat(libvirt): add new timer config`

## 3. Body
- Must start one blank line after the summary
- Wrap lines at 72 characters
- Clearly describe:
  - What the change does
  - Why it is necessary
  - Known limitations or trade-offs
  - Original problem if fixing a bug

## 4. Footer
- Must start one blank line after the body
- Include machine-readable metadata if applicable:
  - `Closes-Bug: #1234567`
  - `Partial-Bug: #1234567`
  - `Related-Bug: #1234567`
  - `Implements: blueprint-name`
  - `DocImpact`, `APIImpact`, `SecurityImpact`, `UpgradeImpact`
  - `Signed-off-by: Name <email>` (mandatory)

## 5. Commit splitting
- Each commit should contain **only one logical change**
- Do not mix whitespace-only changes with functional changes
- Refactoring must be separate from feature additions
- Do not combine unrelated changes into one commit

## 6. Test Plan
- If tests were performed, include a `Test Plan:` section in the body
- Explain how you verified the correctness of the change

## 7. Language
- The commit message must be fully self-contained
- Do not assume access to external websites (e.g. bug trackers)
- Avoid vague expressions; describe intent and justification explicitly

---

**Main rule:**  
> The commit message must contain all the information required to fully understand and review the patch.  
> *Less is not more. More is more.*
""")

# ステージされた変更を取得
staged_diff = subprocess.check_output(
    ["git", "diff", "--cached"], text=True)

user_prompt = (
    f"Generate the commit message for the following git diff:\n"
    f"{staged_diff}"
)

payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_prompt}
    ],
    "temperature": 0.4,
    "max_tokens": 128
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
response.raise_for_status()

commit_msg = response.json()["choices"][0]["message"]["content"].strip()
print("\nGenerated commit message:\n")
print(commit_msg)

ans = input("\nDo you want to adopt the commit message? (y/N): ")
if ans.lower() == 'y':
    subprocess.run(['git', 'commit', '-m', commit_msg])

