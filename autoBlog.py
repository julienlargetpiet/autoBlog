import argparse
import sys
import requests
import subprocess
import time
import re
import random

def parse_args():
    parser = argparse.ArgumentParser(description="AutoBlog generator")

    parser.add_argument(
        "--is_public",
        choices=["true", "false"],
        help="Publish articles as public or private"
    )

    parser.add_argument(
        "--subject-id",
        type=int,
        default=24,
        help="Statix subject ID (default: 24)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=6000, # 10 minutes
        help="LLM request timeout in seconds (default: 120)"
    )

    parser.add_argument(
        "--llm-url",
        default="http://127.0.0.1:8080/completion",
        help="LLM server URL"
    )

    parser.add_argument(
        "--topics-file",
        default="topics.txt",
        help="Path to topics file (default: topics.txt)"
    )
    
    parser.add_argument(
        "--prompt-file",
        default="prompt.txt",
        help="Path to prompt file (default: prompt.txt)"
    )

    return parser.parse_args()

def load_topics(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            topics = [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith("#")
            ]

        if not topics:
            raise ValueError("No valid topics found")

        return topics

    except Exception as e:
        print(f"[ERROR] Failed to load topics from {path}: {e}")
        return [
            "AI agents in 2026",
            "future of autonomous systems",
            "AI and cybersecurity"
        ]

args = parse_args()

IS_PUBLIC = args.is_public
SUBJECT_ID = args.subject_id
TIMEOUT_VALUE = args.timeout
LLM_URL = args.llm_url
TOPICS = load_topics(args.topics_file)
PROMPT_FILE = args.prompt_file

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def generate_article(topic):
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
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
            timeout=TIMEOUT_VALUE
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


