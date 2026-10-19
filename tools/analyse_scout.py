#!/usr/bin/env python3
"""Analyse data downloaded by fetch_matches.py: team strength, champion and first-pick win rates
(raw and corrected for team strength), and what winners buy.

Usage: python tools/analyse_scout.py [data-dir]     (default: data/)
"""
import collections
import glob
import json
import statistics as st
import sys
from pathlib import Path


def load(data: Path):
    names = {}
    for f in glob.glob(str(data / "teams" / "*.json")):
        for m in json.load(open(f)):
            names[m["matchId"]] = {t["side"]: t["name"] for t in m["teams"]}
    games = []
    for f in glob.glob(str(data / "summaries" / "*.json")):
        try:
            s = json.load(open(f))
        except ValueError:
            continue
        if s.get("match", {}).get("outcome") in ("teamA", "teamB"):
            games.append((Path(f).stem, s, s["match"]["outcome"]))
    return names, games


def main() -> int:
    data = Path(sys.argv[1] if len(sys.argv) > 1 else "data")
    names, games = load(data)
    print(f"{len(games)} finished games")
    wins, played = collections.Counter(), collections.Counter()
    for mid, _, out in games:
        for side, team in (("a", "teamA"), ("b", "teamB")):
            name = names.get(mid, {}).get(side, "?")
            played[name] += 1
            wins[name] += out == team
    rate = {n: wins[n] / played[n] for n in played}
    print("\nTeams (40+ games):")
    for n in sorted(played, key=lambda n: -rate[n]):
        if played[n] >= 40:
            print(f"  {n:32} {wins[n]}/{played[n]} = {100 * rate[n]:.0f}%")

    lift, first_lift = collections.defaultdict(list), collections.defaultdict(list)
    for mid, s, out in games:
        picks = collections.defaultdict(list)
        for d in s["roster"]["draft"]:
            picks[d["team"]].append(d["champion"])
        for side, team in (("a", "teamA"), ("b", "teamB")):
            base = rate.get(names.get(mid, {}).get(side, "?"), 0.5)
            won = out == team
            for c in set(picks[team]):
                lift[c].append(won - base)
            if picks[team]:
                first_lift[picks[team][0]].append(won - base)
    print("\nChampion win lift over the team's own win rate (percentage points):")
    for c, v in sorted(lift.items(), key=lambda kv: -st.mean(kv[1])):
        print(f"  {c:16} {100 * st.mean(v):+5.1f}  n={len(v)}")
    print("\nFirst-pick lift:")
    for c, v in sorted(first_lift.items(), key=lambda kv: -st.mean(kv[1])):
        if len(v) >= 30:
            print(f"  {c:16} {100 * st.mean(v):+5.1f}  n={len(v)}")

    win, lose = collections.defaultdict(list), collections.defaultdict(list)
    for _, s, out in games:
        for c in s["champions"]:
            target = win if c["team"] == out else lose
            for key in ("deaths", "kills", "earnedGold", "spentGold", "collectedGems", "submittedGems"):
                target[key].append(float(c["metrics"][key]))
    print("\nPer-champion medians, winners vs losers:")
    for key in win:
        print(f"  {key:14} {st.median(win[key]):7.0f} vs {st.median(lose[key]):7.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
