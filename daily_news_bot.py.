import os 
import feedparser
import requests
from datetime import datetime

# ==========================================
# 1. CONFIGURATION
# ==========================================

GROQ_API_KEY = os.environ.get("GROQ_API_KEY") 

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

FEEDS = {
    " AI & Tech": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"
    ],
    "💰 Finance": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    ],
    "⚽ Football": [
        "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "https://www.espn.com/espn/rss/soccer/news"
    ]
}

# ==========================================
# 2. FETCH NEWS
# ==========================================
def get_latest_news():
    news_data = {}
    for category, urls in FEEDS.items():
        items = []
        for url in urls:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]: 
                items.append({
                    "title": entry.title,
                    "link": entry.link
                })
        news_data[category] = items
    return news_data

# ==========================================
# 3. AI SUMMARIZATION (GROQ)
# ==========================================
def summarize_with_ai(news_data):
    prompt = "You are a morning news anchor. Based on these headlines, write a very brief, 1-sentence summary for each category. Keep it punchy, exciting, and easy to read.\n\n"
    for cat, items in news_data.items():
        prompt += f"{cat}: {', '.join([i['title'] for i in items])}\n"
    prompt += "\nFormat the output nicely with emojis."

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"AI Summary unavailable today. Error: {e}"

# ==========================================
# 4. SEND TO TELEGRAM
# ==========================================
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML" # Allows bold text and links
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.json().get("ok"):
            print("✅ Morning digest sent to Telegram!")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

# ==========================================
# 5. MAIN EXECUTION
# ==========================================
def main():
    print(" Fetching news...")
    raw_news = get_latest_news()
    
    print("🧠 Summarizing with AI...")
    ai_summary = summarize_with_ai(raw_news)
    
    # Build the final message using HTML for Telegram
    final_message = f"<b>🌅 Good Morning! Here is your Daily Digest for {datetime.now().strftime('%b %d, %Y')}</b>\n\n"
    final_message += ai_summary + "\n\n"
    final_message += "<b>👇 Read the full stories:</b>\n"
    
    for category, items in raw_news.items():
        final_message += f"\n<b>{category}</b>\n"
        for item in items:
            # Create a clickable link for Telegram
            final_message += f"• <a href=\"{item['link']}\">{item['title']}</a>\n"
            
    send_to_telegram(final_message)

if __name__ == "__main__":
    main()
