"""Tråde (docs/traade.md) and the automatic tracking tools for the atlas.

Used by build.py. Nothing here infers connections: threads are hand-written in
docs/traade.md; the tools only count, list and quote what the session logs say.
"""
import re
from collections import defaultdict

SESSION_REF = re.compile(r"(?<![\w/\[])S(\d+(?:\.\d+)?)(?:\s*[–-]\s*(\d+(?:\.\d+)?))?")
LABELS = {"Status": "Status", "Spor": "Spor", "Åbent": "Åbent", "Muligt (gæt)": "Muligt (gæt)",
          "Ifølge Bahne": "Ifølge Bahne", "Næste skridt ifølge noterne": "Næste skridt"}
ENTITY_FOLDERS = ("People", "Locations", "Factions", "Items", "Loot")


def link_sessions(text, known):
    """S26 / S26–27 / S45.5–46 -> markdown links that open the session in Rejsen."""
    def one(num):
        key = float(num)
        return f"[{num}](#session/{known[key]}/laes)" if key in known else num

    return SESSION_REF.sub(lambda m: "S" + one(m.group(1)) + (f"–{one(m.group(2))}" if m.group(2) else ""), text)


def parse_threads(path, known, slug):
    """docs/traade.md -> [{group, id, title, parts: [[label, markdown]]}]."""
    threads, group, cur = [], "", None
    for raw in open(path, encoding="utf-8").read().split("\n"):
        line = raw.rstrip()
        if line.startswith("## "):
            group, cur = re.sub(r"^\d+\.\s*", "", line[3:]).strip(), None
        elif line.startswith("### "):
            title = re.sub(r"^[\d.]+\s*", "", line[4:]).strip()
            cur = {"group": group, "id": slug(title), "title": title, "parts": []}
            threads.append(cur)
        elif line.startswith("| **") and group:
            # table of old loose ends: | **title** | clues | open questions |
            cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
            title = cells[0].strip("* ")
            threads.append({"group": group, "id": slug(title), "title": title,
                            "parts": [["Spor", link_sessions(cells[1], known)],
                                      ["Åbent", link_sessions(cells[2], known)]]})
        elif cur is not None and line.strip() and not line.startswith("---"):
            m = re.match(r"^\*\*([^*]+)\*\*:?\s*(.*)$", line)
            if m and m.group(1) in LABELS:
                cur["parts"].append([LABELS[m.group(1)], link_sessions(m.group(2), known)])
            elif line.lstrip().startswith("- ") and cur["parts"]:
                prev = cur["parts"][-1]
                prev[1] = (prev[1] + "\n" if prev[1] else "") + link_sessions(line.strip(), known)
            else:
                cur["parts"].append(["", link_sessions(line.strip(), known)])
    return threads


def mentions(notes, note_id, session_notes, plain, links_in, wikilink, aliases):
    """note id -> set of sessions that mention it: a link either way, or its name in the log text."""
    by_title = {t: num for num, t in session_notes.items()}
    text = {num: plain(notes[t]["body"]).lower() for num, t in session_notes.items()}
    all_links = lambda body: links_in(body) | {m.group(1).strip() for m in wikilink.finditer(body)}
    out = defaultdict(set)
    for title, n in notes.items():
        nid = note_id.get(title)
        if not nid or n["folder"] not in ENTITY_FOLDERS:
            continue
        out[nid] |= {by_title[t] for t in all_links(n["body"]) if t in by_title}
        for name in [title] + aliases.get(nid, []):
            name = name.lower().strip()
            if len(name) < 5:
                continue
            pat = re.compile(r"(?<![\wæøå])" + re.escape(name) + r"(?![\wæøå])")
            out[nid] |= {num for num, t in text.items() if pat.search(t)}
    for num, t in session_notes.items():
        for target in all_links(notes[t]["body"]):
            if target in note_id and notes[target]["folder"] in ENTITY_FOLDERS:
                out[note_id[target]].add(num)
    return out


def next_steps(notes, session_notes, plain):
    """The group's own NEXT / 'næste gang' lines, per session (repeats dropped)."""
    head = re.compile(r"^[\s>#*-]*(Next Action|Planen? (?:Til )?Næste Gang|Plan Næste Gang|NEXT)\b"
                      r"(?:\s*move)?\s*(?:=>|:)?\s*(.*)$", re.I)
    out, seen = [], set()
    for num in sorted(session_notes):
        lines = notes[session_notes[num]]["body"].split("\n")
        for i, line in enumerate(lines):
            m = head.match(line)
            if not m:
                continue
            items = [m.group(2)] if m.group(2).strip() else []
            for nxt in lines[i + 1:i + 9]:
                if not nxt.strip() or nxt.lstrip().startswith("#") or nxt.strip() in (">", "_Erukana home"):
                    break
                items.append(re.sub(r"^[\s\-*]+", "", nxt))
            items = [plain(x).strip(" =>") for x in items]
            # drop empties and bare in-game dates ("25th Flamerule, …")
            items = [x for x in items if x and not re.match(r"^\d+(st|nd|rd|th)\b", x)]
            key = " ".join(items)
            if items and key not in seen:
                seen.add(key)
                out.append({"session": num, "items": items})
    return out


def open_questions(notes, session_notes, plain):
    """Questions the players wrote in the logs (not numbered speak-with-dead lists or GM boxes)."""
    out = []
    for num in sorted(session_notes):
        for line in notes[session_notes[num]]["body"].split("\n"):
            if re.match(r"^\s*(\d+\.|>|\*)", line):
                continue
            text = plain(re.sub(r"^[\s\-]+", "", line))
            if text.endswith("?") and len(text) > 25:
                out.append({"session": num, "text": text})
    return out
