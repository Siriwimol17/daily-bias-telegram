#!/usr/bin/env python3
"""
Daily Bias Analyzer for XAUUSD + US100
Sends summary to Telegram every 4 hours via GitHub Actions
"""

import os
import requests
from datetime import datetime, timedelta
import pytz
import yfinance as yf
import pandas as pd

# ============== CONFIG ==============
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

THAI_TZ = pytz.timezone("Asia/Bangkok")
ET_TZ = pytz.timezone("America/New_York")  # UTC-4 / UTC-5

SYMBOLS = {
    "XAUUSD": "GC=F",      # Gold Futures as proxy
    "US100": "NQ=F",       # Nasdaq 100 Futures as proxy
}


def send_telegram(message: str):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        print(message)
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        print("Telegram sent successfully")
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False


def get_ohlc(symbol: str, period: str = "10d", interval: str = "1d") -> pd.DataFrame:
    """Fetch OHLC data"""
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()


def analyze_symbol(name: str, yf_symbol: str) -> dict:
    """Basic analysis for one symbol"""
    result = {
        "name": name,
        "error": None,
        "pdh": None,
        "pdl": None,
        "eq": None,
        "last_close": None,
        "last_open": None,
        "last_high": None,
        "last_low": None,
        "prev_close_near": None,
        "week_high": None,
        "week_low": None,
        "bias": "Neutral",
        "confidence": "Low",
        "note": "",
    }

    df = get_ohlc(yf_symbol, period="15d", interval="1d")
    if df.empty or len(df) < 3:
        result["error"] = "ไม่สามารถดึงข้อมูลราคาได้"
        return result

    # Latest completed day
    last = df.iloc[-1]
    prev = df.iloc[-2]

    result["last_open"] = round(float(last["Open"]), 2)
    result["last_high"] = round(float(last["High"]), 2)
    result["last_low"] = round(float(last["Low"]), 2)
    result["last_close"] = round(float(last["Close"]), 2)

    result["pdh"] = round(float(prev["High"]), 2)
    result["pdl"] = round(float(prev["Low"]), 2)
    result["eq"] = round((result["pdh"] + result["pdl"]) / 2, 2)

    # Where did previous day close?
    prev_range = float(prev["High"]) - float(prev["Low"])
    if prev_range > 0:
        close_pos = (float(prev["Close"]) - float(prev["Low"])) / prev_range
        if close_pos > 0.7:
            result["prev_close_near"] = "ใกล้ High (Bullish close)"
        elif close_pos < 0.3:
            result["prev_close_near"] = "ใกล้ Low (Bearish close)"
        else:
            result["prev_close_near"] = "กลาง Range"

    # Simple week high/low (last 5 trading days)
    recent = df.tail(5)
    result["week_high"] = round(float(recent["High"].max()), 2)
    result["week_low"] = round(float(recent["Low"].min()), 2)

    # Very simple bias heuristic
    if result["last_close"] > result["pdh"]:
        result["bias"] = "Bullish"
        result["confidence"] = "Medium"
        result["note"] = "ราคาอยู่เหนือ PDH"
    elif result["last_close"] < result["pdl"]:
        result["bias"] = "Bearish"
        result["confidence"] = "Medium"
        result["note"] = "ราคาอยู่ใต้ PDL"
    else:
        result["bias"] = "Neutral"
        result["confidence"] = "Low"
        result["note"] = "ราคายังอยู่ใน range วันก่อน"

    return result


def format_message(analyses: list) -> str:
    """Create Telegram message"""
    now_thai = datetime.now(THAI_TZ).strftime("%Y-%m-%d %H:%M")
    now_et = datetime.now(ET_TZ).strftime("%Y-%m-%d %H:%M")

    lines = [
        f"📊 <b>Daily Bias Update</b>",
        f"🕐 ไทย: {now_thai} | ET: {now_et}",
        "",
    ]

    for a in analyses:
        lines.append(f"━━━━━━━━━━━━━━━━")
        lines.append(f"<b>{a['name']}</b>")

        if a.get("error"):
            lines.append(f"⚠️ {a['error']}")
            continue

        lines.append(f"• Last Close: <code>{a['last_close']}</code>")
        lines.append(f"• PDH: <code>{a['pdh']}</code> | PDL: <code>{a['pdl']}</code>")
        lines.append(f"• EQ: <code>{a['eq']}</code>")
        lines.append(f"• Week H/L: <code>{a['week_high']}</code> / <code>{a['week_low']}</code>")
        lines.append(f"• Prev Close: {a['prev_close_near']}")
        lines.append(f"• Bias: <b>{a['bias']}</b> ({a['confidence']})")
        lines.append(f"• Note: {a['note']}")
        lines.append("")

    lines.append("━━━━━━━━━━━━━━━━")
    lines.append("<i>ข้อมูลจาก yfinance (GC=F / NQ=F) เป็น proxy</i>")
    lines.append("<i>ยังต้องยืนยันด้วยตา + CISD บน H1/4H</i>")

    return "\n".join(lines)


def main():
    print("Starting bias analysis...")
    analyses = []
    for name, symbol in SYMBOLS.items():
        print(f"Analyzing {name} ({symbol})...")
        analyses.append(analyze_symbol(name, symbol))

    message = format_message(analyses)
    print(message)
    send_telegram(message)
    print("Done.")


if __name__ == "__main__":
    main()
