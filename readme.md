# PerieAI 🚀
### An Autonomous Technical Research & Intelligence Agent

**PerieAI** is an AI-powered technical research agent that discovers, evaluates, and delivers meaningful technology developments — without the noise.

It continuously collects technology news and engineering updates, evaluates them against predefined technical and editorial standards, and uses an **LLM-as-a-Judge** quality gate to ensure every briefing is relevant, insightful, and actionable.

The result? A curated technical intelligence briefing delivered directly to your Slack channel.

**Discover. Evaluate. Validate. Deliver.**

---

## ✨ What PerieAI Does

PerieAI automates the technical research and editorial process through four stages:

1. **Collect** — Ingests technology articles and updates from configured feeds.
2. **Evaluate** — Identifies high-impact developments based on technical relevance and engineering significance.
3. **Validate** — Uses an independent LLM evaluation process to assess the quality, depth, and actionability of generated briefings.
4. **Deliver** — Sends approved technical intelligence briefings directly to Slack.

Only content that passes the quality gate gets delivered.

---

## 🏗️ Architecture & Technology

| Component | Technology |
|---|---|
| Backend API | Python, FastAPI |
| Data Validation | Pydantic |
| Database | SQLite |
| LLM Intelligence | Groq / Google Gemini |
| Structured Outputs | JSON |
| Editorial Framework | Custom `SKILL.md` rubric |
| Quality Evaluation | LLM-as-a-Judge |
| Notifications | Slack Web API |
| HTTP Client | httpx |

### How It Works

```text
       Technology Feeds
              |
              v
       Feed Collection
              |
              v
        SQLite Database
              |
              v
       Topic Selection
              |
              v
        LLM Research
              |
              v
       Brief Generation
              |
              v
       Editorial Judge
          /       \
       FAIL       PASS
        |           |
      Reject     Slack Delivery
                    |
                    v
             Technical Brief
```

---

## 🧠 Intelligence & Quality Control

PerieAI goes beyond simply summarizing technology news.

It uses a two-stage intelligence process:

**1. Content Generation**

An LLM researches and generates a technical briefing based on the selected development.

**2. Independent Quality Evaluation**

A separate evaluation step acts as an editorial judge, assessing the generated briefing against a predefined `SKILL.md` rubric.

The evaluation focuses on:

- Technical depth and accuracy
- Engineering and architectural significance
- Practical relevance
- Actionability
- Overall briefing quality

Briefings must pass the quality gate before being delivered.

---

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- Groq API key and/or Google Gemini API key
- Slack Bot Token
- Slack channel access

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd PerieAI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key

SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_CHANNEL_ID=your-slack-channel-id
```

Configure the API keys for the LLM providers you intend to use.

### 5. Start the Application

```bash
uvicorn main:app --reload
```

The API will be available at:

`http://localhost:8000`

Interactive API documentation:

`http://localhost:8000/docs`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/collect` | Collects and stores fresh technology articles. |
| POST | `/run` | Executes the complete research, evaluation, and delivery pipeline. |
| POST | `/test-slack` | Sends a test notification to verify Slack connectivity. |

---

## 🔐 Configuration

PerieAI uses environment variables to manage API credentials and external service integrations.

**Never commit your `.env` file or expose API keys in source control.**

Add the following to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
perie_ai.db
```

---

## 🎯 Project Vision

The internet produces more technology information than engineering teams can realistically consume.

PerieAI aims to solve this problem by building an autonomous technical intelligence system that prioritizes **signal over noise**.

The long-term vision is to evolve from a technology briefing agent into a reliable engineering intelligence platform — one that can continuously research emerging technologies, evaluate architectural decisions, identify important developments, and help engineering teams stay ahead.

---

**PerieAI — Less noise. More engineering intelligence.** 🚀