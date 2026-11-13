import os
import httpx
from dotenv import load_dotenv

load_dotenv()


async def send_brief_to_slack(brief_data: dict) -> str:
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    default_channel = os.getenv("SLACK_CHANNEL_ID", "#general")
    
    if not slack_token:
        raise ValueError("SLACK_BOT_TOKEN is missing in environment variables.")

    scorecard = brief_data.get("scorecard", {})
    grade_emoji = "🟢" if scorecard.get("grade") == "PASS" else "🔴"

    message = (
        f"🚨 *PerieAI Daily Tech Brief* {grade_emoji}\n\n"
        f"📌 *Topic:* {brief_data['selected_title']}\n"
        f"📝 *Suggested Title:* {brief_data['suggested_blog_title']}\n"
        f"💡 *Why It Matters:* {brief_data['why_it_matters']}\n\n"
        f"📋 *Outline:*\n" + "\n".join(f"• {item}" for item in brief_data['suggested_outline']) + "\n\n"
        f"🤖 *Editorial Judge Review:*\n"
        f"• *Grade:* `{scorecard.get('grade', 'N/A')}` (Tech Depth: {scorecard.get('technical_depth_score', 0)}/1.0)\n"
        f"• *Critique:* {scorecard.get('critique', 'N/A')}\n\n"
        f"🔗 *Source:* {brief_data['source_links'][0]}"
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