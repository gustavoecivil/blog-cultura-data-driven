from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

URLS = {
    "tournament": "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup",
    "officials": "https://en.wikipedia.org/wiki/2022_FIFA_World_Cup_officials",
}

out = Path("/tmp/external_probe")
out.mkdir(parents=True, exist_ok=True)
report = {}
for name, url in URLS.items():
    response = requests.get(url, timeout=120, headers={"User-Agent": "Data-Driven-em-Campo-2022/1.0"})
    response.raise_for_status()
    html = response.text
    (out / f"{name}.html").write_text(html, encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    footballboxes = soup.select("table.footballbox")
    tables = pd.read_html(StringIO(html))
    table_summaries = []
    for i, table in enumerate(tables):
        table_summaries.append({
            "index": i,
            "shape": list(table.shape),
            "columns": [str(c) for c in table.columns],
            "head": table.head(2).astype(str).to_dict(orient="records"),
        })
    report[name] = {
        "url": url,
        "html_bytes": len(response.content),
        "footballbox_count": len(footballboxes),
        "first_footballbox_text": footballboxes[0].get_text(" | ", strip=True) if footballboxes else None,
        "table_count": len(tables),
        "tables": table_summaries,
    }
(out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: {"footballbox_count": v["footballbox_count"], "table_count": v["table_count"]} for k, v in report.items()}, indent=2))
