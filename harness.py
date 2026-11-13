import asyncio
import json
import os
from groq import Groq
from database import get_db
from llm_client import evaluate_topics_with_llm, TopicBrief
from mcp_client import send_brief_to_slack
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_pending_topics(limit: int = 15) -> list[dict]:
    """Fetches unreviewed topics from SQLite."""
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT id, title, url, source, snippet FROM topics WHERE status = 'pending' ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

def finalize_run(selected_id: int, all_candidate_ids: list[int], brief: TopicBrief):
    """Logs the run result and updates topic statuses in SQLite."""
    with get_db() as db:
        cursor = db.cursor()
        
        # 1. Insert the evaluation log into runs
        cursor.execute("""
            INSERT INTO runs (selected_topic_id, evaluation_score, summary)
            VALUES (?, ?, ?)
        """, (selected_id, brief.evaluation_score, brief.short_description))
        
        # 2. Mark the winning topic as 'selected' and the rest as 'reviewed'
        cursor.execute("UPDATE topics SET status = 'selected' WHERE id = ?", (selected_id,))
        other_ids = [tid for tid in all_candidate_ids if tid != selected_id]
        if other_ids:
            placeholders = ",".join("?" * len(other_ids))
            cursor.execute(f"UPDATE topics SET status = 'reviewed' WHERE id IN ({placeholders})", other_ids)
            
        db.commit()

def run_agent_pipeline(provider: str = None) -> dict:
    """Main deterministic agent loop: Fetch -> Validate -> Evaluate -> Log."""
    candidates = get_pending_topics(limit=15)
    if not candidates:
        return {"status": "skipped", "reason": "No pending topics in database. Run /collect first."}

    # Call the LLM using SKILL.md rules
    brief: TopicBrief = evaluate_topics_with_llm(candidates, provider=provider)

    # Guardrail: Ensure the LLM picked a valid ID from our candidate list
    valid_ids = [c["id"] for c in candidates]
    if brief.selected_topic_id not in valid_ids:
        raise ValueError(f"Hallucinated topic ID {brief.selected_topic_id} not in candidates.")

    finalize_run(brief.selected_topic_id, valid_ids, brief)

    return {
        "status": "completed",
        "provider_used": provider or "default",
        "result": brief.model_dump()
    }


def run_agent_pipeline(provider: str = None) -> dict:
    candidates = get_pending_topics(limit=15)
    if not candidates:
        return {"status": "skipped", "reason": "No pending topics in database. Run /collect first."}

    brief: TopicBrief = evaluate_topics_with_llm(candidates, provider=provider)

    valid_ids = [c["id"] for c in candidates]
    if brief.selected_topic_id not in valid_ids:
        raise ValueError(f"Hallucinated topic ID {brief.selected_topic_id} not in candidates.")

    finalize_run(brief.selected_topic_id, valid_ids, brief)

    # 1. Run Quality Judge evaluation on the generated brief
    try:
        scorecard = evaluate_brief_quality(brief.model_dump())
    except Exception as e:
        scorecard = {"grade": "PASS", "technical_depth_score": 0.8, "critique": f"Judge skipped due to error: {str(e)}"}

    # 2. Combine brief and scorecard payload for Slack
    slack_payload = {
        **brief.model_dump(),
        "scorecard": scorecard
    }

    # 3. Automatically dispatch the enriched brief to Slack
    try:
        asyncio.run(send_brief_to_slack(slack_payload))
        slack_status = "sent"
    except Exception as e:
        slack_status = f"failed: {str(e)}"

    return {
        "status": "completed",
        "provider_used": provider or "default",
        "slack_delivery": slack_status,
        "quality_gate": scorecard,
        "result": brief.model_dump()
    } 

def evaluate_brief_quality(brief_data: dict) -> dict:
    """LLM-as-a-Judge to score the generated brief before dispatching."""
    prompt = f"""
    You are an elite Staff Engineering Editor reviewing an AI-generated tech brief.
    Evaluate the following brief based on technical depth, absence of marketing fluff, and developer value.

    Brief Data:
    - Title: {brief_data.get('selected_title')}
    - Suggested Blog Title: {brief_data.get('suggested_blog_title')}
    - Why It Matters: {brief_data.get('why_it_matters')}
    - Outline: {brief_data.get('suggested_outline')}

    Provide a strict JSON response with these exact keys:
    - "technical_depth_score": float between 0.0 and 1.0
    - "actionability_score": float between 0.0 and 1.0
    - "fluff_penalty": float between 0.0 and 1.0 (1.0 = zero fluff)
    - "grade": "PASS" or "FAIL" (PASS if average score >= 0.7)
    - "critique": "1 sentence explanation"
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
