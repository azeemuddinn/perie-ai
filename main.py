from fastapi import FastAPI, HTTPException
from database import init_db, get_db
from collector import fetch_rss_topics, save_topics_to_db
from collector import fetch_rss_topics, save_topics_to_db
from harness import run_agent_pipeline


app = FastAPI(title="PerieAI", version="1.0.0")

@app.on_event("startup")
def startup_event():
    init_db()
    print("Database initialized successfully.")

@app.get("/")
def read_root():
    return {"status": "online", "agent": "PerieAI is ready to start"}

@app.post("/collect")
async def trigger_collection():
    """Triggers fetching from RSS sources and saves new topics to SQLite."""
    raw_topics = await fetch_rss_topics()
    new_count = save_topics_to_db(raw_topics)
    
    # Return count and a few stored items for verification
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, title, source FROM topics ORDER BY id DESC LIMIT 5")
        recent_topics = [dict(row) for row in cursor.fetchall()]
        
    return {
        "status": "success",
        "fetched_raw": len(raw_topics),
        "new_inserted": new_count,
        "recent_topics": recent_topics
    }

@app.post("/run")
def trigger_agent(provider: str | None = None):
    """Runs the agent harness. Optional query param: provider='groq' or 'gemini'."""
    try:
        return run_agent_pipeline(provider=provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))