# Optional: correlate internal metrics (CSV) with change dates using ruptures
import os, pathlib, json, pandas as pd, numpy as np
from datetime import datetime, timedelta
from jinja2 import Template
import ruptures as rpt

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = ROOT / "data"
DOCS.mkdir(exist_ok=True)
DATA.mkdir(exist_ok=True)

def load_events():
    arch = DOCS / "archive.json"
    if arch.exists():
        return json.loads(arch.read_text(encoding="utf-8"))
    return []

def detect_changepoints(series: pd.Series, model="l2", pen=10):
    """Return list of indices where change is detected."""
    y = series.values.astype(float)
    algo = rpt.Pelt(model=model).fit(y)
    idxs = algo.predict(pen=pen)
    # ruptures returns end indexes of segments; convert to 0-based change points
    return [i-1 for i in idxs if i-1 >= 0 and i-1 < len(series)]

def correlate(events, df):
    # Expect df with columns: date, platform, metric, value
    df["date"] = pd.to_datetime(df["date"])
    out_rows = []
    for (plat, metric), g in df.groupby(["platform", "metric"]):
        g = g.sort_values("date")
        g = g.set_index("date").asfreq("D").interpolate()
        cps = detect_changepoints(g["value"])
        cp_dates = [g.index[i] for i in cps]
        # match events within +/- 7 days
        for ev in events:
            ev_date = pd.to_datetime(ev.get("date", None), errors="coerce")
            if pd.isna(ev_date):
                continue
            for cp in cp_dates:
                if abs((cp - ev_date).days) <= 7:
                    out_rows.append({
                        "platform": plat, "metric": metric,
                        "change_point": cp.date().isoformat(),
                        "event_title": ev.get("title", ""),
                        "event_date": ev.get("date", ""),
                        "source": ev.get("url", "")
                    })
    return pd.DataFrame(out_rows)

def main():
    metrics = DATA / "metrics.csv"
    if not metrics.exists():
        # Create a sample
        (DATA / "metrics.csv").write_text(
            "date,platform,metric,value\n"
            "2025-07-01,linkedin,reach,100\n"
            "2025-07-02,linkedin,reach,98\n"
            "2025-07-10,linkedin,reach,130\n",
            encoding="utf-8"
        )
    df = pd.read_csv(metrics)
    events = load_events()
    corr = correlate(events, df)
    # Render very simple HTML
    rows = "".join([f"<tr><td>{r.platform}</td><td>{r.metric}</td><td>{r.change_point}</td>"
                    f"<td>{r.event_title}</td><td>{r.event_date}</td>"
                    f"<td><a href='{r.source}'>link</a></td></tr>"
                    for r in corr.itertuples(index=False)])
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Correlation</title></head>
<body>
<h2>Kết hợp mốc change-point (metrics) với events</h2>
<table border="1" cellspacing="0" cellpadding="6">
<tr><th>Platform</th><th>Metric</th><th>Change Point</th><th>Event</th><th>Event Date</th><th>Source</th></tr>
{rows if rows else "<tr><td colspan='6'>No overlaps</td></tr>"}
</table>
</body></html>"""
    (DOCS / "analysis.html").write_text(html, encoding="utf-8")

if __name__ == "__main__":
    main()
