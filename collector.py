import httpx
import feedparser
from database import get_db

# Example RSS feeds for tech/AI development
RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://news.ycombinator.com/rss"
]

async def fetch_rss_topics():
    """Fetches topics from RSS feeds asynchronously."""
    new_topics = []
    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in RSS_FEEDS:
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    feed = feedparser.parse(response.text)
                    source_name = feed.feed.get("title", url)
                    
                    # Grab top 5 items from each feed
                    for entry in feed.entries[:5]:
                        title = entry.get("title", "No Title")
                        link = entry.get("link", "")
                        summary = entry.get("summary", entry.get("description", ""))
                        
                        if link and title:
                            new_topics.append({
                                "title": title,
                                "url": link,
                                "source": source_name,
                                "snippet": summary[:300] # truncate for cleaner storage
                            })
            except Exception as e:
                print(f"Error fetching RSS from {url}: {e}")
                
    return new_topics

def save_topics_to_db(topics):
    """Saves topics to SQLite, ignoring duplicates based on unique URL."""
    inserted_count = 0
    with get_db() as db:
        cursor = db.cursor()
        for t in topics:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO topics (url, title, source, snippet, status)
                    VALUES (?, ?, ?, ?, 'pending')
                """, (t["url"], t["title"], t["source"], t["snippet"]))
                if cursor.rowcount > 0:
                    inserted_count += 1
            except Exception as e:
                print(f"DB insert error: {e}")
        db.commit()
    return inserted_count