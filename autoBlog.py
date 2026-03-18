import sys
import requests
import subprocess
import time
import re
import random

if len(sys.argv) != 2 or sys.argv[1].lower() not in ["true", "false"]:
    print("Usage: python3 autoBlog.py true|false")
    sys.exit(1)

IS_PUBLIC = sys.argv[1].lower()

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
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read().strip()
    except Exception as e:
        print(f"[ERROR] Failed to read prompt.txt: {e}")
        return None

    prompt = prompt_template.replace("{{TOPIC}}", topic)

    try:
        response = requests.post(
            LLM_URL,
            json={
                "prompt": prompt,
                "n_predict": 800
            },
            timeout=120 
        )
    except requests.exceptions.ConnectionError:
        print("[ERROR] LLM server not reachable (is llama-server running?)")
        return None
    except requests.exceptions.Timeout:
        print("[ERROR] LLM request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None

    if response.status_code != 200:
        print(f"[ERROR] Bad response status: {response.status_code}")
        return None

    try:
        data = response.json()
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON: {e}")
        return None

    content = data.get("content")
    if not content:
        print("[ERROR] Empty content from LLM")
        return None

    return content

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
            
            if not content:
                print("Skipping iteration due to error")
                time.sleep(10)
                continue

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
                "--is_public", IS_PUBLIC,
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


