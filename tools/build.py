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
from datetime import datetime
from urllib.parse import quote, unquote

sys.path.insert(0, os.path.dirname(__file__))
from curation import (GARDEN_URL, LOCATION_ALIASES, MAPS, NOT_PEOPLE, NOT_PLACES,  # noqa: E402
                      OFFMAP, PARTY, PARTY_EXTRA, PARTY_STATUS, PLACES, PORTALS, REGIONS, SESSIONS)
import threads as thr  # noqa: E402

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
                             "permalink": meta.get("permalink"), "body": body,
                             "props": meta.get("dg-note-properties") or {}}
    return notes


def link_label(m):
    """Visible text of a wikilink; aliases that are full paths show just the note name."""
    return (m.group(2) or m.group(1)).split("/")[-1].strip()


def plain(text, ids=None):
    """Strip markdown; with `ids`, wikilinks to known notes become [name](#note/<id>) links."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[*_`]+(?![^\[]*\]\])", "", text)
    text = WIKILINK.sub(lambda m: f"[{link_label(m)}](#note/{ids[m.group(1).strip()]})"
                        if ids and m.group(1).strip() in ids else link_label(m), text)
    return re.sub(r"\s+", " ", text).strip()


def summarize(body, ids=None):
    """First descriptive paragraph of a note, cut to at most ~2 sentences (links kept with `ids`)."""
    for pattern in (r"## Description\n+(.+?)(?:\n\n|\n#|$)", r"(?i:#* *beskrivelse):?\s*\n(.+?)(?:\n[A-ZÆØÅ ]{4,}\n|\n#|$)"):
        m = re.search(pattern, body, re.S)
        if m:
            text = plain(m.group(1), ids)
            break
    else:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = ""
    for s in sentences:
        # never cut inside a link such as [Hr. Flick](#note/...)
        if len(out) + len(s) > 320 and out and out.count("[") == out.count("]("):
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
    md = WIKILINK.sub(lambda m: f"[{link_label(m)}](#note/{ids[m.group(1).strip()]})"
                      if m.group(1).strip() in ids else link_label(m), md)

    def garden_link(m):  # [text](/02 Player/.../Title/) links from embeds
        title = unquote(m.group(2).rstrip("/").split("/")[-1].split("#")[0])
        return f"[{m.group(1)}](#note/{ids[title]})" if title in ids else m.group(1)
    md = re.sub(r"\[([^\]]*)\]\((/02[^)]*)\)", garden_link, md)
    md = re.sub(r"(?m)^\s*(?:#[^\s#][^\s]*\s*)+$", "", md)          # tag-only lines
    md = re.sub(r"(?m)^\[?_Erukana home\]?(?:\([^)]*\))?\s*$", "", md)  # navigation back-link
    md = re.sub(r"(?m)^\{[^}]*\}\s*$", "", md)                       # { .block-language-dataview}
    md = re.sub(r"(?m)^\s*#+\s*$", "", md)                            # empty headings
    md = re.sub(r"(?m)^([\wæøåÆØÅ ]+):: ?(.*)$", r"**\1:** \2", md)   # dataview inline fields
    return re.sub(r"\n{3,}", "\n\n", md).strip()


def note_ids(notes):
    return {t: slug(t) for t in notes if t not in SKIP_NOTES and notes[t]["folder"] != "bases"}


def export_notes(notes, ids, place_of, session_of):
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


def prop_targets(value):
    """Note titles named by a property value: [[links]] inside strings, or the plain string itself."""
    out = []
    for v in value if isinstance(value, list) else [value]:
        if not isinstance(v, str) or not v.strip():
            continue
        found = [m.group(1).strip() for m in WIKILINK.finditer(v)]
        out += found or [v.strip()]
    return out


# Disposition / friend-or-foe values -> ally | neutral | enemy | unknown
STANCE = {"ally": "ally", "friend": "ally", "deceased-ally": "ally", "neutral": "neutral",
          "conditional": "neutral", "enemy": "enemy", "foe": "enemy", "hostile": "enemy"}


def text_prop(value):
    vals = [v for v in (value if isinstance(value, list) else [value]) if isinstance(v, str) and v.strip()]
    return ", ".join(WIKILINK.sub(link_label, v) for v in vals)


def build_people(notes, note_id, session_of):
    """People and factions from their notes' properties, placed on atlas places where possible."""
    where = {p["note"]: pid for pid, p in PLACES.items()}
    where.update({a: pid for pid, p in PLACES.items() for a in p.get("aliases", [])})
    where.update({r["note"]: f"region:{rid}" for rid, r in REGIONS.items()})
    where.update({a: f"region:{rid}" for rid, r in REGIONS.items() for a in r.get("aliases", [])})
    where.update(LOCATION_ALIASES)

    def place_of(props):
        for key in ("location_primary", "Location", "location"):
            for t in prop_targets(props.get(key)):
                if t in where:
                    return where[t]
        return None

    def sessions_of(title, props):
        nums = {session_of[t] for t in prop_targets(props.get("sessions")) if t in session_of}
        nums |= {num for t, num in session_of.items() if title in links_in(notes[t]["body"])}
        return sorted(nums)

    factions = {}
    for title, n in notes.items():
        if n["folder"] != "Factions" or title not in note_id:
            continue
        pr = n["props"]
        factions[note_id[title]] = {
            "name": title, "seat": place_of(pr),
            "stance": STANCE.get(str(pr.get("friend-or-foe", "")).lower(), "unknown"),
            "type": text_prop(pr.get("faction_type")), "status": text_prop(pr.get("status")),
            "leader": [note_id[t] for t in prop_targets(pr.get("leader")) if t in note_id],
            "sessions": sessions_of(title, pr), "members": [],
        }
    people = {}
    for title, n in notes.items():
        in_party = title in PARTY
        if (n["folder"] != "People" and not (in_party and n["folder"] == "Characters")) or title not in note_id \
                or (title in NOT_PEOPLE and not in_party) \
                or re.search(r"\.(png|jpe?g|webp)$", title, re.I):  # image notes are not people
            continue
        pr = n["props"]
        disp = str(pr.get("disposition", "")).lower()
        status, status_note = PARTY_STATUS.get(title, (str(pr.get("status", "")).lower(), ""))
        fids = []
        for key in ("affiliation", "Faction", "faction"):
            for t in prop_targets(pr.get(key)):
                if note_id.get(t) in factions and note_id[t] not in fids:
                    fids.append(note_id[t])
        pid = note_id[title]
        people[pid] = {
            "name": title, "place": place_of(pr),
            "stance": STANCE.get(disp, "ally" if in_party else "unknown"),  # party members are allies unless noted
            "dead": status == "dead" or disp.startswith("deceased"),
            "status": status if status not in ("", "alive", "unknown") else "",
            "race": "" if pr.get("race") in (None, "unspecified") else text_prop(pr.get("race")),
            "social": text_prop(pr.get("social_status")),
            "role": text_prop(pr.get("role")) or text_prop(pr.get("Profession")),
            "aliases": [a for a in pr.get("aliases") or [] if isinstance(a, str)],
            "factions": fids, "sessions": sessions_of(title, pr),
            "pc": in_party, "statusNote": status_note,
        }
        for f in fids:
            factions[f]["members"].append(pid)
    # Party members without a note: sessions from their name in the logs.
    for name, extra in PARTY_EXTRA.items():
        names = [name] + extra["aliases"]
        pat = re.compile(r"(?<![\wæøå])(" + "|".join(re.escape(x.lower()) for x in names) + r")(?![\wæøå])")
        nums = sorted(num for t, num in session_of.items() if t in notes and pat.search(plain(notes[t]["body"]).lower()))
        people[slug(name)] = {"name": name, "place": None, "stance": "ally", "dead": extra["dead"], "status": "",
                              "race": extra["race"], "social": extra["social"], "role": extra["role"],
                              "aliases": extra["aliases"], "factions": [], "sessions": nums, "pc": True,
                              "statusNote": extra["statusNote"], "noNote": True}
    return people, factions


def main():
    notes = load_notes()
    note_id = note_ids(notes)
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
    for num, _, ids, *_ in SESSIONS:
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
            "summary": p.get("summary") or (summarize(n["body"], note_id) if n else ""),
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
            "summary": r.get("summary") or (summarize(n["body"], note_id) if n else ""),
            "url": note_url(n),
            "people": sorted(set().union(*(linked[t]["People"] for t in titles)), key=str.lower),
            "factions": sorted(set().union(*(linked[t]["Factions"] for t in titles)), key=str.lower),
        }

    session_notes = {float(re.match(r"\d+(?:\.\d+)?", t).group()): t for t, n in notes.items()
                     if n["folder"] == "" and re.match(r"^\d+(?:\.\d+)?\s*[-\s]", t)}
    # Journey entries without a session log name their own note (e.g. a mission note).
    entry_notes = {num: extra[0] for num, _, _, *extra in SESSIONS if extra}
    sessions = []
    for num, title, ids, *_ in SESSIONS:
        t = entry_notes.get(num) or session_notes.get(num)
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
    session_of = {t: int(num) if num == int(num) else num for num, t in {**session_notes, **entry_notes}.items()}
    export_notes(notes, note_id, place_of, session_of)
    people, factions = build_people(notes, note_id, session_of)

    # Tråde (hand-written in docs/traade.md) and the automatic tracking tools
    known = {float(s["num"]): s["num"] for s in sessions}
    threads = thr.parse_threads(os.path.join(ROOT, "docs", "traade.md"), known, slug)
    seen_in = thr.mentions(notes, note_id, session_notes, plain, links_in, WIKILINK,
                           {pid: p["aliases"] for pid, p in people.items()})
    latest = max(session_notes)
    # duplicate notes that the atlas treats as aliases of another place (e.g. "knoglestammens huler 1")
    aliases = {a for p in PLACES.values() for a in p.get("aliases", [])}
    title_of = {v: k for k, v in note_id.items()}
    kind_of = {note_id[t]: n["folder"] for t, n in notes.items() if t in note_id}
    to_num = lambda x: int(x) if x == int(x) else x
    forgotten = sorted(
        ({"id": nid, "title": title_of[nid], "kind": kind_of[nid], "sessions": [to_num(x) for x in sorted(s)],
          "last": to_num(max(s))} for nid, s in seen_in.items()
         if len(s) >= 2 and max(s) <= latest - 12 and title_of[nid] not in NOT_PEOPLE | NOT_PLACES | aliases
         and not people.get(nid, {}).get("dead")),
        key=lambda f: (-len(f["sessions"]), -f["last"]))
    # "Nævnt sammen med": notes sharing the most sessions, leaving out those in over half of all sessions
    common = {nid for nid, s in seen_in.items() if len(s) > 0.5 * len(session_notes)}
    together = {}
    for nid, s in seen_in.items():
        pairs = sorted(((len(s & t), other) for other, t in seen_in.items()
                        if other != nid and other not in common and len(s & t) >= 2), reverse=True)[:8]
        if pairs:
            together[nid] = [[other, k] for k, other in pairs]
    tools = {"forgotten": forgotten, "latest": to_num(latest),
             "next": [{**x, "session": to_num(x["session"])} for x in thr.next_steps(notes, session_notes, plain)],
             "questions": [{**x, "session": to_num(x["session"])} for x in thr.open_questions(notes, session_notes, plain)]}
    notes_path = os.path.join(ROOT, "data", "notes.json")
    notes_out = json.load(open(notes_path, encoding="utf-8"))
    for nid, pairs in together.items():
        if nid in notes_out:
            notes_out[nid]["together"] = pairs
    json.dump(notes_out, open(notes_path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    for item in list(places.values()) + list(regions.values()):
        for key in ("people", "factions"):
            item[key] = [[t, note_id.get(t)] for t in item[key]]
    for pid, p in PLACES.items():
        places[pid]["noteId"] = note_id.get(p["note"])
    for rid, r in REGIONS.items():
        regions[rid]["noteId"] = note_id.get(r["note"])
    for s in sessions:
        s["noteId"] = note_id.get(entry_notes.get(s["num"]) or session_notes.get(s["num"]))

    out = {"maps": MAPS, "portals": PORTALS, "offmap": OFFMAP, "places": places,
           "people": people, "factions": factions, "threads": threads, "tools": tools,
           "regions": regions, "sessions": sessions, "unplaced": unplaced}
    with open(os.path.join(ROOT, "data", "erukana.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    # Stamp a new version into index.html so browsers (phones especially) skip cached files.
    version = datetime.now().strftime("%Y%m%d%H%M%S")
    index = os.path.join(ROOT, "index.html")
    html = open(index, encoding="utf-8").read()
    html = re.sub(r'\?v=[0-9]+"', f'?v={version}"', html)
    html = re.sub(r'ATLAS_VERSION = "[0-9]*"', f'ATLAS_VERSION = "{version}"', html)
    open(index, "w", encoding="utf-8").write(html)

    print(f"{len(places)} places, {len(regions)} regions, {len(sessions)} sessions (version {version})")
    print(f"{len(threads)} threads; tools: {len(forgotten)} forgotten, {len(tools['next'])} next steps, "
          f"{len(tools['questions'])} questions")
    placed = sum(1 for p in people.values() if p["place"])
    print(f"{len(people)} people ({placed} placed), {len(factions)} factions "
          f"({sum(1 for f in factions.values() if f['seat'])} with a seat)")
    print("new location notes, not yet in the atlas:", ", ".join(uncurated) or "none")
    for p in problems:
        print("PROBLEM", p)


main()
