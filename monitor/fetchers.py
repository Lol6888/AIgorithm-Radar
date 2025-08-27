import hashlib
import time
import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Tuple, Optional
try:
    import trafilatura
except Exception:
    trafilatura = None

HEADERS = {
    "User-Agent": "126V-Algorithm-Radar/1.0 (+https://example.com)"
}

def get_url(url: str, timeout: int = 25) -> Tuple[str, str]:
    """Return (content, content_type) for a URL with polite headers."""
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    ctype = r.headers.get("Content-Type", "")
    return r.text, ctype

def extract_main_text(html: str) -> str:
    """Try to extract main article text; fallback to stripped body text."""
    if trafilatura:
        try:
            text = trafilatura.extract(html) or ""
            if text.strip():
                return text
        except Exception:
            pass
    soup = BeautifulSoup(html, "lxml")
    # Remove scripts/styles
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    body = soup.get_text("\n", strip=True)
    # Keep it compact
    lines = [ln for ln in body.splitlines() if ln.strip()]
    return "\n".join(lines)

def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def parse_rss(url: str):
    return feedparser.parse(url)

def polite_sleep(sec: float = 1.2):
    time.sleep(sec)
