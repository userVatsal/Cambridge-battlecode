#!/usr/bin/env python3
"""Evaluate one bot against another on every map, playing both sides.

Usage:
    python tools/run_matches.py                       # goldrush vs starter-python
    python tools/run_matches.py --bot goldrush --opponent goldrush-v0 --jobs 2
    python tools/run_matches.py --maps expanse lanes

Prints a per-map table and an overall win rate, and writes a JSON summary to
results/<bot>_vs_<opponent>.json so changes can be compared over time.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def all_maps() -> list[str]:
    return sorted(p.stem for p in (ROOT / "maps").glob("*.map26a"))


def build(bot: str) -> None:
    subprocess.run(["cambc", "build", f"bots/{bot}"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def run(bot: str, opponent: str, maps: list[str], jobs: int) -> list[dict]:
    work = Path(tempfile.mkdtemp(prefix="cambc-eval-"))
    rows, games = [], []
    for name in maps:
        for side, (a, b) in enumerate(((bot, opponent), (opponent, bot))):
            stats = work / f"{name}-{side}.json"
            replay = work / f"{name}-{side}.repl26a"
            rows.append(f"{ROOT}/bots/{a} {ROOT}/bots/{b} {ROOT}/maps/{name}.map26a {replay} --statistics {stats} --json")
            games.append({"map": name, "bot_side": "teamA" if side == 0 else "teamB", "stats": stats})
    manifest = work / "manifest.txt"
    manifest.write_text("\n".join(rows) + "\n")
    subprocess.run(["cambc", "run-batch", str(manifest), "--jobs", str(jobs)], cwd=ROOT,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    results = []
    for game in games:
        result = {"map": game["map"], "bot_side": game["bot_side"]}
        try:
            data = json.loads(game["stats"].read_text())
            gems = {t["team"]: int(t["submittedGems"]) for t in data["teams"]}
            other = "teamB" if game["bot_side"] == "teamA" else "teamA"
            result.update(
                won=data["match"]["outcome"] == game["bot_side"],
                rounds=data["match"]["roundsStarted"],
                gems=gems[game["bot_side"]],
                opp_gems=gems[other],
                faults=data["diagnostics"]["botFaults"][game["bot_side"]],
            )
        except (OSError, KeyError, ValueError) as error:
            result.update(won=False, error=str(error))
        results.append(result)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bot", default="goldrush")
    parser.add_argument("--opponent", default="starter-python")
    parser.add_argument("--maps", nargs="*", default=None)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()

    maps = args.maps or all_maps()
    for name in {args.bot, args.opponent}:
        build(name)
    results = run(args.bot, args.opponent, maps, args.jobs)

    print(f"{'map':<12}{'side':<7}{'result':<8}{'round':>6}{'gems':>7}{'opp':>7}")
    for r in results:
        if "error" in r:
            print(f"{r['map']:<12}{r['bot_side']:<7}ERROR   {r['error']}")
            continue
        print(f"{r['map']:<12}{r['bot_side']:<7}{'WIN' if r['won'] else 'loss':<8}"
              f"{r['rounds']:>6}{r['gems']:>7}{r['opp_gems']:>7}")
    wins = sum(r["won"] for r in results)
    print(f"\n{args.bot} vs {args.opponent}: {wins}/{len(results)} wins")

    out = ROOT / "results" / f"{args.bot}_vs_{args.opponent}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"wins": wins, "games": len(results), "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
