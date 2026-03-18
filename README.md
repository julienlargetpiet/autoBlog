# autoBlog

Let an LLM write and publish blog articles while you sleep.

---

## Overview

This project connects:
- a **local LLM** (`llama.cpp`)
- your **Statix blog CLI**
- a **Python automation script**

👉 Result: fully automated article generation + publishing.

---

## 1. Set up a `Statix` blog

- [Statix](https://github.com/julienlargetpiet/Statix)

---

## 2. Configure Statix CLI

```bash
$ stx set-credentials --url URL --password TOKEN
```

---

## 3. Create a subject slot for AI articles

```bash
$ stx subject add "AutoBlog - Auto AI generated articles"
```

List subjects:

```bash
$ stx subjects
```

👉 Note the **ID** (e.g. `24`) and set it in your script:

```python
SUBJECT_ID = 24
```

---

## 4. Set up `llama.cpp`

```bash
$ sudo apt update
$ sudo apt install -y build-essential cmake
$ git clone https://github.com/ggml-org/llama.cpp
$ cd llama.cpp
$ cmake -B build -DGGML_NATIVE=ON
$ cmake --build build -j
```

---

## 5. Download a model

Download a GGUF model (example: LLaMA 3.1 8B Q4):  
👉 https://huggingface.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF

Recommended file:

```
Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
```

Place it in a folder, e.g.:

```
~/models/
```

---

## 6. Start the LLM server

```bash
./build/bin/llama-server \
  -m ~/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf \
  -c 1024 \
  -t 8
```

⚠️ **Notes**
- `-c` = context size → critical for RAM usage
- Recommended:
  - `1024` → safe (16GB RAM)
  - `2048` → higher quality but heavier

- `-t` is the number of CPU threads

---

## 7. Set up Python environment

```bash
$ python3 -m venv menv
$ source menv/bin/activate
(menv) $ pip install requests
```

---

## 8. Configure `autoBlog.py`

Project structure:

```
.
├── articles
└── autoBlog.py
└── prompt.txt
└── models
```

Make sure:
- `SUBJECT_ID` is correct
- Output folder exists:

```bash
$ mkdir -p articles
```

By default TOPICS are:

```

TOPICS = [
    "AI agents in 2026",
    "future of autonomous systems",
    "how LLMs change software engineering",
    "AI and cybersecurity",
    "limits of artificial intelligence",
]

```

You can change them direclty in the Code

**Note that the topic of an article is randomly chosen at runtime**

You can also vary the prompt in:

`prompt.txt`

---

## 9. Run the automation

```bash
(menv) $ python3 autoBlog.py true|false
```

where the last arg is the visibility on your Statix blog

---

## What happens

Loop:
1. Pick a topic
2. Generate article via local LLM
3. Extract title
4. Save markdown file
5. Create nickname
6. Publish via Statix

---

## Output format

- Articles are generated in Markdown
- Title (`# Title`) is extracted and removed from content
- Body is saved in:

```
articles/<slug>.md
```

---

## Example pipeline

```
LLM → Markdown
      ↓
extract title
      ↓
save file
      ↓
stx nickname create
      ↓
stx publish
```

---

## Notes

- No external APIs required
- Fully local (LLM + CLI)
- Performance depends on CPU + RAM
- Quality depends heavily on prompt

---

## Next steps

- Better prompt engineering
- Topic generation via LLM
- Deduplication / quality filtering
- Scheduling (cron)

---

## Philosophy

No SaaS. No API keys. No black boxes.  
Just local compute, full control, and automation.


