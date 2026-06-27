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
    item = {"url": url}
    try:
        response = requests.get(url, timeout=120, headers={"User-Agent": "Data-Driven-em-Campo-2022/1.0"})
        item["status_code"] = response.status_code
        response.raise_for_status()
        html = response.text
        (out / f"{name}.html").write_text(html, encoding="utf-8")
        soup = BeautifulSoup(html, "lxml")
        footballboxes = soup.select("table.footballbox")
        item["html_bytes"] = len(response.content)
        item["footballbox_count"] = len(footballboxes)
        item["first_footballbox_text"] = footballboxes[0].get_text(" | ", strip=True) if footballboxes else None
        try:
            tables = pd.read_html(StringIO(html))
        except Exception as exc:
            item["table_parse_error"] = f"{type(exc).__name__}: {exc}"
            tables = []
        table_summaries = []
        for i, table in enumerate(tables):
            table_summaries.append({
                "index": i,
                "shape": list(table.shape),
                "columns": [str(c) for c in table.columns],
                "head": table.head(2).astype(str).to_dict(orient="records"),
            })
        item["table_count"] = len(tables)
        item["tables"] = table_summaries
    except Exception as exc:
        item["error"] = f"{type(exc).__name__}: {exc}"
    report[name] = item
(out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: {"status_code": v.get("status_code"), "footballbox_count": v.get("footballbox_count"), "table_count": v.get("table_count"), "error": v.get("error"), "table_parse_error": v.get("table_parse_error")} for k, v in report.items()}, indent=2))
