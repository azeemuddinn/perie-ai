import os
from pydantic import BaseModel, Field
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class QualityScorecard(BaseModel):
    technical_depth_score: float = Field(..., description="Score 0.0 to 1.0 for engineering substance.")
    actionability_score: float = Field(..., description="Score 0.0 to 1.0 for how actionable/valuable it is for developers.")
    fluff_penalty: float = Field(..., description="Score 0.0 to 1.0 (1.0 = zero marketing fluff/clickbait).")
    overall_quality_grade: str = Field(..., description="PASS or FAIL based on whether score >= 0.75")
    critique: str = Field(..., description="Brief 1-sentence explanation of the score.")

def evaluate_brief_quality(brief_data: dict) -> QualityScorecard:
    prompt = f"""
    You are an elite Staff Engineering Editor reviewing an AI-generated tech brief.
    Evaluate the following brief based on technical depth, absence of marketing fluff, and engineering value.

    Brief Data:
    - Title: {brief_data.get('selected_title')}
    - Suggested Blog Title: {brief_data.get('suggested_blog_title')}
    - Why It Matters: {brief_data.get('why_it_matters')}
    - Outline: {brief_data.get('suggested_outline')}

    Provide a strict JSON evaluation scorecard.
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b", # or your active model
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    import json
    result = json.loads(response.choices[0].message.content)
    return QualityScorecard(**result)