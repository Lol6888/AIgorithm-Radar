import os, json, pathlib, yaml, datetime
from typing import Dict, Any, List
from jinja2 import Template
from dateutil import tz
from tqdm import tqdm

from .fetchers import get_url, extract_main_text, content_hash, parse_rss, polite_sleep
from .diffing import unified_diff
from .notifier import notify
from .rules import recommend

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "monitor" / "state"
DOCS_DIR = ROOT / "docs"
TEMPLATE_PATH = DOCS_DIR / "_index_template.html"

STATE_DIR.mkdir(parents=True, exist_ok=True)
DOCS_DIR.mkdir(parents=True, exist_ok=True)

RSS_STATE = STATE_DIR / "rss_state.json"
PAGE_STATE = STATE_DIR / "page_state.json"

def load_json(p: pathlib.Path, default):
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return default
    return default

def save_json(p: pathlib.Path, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def read_sources() -> List[Dict[str, Any]]:
    cfg_path = ROOT / "monitor" / "sources.yaml"
    return yaml.safe_load(cfg_path.read_text(encoding="utf-8")).get("sources", [])

def now_str():
    return datetime.datetime.utcnow().replace(tzinfo=tz.UTC).strftime("%Y-%m-%d %H:%M UTC")

def run_once() -> List[Dict[str, Any]]:
    sources = read_sources()
    rss_state = load_json(RSS_STATE, {})
    page_state = load_json(PAGE_STATE, {})

    new_events = []

    for s in tqdm(sources, desc="Monitoring"):
        sid = s["id"]
        stype = s["type"]
        url = s["url"]
        tags = s.get("tags", [])

        if stype == "rss":
            feed = parse_rss(url)
            # feed.entries sorted by published
            last_ids = set(rss_state.get(sid, []))
            fresh_ids = []
            for e in feed.entries[:20]:
                eid = getattr(e, "id", "") or getattr(e, "link", "")
                title = getattr(e, "title", "RSS item")
                link = getattr(e, "link", url)
                if eid and eid not in last_ids:
                    new_events.append({
                        "source_id": sid,
                        "title": title,
                        "url": link,
                        "tags": tags,
                        "date": getattr(e, "published", "") or now_str(),
                        "summary": getattr(e, "summary", "")[:500]
                    })
                    fresh_ids.append(eid)
            # update state (keep last 100 ids to limit file size)
            rss_state[sid] = (list(last_ids) + fresh_ids)[-100:]
            polite_sleep(0.8)

        elif stype == "page":
            try:
                html, ctype = get_url(url)
                text = extract_main_text(html)
                h = content_hash(text)
            except Exception as ex:
                print(f"[WARN] Failed to fetch {url}: {ex}")
                continue

            prev = page_state.get(sid, {})
            prev_hash = prev.get("hash", "")
            prev_text = prev.get("text", "")

            if h != prev_hash and text.strip():
                # Generate a diff
                diff = unified_diff(prev_text, text)
                title = s.get("name", url)
                # short summary = first 400 chars
                summary = text.strip().splitlines()
                summary = " ".join(summary[:6])[:500]

                new_events.append({
                    "source_id": sid,
                    "title": title,
                    "url": url,
                    "tags": tags,
                    "date": now_str(),
                    "summary": summary,
                    "diff": diff
                })

                page_state[sid] = {"hash": h, "text": text}
            polite_sleep(1.0)

    # Persist states
    save_json(RSS_STATE, rss_state)
    save_json(PAGE_STATE, page_state)

    return new_events

def render_dashboard(events: List[Dict[str, Any]]):
    tpl = Template((DOCS_DIR / "_index_template.html").read_text(encoding="utf-8"))
    generated_at = now_str()
    # Keep latest 40
    events = events[:40]
    html = tpl.render(events=events, generated_at=generated_at)
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")

def append_archive(events: List[Dict[str, Any]]):
    """Append events to docs/archive.json for history & dashboard rebuilds."""
    archive_path = DOCS_DIR / "archive.json"
    history = []
    if archive_path.exists():
        try:
            history = json.loads(archive_path.read_text(encoding="utf-8"))
        except Exception:
            history = []
    # Prepend new items (newest first)
    history = events + history
    # Keep last 500
    history = history[:500]
    archive_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    return history

def notify_changes(events: List[Dict[str, Any]]):
    if not events:
        return
    # Build a compact Telegram message (limit ~4k chars)
    lines = ["<b>126V Algorithm Radar — thay đổi mới</b>"]
    for ev in events[:10]:
        rec = recommend(ev.get("tags", []), ev.get("title", ""), ev.get("summary", "") or "")
        lines.append(f"• <b>{ev['title']}</b> — <a href='{ev['url']}'>link</a>")
        if rec:
            lines.append(rec)
    text = "\n".join(lines)
    notify(text)

def main():
    events = run_once()
    # Merge with archive and render latest dashboard
    history = append_archive(events)
    render_dashboard(history)

if __name__ == "__main__":
    # Ensure template exists
    if not TEMPLATE_PATH.exists():
        TEMPLATE_PATH.write_text((ROOT / "docs" / "_index_template.html").read_text(encoding="utf-8"), encoding="utf-8")
    main()
