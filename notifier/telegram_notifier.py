import os
import requests

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def send_telegram_alert(
    title: str,
    company: str,
    location: str,
    match_score: int,
    tech_stack: list[str],
    fit_summary: str,
    job_url: str = ""
) -> bool:
    """
    Pushes a high-matching job alert card to Telegram via Bot API.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    chat_id = os.getenv("TELEGRAM_CHAT_ID", TELEGRAM_CHAT_ID)

    if not token or not chat_id:
        print("⚠️ Telegram credentials (TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID) not set. Skipping Telegram notification.")
        return False

    tech_badges = ", ".join([f"`{t}`" for t in tech_stack]) if tech_stack else "N/A"
    
    message = (
        f"🎯 *HIGH-MATCH JOB ALERT!* (Score: *{match_score}/100*)\n\n"
        f"📌 *Role:* {title}\n"
        f"🏢 *Company:* {company}\n"
        f"📍 *Location:* {location}\n\n"
        f"🛠️ *Tech Stack:* {tech_badges}\n\n"
        f"💡 *Fit Summary:* {fit_summary}\n\n"
    )

    if job_url:
        message += f"🔗 [Apply Now]({job_url})"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"✅ Telegram alert sent for {title} @ {company}")
            return True
        else:
            print(f"⚠️ Telegram API error ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"⚠️ Failed to send Telegram alert: {e}")
        return False
