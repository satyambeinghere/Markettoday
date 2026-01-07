import json
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

import yfinance as yf
import feedparser
from groq import Groq

# ✅ IMPORT FORMATTER
from formatter import build_final_message

# ---------------- CONFIG ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CACHE_DIR = "cache"

client = Groq(api_key=GROQ_API_KEY)

# ---------------- HELPERS ----------------
def get_market_data():
    nifty = yf.Ticker("^NSEI").history(period="1d")
    sensex = yf.Ticker("^BSESN").history(period="1d")

    if nifty.empty or sensex.empty:
        return {"nifty_change": 0, "sensex_change": 0}

    return {
        "nifty_change": round(
            ((nifty["Close"].iloc[0] - nifty["Open"].iloc[0]) / nifty["Open"].iloc[0]) * 100, 2
        ),
        "sensex_change": round(
            ((sensex["Close"].iloc[0] - sensex["Open"].iloc[0]) / sensex["Open"].iloc[0]) * 100, 2
        )
    }

def get_news():
    feed = feedparser.parse("https://www.moneycontrol.com/rss/marketreports.xml")
    return [entry.title for entry in feed.entries[:5]]

def ai_summary(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# ---------------- MAIN LOGIC ----------------
def generate():
    market = get_market_data()
    news = get_news()

    # -------- FREE PROMPT --------
    free_prompt = f"""
You are a calm market teacher explaining the Indian stock market to complete beginners.

Create a DAILY INDIAN STOCK MARKET SUMMARY in SIMPLE ENGLISH using the EXACT format below.

Title: Market Summary for Beginners

1. Market Snapshot
- NIFTY: moved <up/down> by <percentage> today
- SENSEX: moved <up/down> by <percentage> today

2. What happened today?
Explain in 2–3 VERY SIMPLE sentences.

3. Main Reasons (Simple)
List 3–4 simple reasons.

4. Simple Takeaway
ONE short sentence describing today’s market mood.

Data:
- NIFTY change: {market['nifty_change']}%
- SENSEX change: {market['sensex_change']}%
- News headlines: {news}
"""

    # -------- PREMIUM PROMPT --------
    premium_prompt = f"""
You are an experienced Indian market observer writing for thoughtful retail investors.

Create a DAILY PREMIUM MARKET NOTE.

1. Market Overview
2. Market Mood
3. What Could Matter Next (Educational)
4. Learning Point

Market data:
{market}

News headlines:
{news}
"""

    # 🔹 AI GENERATES CONTENT ONLY
    free_ai_content = ai_summary(free_prompt)
    premium_ai_content = ai_summary(premium_prompt)

    # 🔹 FORMATTER ADDS HEADER + FOOTER
    free_summary = build_final_message(free_ai_content)
    premium_summary = build_final_message(premium_ai_content)

    # ---------------- SAVE CACHE ----------------
    os.makedirs(CACHE_DIR, exist_ok=True)

    with open(f"{CACHE_DIR}/free.json", "w") as f:
        json.dump({
            "updated_at": str(datetime.now()),
            "content": free_summary
        }, f, indent=2)

    with open(f"{CACHE_DIR}/premium.json", "w") as f:
        json.dump({
            "updated_at": str(datetime.now()),
            "content": premium_summary
        }, f, indent=2)

    print("✅ Cache updated with formatted content")

if __name__ == "__main__":
    generate()
