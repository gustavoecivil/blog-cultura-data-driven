from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SB = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"
OF = "https://raw.githubusercontent.com/openfootball/worldcup.json/master"
UA = "Data-Driven-em-Campo-2022"


def fetch(url: str, path: Path, optional: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(Request(url, headers={"User-Agent": UA}), timeout=120) as response:
            path.write_bytes(response.read())
    except HTTPError as exc:
        if optional and exc.code == 404:
            return
        raise


def main() -> None:
    sb = Path("/tmp/statsbomb/data")
    of = Path("/tmp/openfootball/2022/worldcup.json")
    matches_path = sb / "matches/43/106.json"
    fetch(f"{SB}/competitions.json", sb / "competitions.json")
    fetch(f"{SB}/matches/43/106.json", matches_path)
    fetch(f"{OF}/2022/worldcup.json", of)
    matches = json.loads(matches_path.read_text(encoding="utf-8"))
    for match in matches:
        mid = match["match_id"]
        fetch(f"{SB}/events/{mid}.json", sb / f"events/{mid}.json")
        fetch(f"{SB}/lineups/{mid}.json", sb / f"lineups/{mid}.json")
        fetch(f"{SB}/three-sixty/{mid}.json", sb / f"three-sixty/{mid}.json", optional=True)
    print(json.dumps({"matches": len(matches), "mode": "selective"}))


if __name__ == "__main__":
    main()
