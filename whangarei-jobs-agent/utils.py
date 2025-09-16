import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from dateutil import parser

NZT = ZoneInfo("Pacific/Auckland")

def compile_region(pattern:str):
    return re.compile(pattern, re.I)

def in_region(location:str, rx)->bool:
    return bool(rx.search(location or ""))

def match_keywords(text:str, keywords)->bool:
    t = (text or "").lower()
    return any(kw.lower() in t for kw in keywords)

def parse_deadline(text:str)->str:
    if not text: return ""
    m = re.search(r"(\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})|(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text)
    if not m: return ""
    try:
        dt = parser.parse(m.group(0), dayfirst=True).date()
        return dt.isoformat()
    except Exception:
        return ""

def today_str()->str:
    return datetime.now(NZT).strftime("%Y-%m-%d")
