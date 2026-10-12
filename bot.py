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

# We fetch 10 articles per source now!
FEEDS = {
    "🤖 New AI Launches & Tech": [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "https://feeds.feedburner.com/TheHackersNews" 
    ],
    "💰 Finance & Business": [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    ],
    "⚽ Sports & Football": [
        "http://feeds.bbci.co.uk/sport/football/rss.xml",
        "https://www.espn.com/espn/rss/soccer/news"
    ],
    "🌍 World News": [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"
    ]
}

# ==========================================
# 2. FETCH NEWS (Now gets 10 items!)
# ==========================================
def get_latest_news():
    news_data = {}
    for category, urls in FEEDS.items():
        items = []
        for url in urls:
            feed = feedparser.parse(url)
            # Changed from 3 to 10 to get more news
            for entry in feed.entries[:10]: 
                items.append({
                    "title": entry.title,
                    "link": entry.link
                })
        news_data[category] = items
    return news_data

# ==========================================
# 3. AI SUMMARIZATION (The New Brain)
# ==========================================
def summarize_with_ai(news_data):
    # We format the data nicely for the AI first
    formatted_data = ""
    for cat, items in news_data.items():
        formatted_data += f"--- {cat} ---\n"
        for item in items:
            formatted_data += f"- {item['title']}\n"
        formatted_data += "\n"

    # The new prompt asks for summaries, not just a list
    prompt = f"""You are an expert morning news anchor. I have fetched headlines for several categories. 
    For EACH category:
    1. Write a 5-sentence summary of the biggest trends or news in that category today.
    2. List the top 3 most important headlines from that category, and for each, write a 1-sentence explanation of what it means.
    
    Keep it punchy, engaging, and easy to read on a mobile screen. Use emojis.
    
    Here is the raw data:
    {formatted_data}
    """

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    # Using a very stable model
    data = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        res_json = response.json()
        
        # Check if the AI actually worked
        if 'choices' in res_json:
            return res_json['choices'][0]['message']['content']
        else:
            # This will tell us if it was a rate limit error!
            return f"AI Error: {res_json}"
            
    except Exception as e:
        return f"Code Error: {e}"

# ==========================================
# 4. SEND TO TELEGRAM
# ==========================================
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML" 
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.json().get("ok"):
            print("✅ Morning digest sent to Telegram!")
        else:
            print(f"❌ Telegram Failed: {response.text}")
    except Exception as e:
        print(f" Error: {e}")

# ==========================================
# 5. MAIN EXECUTION
# ==========================================
def main():
    print("📡 Fetching news...")
    raw_news = get_latest_news()
    
    print("🧠 Summarizing with AI...")
    ai_summary = summarize_with_ai(raw_news)
    
    # Build the final message
    final_message = f"<b>🌅 Good Morning! Here is your Daily Digest for {datetime.now().strftime('%b %d, %Y')}</b>\n\n"
    final_message += ai_summary + "\n\n"
    final_message += "<i>Want to read more? Check the full articles on the websites!</i>"
            
    send_to_telegram(final_message)

if __name__ == "__main__":
    main()
