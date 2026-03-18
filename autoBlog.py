import requests
import subprocess
import time
import re
import random

LLM_URL = "http://127.0.0.1:8080/completion"

SUBJECT_ID = 24

TOPICS = [
    "AI agents in 2026",
    "future of autonomous systems",
    "how LLMs change software engineering",
    "AI and cybersecurity",
    "limits of artificial intelligence",
]

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def generate_article(topic):
    prompt = f"""
Write a complete HTML blog article.

Topic: {topic}

Requirements:
- Valid Markdown only
- no '#', maximum header is '##' apart from title
- so only title is allowed to be '#'
"""

    response = requests.post(LLM_URL, json={
        "prompt": prompt,
        "n_predict": 800
    })

    data = response.json()
    return data["content"]

def extract_title(content):
    lines = content.splitlines()

    title = None
    new_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect title: "# Title"
        if title is None and stripped.startswith("# "):
            title = stripped[2:].strip()
            continue  # skip this line (remove from content)

        new_lines.append(line)

    # Fallback if no title found
    if not title:
        for line in lines:
            stripped = line.strip()
            if stripped:
                title = re.sub(r"^#+\s*", "", stripped)
                break

    if not title:
        title = "AI Generated Article"

    cleaned_content = "\n".join(new_lines).strip()

    return title, cleaned_content

def main():
    while True:
        topic = random.choice(TOPICS)
        print(f"\n=== Generating: {topic} ===")

        try:
            content = generate_article(topic)

            title, content = extract_title(content)
            nickname = slugify(title)

            filename = f"articles/{nickname}.md"

            with open(filename, "w") as f:
                f.write(content)

            # create nickname
            subprocess.run([
                "stx", "nickname", "create",
                "--title", title,
                "--subject_id", str(SUBJECT_ID),
                "--is_public", "true",
                nickname
            ])

            # publish
            subprocess.run([
                "stx", "publish",
                "--file", filename,
                nickname
            ])

            print(f"Published: {title}")

        except Exception as e:
            print("Error:", e)

        time.sleep(30)  # wait 30s between posts

if __name__ == "__main__":
    main()


