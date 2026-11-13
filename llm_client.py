import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel
from groq import Groq
from google import genai
from google.genai import types

load_dotenv()

# Pydantic schema enforcing Section 5 of your SOW
class TopicBrief(BaseModel):
    selected_topic_id: int
    selected_title: str
    suggested_blog_title: str
    why_it_matters: str
    short_description: str
    source_links: list[str]
    suggested_outline: list[str]
    evaluation_score: float

def load_skill_instructions() -> str:
    """Reads the agent instructions from skills/SKILL.md."""
    with open("skills/SKILL.md", "r", encoding="utf-8") as f:
        return f.read()

def evaluate_topics_with_llm(candidates: list[dict], provider: str = None) -> TopicBrief:
    """Routes the candidate topics to either Groq or Gemini based on configuration."""
    active_provider = (provider or os.getenv("DEFAULT_LLM_PROVIDER", "groq")).lower()
    system_prompt = load_skill_instructions()
    user_prompt = f"Evaluate these candidate topics from today and select the best one:\n\n{json.dumps(candidates, indent=2)}"

    if active_provider == "gemini":
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json",
                response_schema=TopicBrief,
                temperature=0.2,
            ),
        )
        return TopicBrief.model_validate_json(response.text)

    elif active_provider == "groq":
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        chat_completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",  # <--- Updated active model ID
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw_json = chat_completion.choices[0].message.content
        return TopicBrief.model_validate_json(raw_json)

    else:
        raise ValueError(f"Unsupported LLM provider: {active_provider}")