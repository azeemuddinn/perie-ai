import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def send_brief_to_slack(brief_data: dict) -> str:
    """Sends the formatted agent brief to Slack using Slack's official Web API."""
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    default_channel = os.getenv("SLACK_CHANNEL_ID", "#general")
    
    if not slack_token:
        raise ValueError("SLACK_BOT_TOKEN is missing in environment variables.")

    message = (
        f"🚨 *PerieAI Daily Tech Brief*\n\n"
        f"📌 *Topic:* {brief_data['selected_title']}\n"
        f"📝 *Suggested Title:* {brief_data['suggested_blog_title']}\n"
        f"💡 *Why It Matters:* {brief_data['why_it_matters']}\n\n"
        f"📋 *Outline:*\n" + "\n".join(f"• {item}" for item in brief_data['suggested_outline']) + "\n\n"
        f"🔗 *Source:* {brief_data['source_links'][0]}\n"
        f"⭐ *Evaluation Score:* {brief_data['evaluation_score']}"
    )

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": default_channel,
        "text": message
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Slack API Error: {data.get('error')}")
        return f"Message posted successfully to channel {default_channel}"