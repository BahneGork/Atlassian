"""Build data/erukana.json from the curated places and the published notes.

Usage: python3 tools/build.py [path-to-notes]
By default the notes are fetched from GitHub (BahneGork/GMnostes), where the Obsidian
Digital Garden plugin publishes them, into .cache/. Notes are only read, never modified.
"""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from urllib.parse import quote, unquote

sys.path.insert(0, os.path.dirname(__file__))
from curation import (GARDEN_URL, MAPS, NOT_PEOPLE, NOT_PLACES, OFFMAP, PLACES,  # noqa: E402
                      PORTALS, REGIONS, SESSIONS)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/BahneGork/GMnostes.git"
CACHE = os.path.join(ROOT, ".cache", "GMnostes")
NOTES_DIR = "src/site/notes/02 Player/Erukana (Nissen)"


def fetch_notes():
    """Sparse, shallow copy of the published notes; refreshed on every build."""
    git = ["git", "-C", CACHE]
    try:
        if not os.path.isdir(CACHE):
            subprocess.run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--sparse", REPO, CACHE],
                           check=True)
            subprocess.run(git + ["sparse-checkout", "set", "--no-cone", f"/{NOTES_DIR}/"], check=True)
        else:
            subprocess.run(git + ["fetch", "-q", "--depth", "1", "origin", "main"], check=True)
            subprocess.run(git + ["reset", "-q", "--hard", "origin/main"], check=True)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"warning: could not update notes from GitHub ({e}); using the cached copy")
    rev = subprocess.run(git + ["log", "-1", "--format=%h %ci"], capture_output=True, text=True).stdout.strip()
    print(f"notes: GitHub {rev}")
    return os.path.join(CACHE, NOTES_DIR)


NOTES = sys.argv[1] if len(sys.argv) > 1 else fetch_notes()

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
                             "marked_visited": "Locationsvisited" in rel.split(os.sep)[:-1],
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


# Note groups shown in the reader, by top-level folder.
GROUPS = {"Locations": "Steder", "People": "Personer", "Factions": "Factions", "Items": "Genstande",
          "Loot": "Loot", "Missions": "Missioner", "Journal": "Journal", "Setting lore": "Lore", "Lore": "Lore",
          "Characters": "Karakterer", "Rules": "Regler", "": "Andet"}
SKIP_NOTES = {"Erukana Tag list"}  # generated Dataview output, 23 MB
# Overview notes that link to everything; readable, but not shown as "related".
HUBS = {"_Erukana home", "_Erukana People List", "Faction list", "Mission Board", "Loot found",
        "Locationsvisited", "States and Baronies of Erukana"}


def slug(title):
    t = title.lower().replace("æ", "ae").replace("ø", "o").replace("å", "a")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def reader_markdown(body, ids):
    """Obsidian/garden markdown -> plain markdown with in-atlas links (#note/<id>)."""
    md = re.sub(r"```(?:leaflet|dataview|dataviewjs|base)\b.*?```", "", body, flags=re.S)
    # "Referenced In" and "Tags" repeat what the reader's related-notes box already shows.
    md = re.sub(r"(?ms)^## (?:Referenced In|Tags)\s*$.*?(?=^## |\Z)", "", md)
    md = re.sub(r"<svg.*?</svg>", "", md, flags=re.S)
    md = re.sub(r"<[^>]+>", "", md)
    md = re.sub(r"!\[\[[^\]]*\]\]|!\[[^\]]*\]\([^)]*\)", "", md)
    md = WIKILINK.sub(lambda m: f"[{m.group(2) or m.group(1)}](#note/{ids[m.group(1).strip()]})"
                      if m.group(1).strip() in ids else (m.group(2) or m.group(1)), md)

    def garden_link(m):  # [text](/02 Player/.../Title/) links from embeds
        title = unquote(m.group(2).rstrip("/").split("/")[-1].split("#")[0])
        return f"[{m.group(1)}](#note/{ids[title]})" if title in ids else m.group(1)
    md = re.sub(r"\[([^\]]*)\]\((/02[^)]*)\)", garden_link, md)
    md = re.sub(r"(?m)^\s*(?:#[^\s#][^\s]*\s*)+$", "", md)          # tag-only lines
    md = re.sub(r"(?m)^\[?_Erukana home\]?(?:\([^)]*\))?\s*$", "", md)  # navigation back-link
    md = re.sub(r"(?m)^\{[^}]*\}\s*$", "", md)                       # { .block-language-dataview}
    md = re.sub(r"(?m)^([\wæøåÆØÅ ]+):: ?(.*)$", r"**\1:** \2", md)   # dataview inline fields
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def export_notes(notes, place_of, session_of):
    ids = {t: slug(t) for t in notes if t not in SKIP_NOTES and notes[t]["folder"] != "bases"}
    out = {}
    for title, nid in ids.items():
        n = notes[title]
        # All links, including "Referenced In": that section is how notes point back to sessions.
        linked = {m.group(1).strip() for m in WIKILINK.finditer(n["body"])}
        links = sorted({ids[t] for t in linked if t in ids and t != title and t not in HUBS})
        out[nid] = {"title": title, "group": "Sessioner" if title in session_of else GROUPS.get(n["folder"], "Andet"),
                    "md": reader_markdown(n["body"], ids), "links": links, "backlinks": []}
        if title in place_of:
            out[nid]["place"] = place_of[title]
        if title in session_of:
            out[nid]["session"] = session_of[title]
    for nid, n in out.items():
        if n["title"] in HUBS:
            continue
        for target in n["links"]:
            out[target]["backlinks"].append(nid)
    with open(os.path.join(ROOT, "data", "notes.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    return ids


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
    # A place counts as visited if the party was there (a session, or its note sits in
    # Locations/Locationsvisited), or was in something inside it.
    for pid in list(places):
        n = notes.get(PLACES[pid]["note"])
        if places[pid]["sessions"] or (n and n["marked_visited"]):
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

    session_notes = {float(re.match(r"\d+(?:\.\d+)?", t).group()): t for t, n in notes.items()
                     if n["folder"] == "" and re.match(r"^\d+(?:\.\d+)?\s*[-\s]", t)}
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

    place_of = {p["note"]: ("sted", pid) for pid, p in PLACES.items()}
    place_of.update({r["note"]: ("region", rid) for rid, r in REGIONS.items()})
    session_of = {t: num for num, t in session_notes.items()}
    ids = export_notes(notes, place_of, session_of)
    for pid, p in PLACES.items():
        places[pid]["noteId"] = ids.get(p["note"])
    for rid, r in REGIONS.items():
        regions[rid]["noteId"] = ids.get(r["note"])
    for s in sessions:
        s["noteId"] = ids.get(session_notes.get(s["num"]))

    out = {"maps": MAPS, "portals": PORTALS, "offmap": OFFMAP, "places": places,
           "regions": regions, "sessions": sessions, "unplaced": unplaced}
    with open(os.path.join(ROOT, "data", "erukana.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print(f"{len(places)} places, {len(regions)} regions, {len(sessions)} sessions")
    print("new location notes, not yet in the atlas:", ", ".join(uncurated) or "none")
    for p in problems:
        print("PROBLEM", p)


main()
