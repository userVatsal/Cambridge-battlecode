#!/usr/bin/env python3
"""Summarise decoded ladder replays: result, gems, kills, deaths and drafts per game.

Input is a directory of JSON files produced by the public replay decoder
(`extract.mjs`, see docs/MATCH_LOG.md). Our team is recognised by its draft,
which always follows config.DRAFT_PRIORITY.

Usage:
    python tools/analyse_replays.py <decoded-json-dir>
"""
import glob
import json
import os
import sys

DRAFT_NAMES = ["Ryth", "Vesper", "Vendetta", "Cassi+Issac", "Stellar", "Prism",
               "Marcella", "Willow", "Ren", "Varg", "Tavi"]
OUR_DRAFT = [9, 0, 4, 6, 10, 1, 2, 8, 5, 3, 7]  # Varg, Ryth, Stellar, Marcella, Tavi, ...


def our_team(drafts):
    for team, picks in enumerate(drafts):
        if picks == OUR_DRAFT[:len(picks)]:
            return team
    return 1


def count_deaths(rounds):
    deaths = [0, 0]
    for before, after in zip(rounds, rounds[1:], strict=False):
        for old, new in zip(before["c"], after["c"], strict=False):
            if old[2] == 1 and new[2] == 0:
                deaths[new[0]] += 1
    return deaths


def summarise(path):
    data = json.load(open(path))
    rounds, final = data["rounds"], data["rounds"][-1]
    us = our_team(data["drafts"])
    them = 1 - us
    gems = final["sg"]
    kills = [sum(c[9] for c in final["c"] if c[0] == team) for team in (0, 1)]
    deaths = count_deaths(rounds)
    return {
        "game": os.path.basename(path)[:-5],
        "won": gems[us] > gems[them],
        "side": "AB"[us],
        "camps": len(data["camps"]),
        "rounds": data["finalRound"],
        "gems": (gems[us], gems[them]),
        "kills": (kills[us], kills[them]),
        "deaths": (deaths[us], deaths[them]),
        "opponent": [DRAFT_NAMES[i] for i in data["drafts"][them]],
    }


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    games = [summarise(p) for p in sorted(glob.glob(os.path.join(folder, "*.json")))]
    for g in games:
        print(f"{g['game']:<14} {'WIN ' if g['won'] else 'loss'} side={g['side']} camps={g['camps']:<3} "
              f"rounds={g['rounds']:<5} gems={g['gems'][0]}-{g['gems'][1]} kills={g['kills'][0]}-{g['kills'][1]} "
              f"deaths={g['deaths'][0]}-{g['deaths'][1]} opp={', '.join(g['opponent'])}")
    wins = sum(g["won"] for g in games)
    print(f"\n{wins} wins / {len(games)} games")


if __name__ == "__main__":
    main()
