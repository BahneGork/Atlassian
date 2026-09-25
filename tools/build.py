"""Build data/erukana.json from the curated places and the published notes.

Usage: python3 tools/build.py [path-to-notes]
Notes are only read, never modified.
"""
import json
import os
import re
import sys
from collections import defaultdict
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from curation import (GARDEN_URL, MAPS, NOT_PEOPLE, NOT_PLACES, OFFMAP, PLACES,  # noqa: E402
                      PORTALS, REGIONS, SESSIONS)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "..", "digital-garden", "GMnostes-repo", "src", "site", "notes", "02 Player", "Erukana (Nissen)")

WIKILINK = re.compile(r"\[\[(?:[^\]|]*/)?([^\]|/#]+?)(?:#[^\]|]*)?(?:\\?\|([^\]]+))?\]\]")


def load_notes():
    notes = {}
    for dirpath, _, files in os.walk(NOTES):
        for f in files:
            if not f.endswith(".md"):
                continue
            path = os.path.join(dirpath, f)
            text = open(path, encoding="utf-8").read()
            meta, body = {}, text
            m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
            if m:
                try:
                    meta = json.loads(m.group(1))
                except ValueError:
                    pass
                body = text[m.end():]
            rel = os.path.relpath(path, NOTES)
            # Some titles exist in several folders; the Locations note wins.
            if notes.get(f[:-3], {}).get("folder") == "Locations":
                continue
            notes[f[:-3]] = {"folder": rel.split(os.sep)[0] if os.sep in rel else "",
                             "permalink": meta.get("permalink"), "body": body}
    return notes


def plain(text):
    text = WIKILINK.sub(lambda m: m.group(2) or m.group(1), text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[*_`]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def summarize(body):
    """First descriptive paragraph of a note, cut to at most ~2 sentences."""
    for pattern in (r"## Description\n+(.+?)(?:\n\n|\n#|$)", r"(?i:#* *beskrivelse):?\s*\n(.+?)(?:\n[A-ZÆØÅ ]{4,}\n|\n#|$)"):
        m = re.search(pattern, body, re.S)
        if m:
            text = plain(m.group(1))
            break
    else:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for s in sentences:
        if len(out) + len(s) > 320 and out:
            break
        out = (out + " " + s).strip()
    return out


def note_url(note):
    if not GARDEN_URL or not note or not note.get("permalink"):
        return ""
    return GARDEN_URL + quote(note["permalink"], safe="/()'")


def links_in(body):
    body = re.split(r"\n## Referenced In", body)[0]
    return {m.group(1).strip() for m in WIKILINK.finditer(body)}


def inside(pt, poly):
    x, y = pt
    hit = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def main():
    notes = load_notes()
    problems = []

    def note(title):
        if title not in notes:
            problems.append(f"missing note: {title}")
        return notes.get(title)

    # Who links to each place from People/ and Factions/.
    linked = defaultdict(lambda: {"People": set(), "Factions": set()})
    for title, n in notes.items():
        if n["folder"] in ("People", "Factions") and title not in NOT_PEOPLE:
            for target in links_in(n["body"]):
                linked[target][n["folder"]].add(title)

    sessions_at = defaultdict(list)
    for num, _, ids in SESSIONS:
        for pid in ids:
            if pid not in PLACES:
                problems.append(f"session {num}: unknown place {pid}")
            sessions_at[pid].append(num)

    places = {}
    for pid, p in PLACES.items():
        n = note(p["note"])
        titles = [p["note"]] + p.get("aliases", [])
        people = set().union(*(linked[t]["People"] for t in titles))
        factions = set().union(*(linked[t]["Factions"] for t in titles))
        places[pid] = {
            "name": p.get("name", p["note"]), "kind": p["kind"],
            "map": p.get("map"), "at": p.get("at"), "approx": p.get("approx", False),
            "parent": p.get("parent"), "region": p.get("region"), "offmap": p.get("offmap"),
            "where": p.get("where", ""), "aliases": p.get("aliases", []),
            "summary": p.get("summary") or (summarize(n["body"]) if n else ""),
            "url": note_url(n), "sessions": sessions_at.get(pid, []),
            "people": sorted(people, key=str.lower), "factions": sorted(factions, key=str.lower),
        }
    # A place counts as visited if the party was there or in something inside it.
    for pid in list(places):
        if places[pid]["sessions"]:
            cur = pid
            while cur:
                places[cur]["visited"] = True
                cur = places[cur]["parent"]
    for pid, p in places.items():
        p.setdefault("visited", False)
        if p["parent"] and p["parent"] not in places:
            problems.append(f"{pid}: unknown parent {p['parent']}")
        if not p["region"] and p["at"]:
            for rid, r in REGIONS.items():
                if r["map"] == p["map"] and r["poly"] and inside(p["at"], r["poly"]):
                    p["region"] = rid
                    break
        if not p["summary"]:
            problems.append(f"{pid}: no summary")

    regions = {}
    for rid, r in REGIONS.items():
        n = note(r["note"])
        titles = [r["note"]] + r.get("aliases", [])
        regions[rid] = {
            "name": r["name"], "map": r["map"], "poly": r["poly"], "label": r.get("label"),
            "summary": r.get("summary") or (summarize(n["body"]) if n else ""),
            "url": note_url(n),
            "people": sorted(set().union(*(linked[t]["People"] for t in titles)), key=str.lower),
            "factions": sorted(set().union(*(linked[t]["Factions"] for t in titles)), key=str.lower),
        }

    session_notes = {int(re.match(r"\d+", t).group()): t for t, n in notes.items()
                     if n["folder"] == "" and re.match(r"^\d+\s*[-\s]", t)}
    sessions = []
    for num, title, ids in SESSIONS:
        t = session_notes.get(num)
        if not t:
            problems.append(f"session {num}: note not found")
        d = re.match(r"^\d+\s*-?\s*(\d{2})(\d{2})(\d{2})\b", t or "")
        sessions.append({
            "num": num, "title": title, "places": ids, "url": note_url(notes.get(t)),
            "date": f"{d.group(1)}.{d.group(2)}.20{d.group(3)}" if d else "",
            "gm": "Steffen" if "steffen" in (t or "").lower() else "Nissen",
        })

    # Location notes nobody has curated yet, so updates can spot new places.
    curated = {p["note"] for p in PLACES.values()} | {a for p in PLACES.values() for a in p.get("aliases", [])}
    curated |= {r["note"] for r in REGIONS.values()} | {a for r in REGIONS.values() for a in r.get("aliases", [])}
    uncurated = sorted(t for t, n in notes.items()
                       if n["folder"] == "Locations" and t not in curated and t not in NOT_PLACES)
    unplaced = [{"note": t, "summary": summarize(notes[t]["body"]), "url": note_url(notes[t])} for t in uncurated]

    out = {"maps": MAPS, "portals": PORTALS, "offmap": OFFMAP, "places": places,
           "regions": regions, "sessions": sessions, "unplaced": unplaced}
    with open(os.path.join(ROOT, "data", "erukana.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"{len(places)} places, {len(regions)} regions, {len(sessions)} sessions")
    print("new location notes, not yet in the atlas:", ", ".join(uncurated) or "none")
    for p in problems:
        print("PROBLEM", p)


main()
