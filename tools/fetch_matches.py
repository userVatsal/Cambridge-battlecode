#!/usr/bin/env python3
"""Download every match the top ladder teams have played, as JSON, using the official cambc CLI.

Needs `cambc login` first (sessions last seven days). Run from the repo root with the venv on.

Usage:
    python tools/fetch_matches.py fetch --top 12            # top 12 ladder teams, all their matches
    python tools/fetch_matches.py fetch --team <TEAM_ID>    # one team
    python tools/fetch_matches.py fetch --top 12 --replays  # also download replay bundles (large)
    python tools/fetch_matches.py report                    # what winners draft, how fast they win

Output (resumable — files already downloaded are skipped):
    data/ladder.json               ladder snapshot
    data/teams/<team_id>.json      that team's match list, as returned by the platform
    data/summaries/<match_id>.json official per-match statistics (same format as `cambc run --statistics`)
    data/replays/<match_id>.zip    replay bundles (only with --replays)
    data/index.json                one row per match: map, teams, winner, drafts, gems, rounds

Uses only the platform's own CLI commands (ladder, matches list, matches summary, matches download),
so it sees exactly what the website shows any signed-in competitor. It pauses between requests.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PAUSE_SECONDS = 1.0
MAX_RETRIES = 8
CURSOR_KEYS = ("cursor", "next", "nextCursor", "next_cursor")


def run_cambc(args: list[str]) -> subprocess.CompletedProcess:
    """Run cambc, waiting and retrying when the platform says it is busy (HTTP 429)."""
    for attempt in range(MAX_RETRIES):
        result = subprocess.run(["cambc", *args], capture_output=True, text=True)
        time.sleep(PAUSE_SECONDS)
        message = result.stderr + result.stdout
        if result.returncode == 0 or "429" not in message:
            return result
        match = re.search(r"retry after (\d+)", message)
        wait = int(match.group(1)) + 1 if match else 2 ** attempt
        print(f"  platform busy, waiting {wait}s (attempt {attempt + 1}/{MAX_RETRIES})")
        time.sleep(wait)
    return result


def cambc_json(*args: str):
    result = run_cambc([*args, "--json"])
    if result.returncode != 0:
        raise RuntimeError(f"cambc {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}")
    return json.loads(result.stdout)


def first_list(payload):
    """The platform wraps lists in an object; return the first list of objects found."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, list) and (not value or isinstance(value[0], dict)):
                return value
    return []


def pick(row: dict, *keys, default=None):
    for key in keys:
        if isinstance(row, dict) and row.get(key) is not None:
            return row[key]
    return default


def top_teams(count: int) -> list[dict]:
    teams, page = [], 1
    while len(teams) < count:
        payload = cambc_json("ladder", "--page", str(page), "--limit", "25")
        rows = first_list(payload)
        if page == 1:
            (DATA / "ladder.json").write_text(json.dumps(payload, indent=1))
        if not rows:
            break
        for row in rows:
            team = row.get("team") if isinstance(row.get("team"), dict) else row
            team_id = pick(team, "id", "teamId", "team_id")
            if team_id:
                teams.append({"id": team_id, "name": pick(team, "name", "teamName", default=team_id)})
        page += 1
    if not teams:
        raise RuntimeError("Could not read team ids from `cambc ladder --json`; see data/ladder.json")
    return teams[:count]


def team_matches(team_id: str, refresh: bool) -> list[dict]:
    cached = DATA / "teams" / f"{team_id}.json"
    if cached.exists() and not refresh:
        return json.loads(cached.read_text())
    matches, cursor = [], None
    while True:
        args = ["matches", "list", "--team", team_id, "--limit", "100"]
        if cursor:
            args += ["--cursor", str(cursor)]
        payload = cambc_json(*args)
        page = first_list(payload)
        matches += page
        cursor = next((payload.get(k) for k in CURSOR_KEYS if isinstance(payload, dict) and payload.get(k)), None)
        if not page or not cursor:
            break
    (DATA / "teams" / f"{team_id}.json").write_text(json.dumps(matches, indent=1))
    return matches


def download_summary(match_id: str) -> bool:
    out = DATA / "summaries" / f"{match_id}.json"
    if out.exists():
        return False
    result = run_cambc(["matches", "summary", match_id, "--json", "-o", str(out)])
    if result.returncode != 0:
        print(f"  summary {match_id} failed: {result.stderr.strip()[:200]}")
        return False
    return True


def download_replay(match_id: str) -> None:
    out = DATA / "replays" / f"{match_id}.zip"
    if not out.exists():
        run_cambc(["matches", "download", match_id, "-o", str(out)])


def index_row(match_id: str, listing: dict) -> dict | None:
    path = DATA / "summaries" / f"{match_id}.json"
    if not path.exists():
        return None
    try:
        stats = json.loads(path.read_text())
    except ValueError:
        return None
    match = stats.get("match", {})
    gems = {t["team"]: int(t.get("submittedGems", 0)) for t in stats.get("teams", [])}
    draft = collections.defaultdict(list)
    for pick_row in stats.get("roster", {}).get("draft", []):
        draft[pick_row["team"]].append(pick_row["champion"])
    names = {"teamA": pick(listing, "teamA", "team_a", "teamAName"), "teamB": pick(listing, "teamB", "team_b", "teamBName")}
    for side in names:
        if isinstance(names[side], dict):
            names[side] = pick(names[side], "name", "id")
    return {
        "match_id": match_id,
        "map": pick(listing, "map", "mapName", default=""),
        "team_a": names["teamA"], "team_b": names["teamB"],
        "winner": match.get("outcome"),
        "rounds": match.get("roundsStarted"),
        "gems_a": gems.get("teamA"), "gems_b": gems.get("teamB"),
        "draft_a": draft.get("teamA", []), "draft_b": draft.get("teamB", []),
    }


def cmd_fetch(args) -> int:
    for sub in ("teams", "summaries", "replays"):
        (DATA / sub).mkdir(parents=True, exist_ok=True)
    teams = [{"id": args.team, "name": args.team}] if args.team else top_teams(args.top)
    listings: dict[str, dict] = {}
    for n, team in enumerate(teams, 1):
        matches = team_matches(team["id"], args.refresh)
        print(f"[{n}/{len(teams)}] {team['name']}: {len(matches)} matches")
        for m in matches:
            match_id = pick(m, "id", "matchId", "match_id")
            if match_id:
                listings[match_id] = m
    new = 0
    for n, match_id in enumerate(listings, 1):
        new += download_summary(match_id)
        if args.replays:
            download_replay(match_id)
        if n % 25 == 0:
            print(f"  {n}/{len(listings)} matches processed ({new} new summaries)")
    rows = [r for r in (index_row(mid, lst) for mid, lst in listings.items()) if r]
    (DATA / "index.json").write_text(json.dumps(rows, indent=1))
    print(f"\n{len(listings)} matches, {new} new summaries, index of {len(rows)} -> data/index.json")
    return 0


def cmd_report(_args) -> int:
    rows = json.loads((DATA / "index.json").read_text())
    winners, losers, first_picks, rounds = collections.Counter(), collections.Counter(), collections.Counter(), []
    for r in rows:
        if r["winner"] not in ("teamA", "teamB"):
            continue
        w, lose = ("a", "b") if r["winner"] == "teamA" else ("b", "a")
        winners.update(r[f"draft_{w}"])
        losers.update(r[f"draft_{lose}"])
        if r[f"draft_{w}"]:
            first_picks[r[f"draft_{w}"][0]] += 1
        if r["rounds"]:
            rounds.append(r["rounds"])
    print(f"{len(rows)} matches")
    print("winner picks:     ", winners.most_common())
    print("loser picks:      ", losers.most_common())
    print("winner first pick:", first_picks.most_common())
    if rounds:
        rounds.sort()
        print(f"rounds to finish: median {rounds[len(rounds) // 2]}, fastest {rounds[0]}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    fetch = sub.add_parser("fetch")
    who = fetch.add_mutually_exclusive_group()
    who.add_argument("--top", type=int, default=12, help="number of ladder teams (default 12)")
    who.add_argument("--team", help="a single team id")
    fetch.add_argument("--replays", action="store_true", help="also download replay bundles")
    fetch.add_argument("--refresh", action="store_true", help="re-download team match lists already saved")
    sub.add_parser("report")
    args = parser.parse_args()
    try:
        return cmd_fetch(args) if args.cmd == "fetch" else cmd_report(args)
    except (RuntimeError, FileNotFoundError, json.JSONDecodeError) as error:
        print(f"error: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
