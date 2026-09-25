# Atlassian

An interactive atlas of **Erukana**, the world of our RPG campaign.

The map is the navigation: pins and baronies open panels about each place, with links to the full notes on the published campaign notes site. **Rejsen** (the journey) replays the campaign session by session on the map, and every note can be read in the atlas. **Personer** is a people register: filter by name, role, race, place or faction (Danish or English), or by allies, enemies and the dead.

## Run locally
The page loads its data with `fetch`, so it needs a web server:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Update the atlas
Atlas content lives in two places:
- `tools/curation.py`: hand-curated places (map position, type, parent place), barony outlines and the session list
- `tools/build.py`: fetches the published notes from GitHub (`BahneGork/GMnostes`, where the Obsidian Digital Garden plugin publishes them) into `.cache/`, adds descriptions, people and factions, and writes `data/erukana.json`

```bash
python3 tools/build.py            # or: python3 tools/build.py <path-to-notes>
```

The build lists any location notes not yet in the atlas and any problems it finds.

### Tråde (threads)
`docs/traade.md` is the source for the **Tråde** tab: plain Markdown, edited by hand (or by Claude after new sessions). Each `###` heading is a thread; lines starting with `**Status**`, `**Spor**`, `**Åbent**`, `**Muligt (gæt)**` or `**Ifølge Bahne**` become its sections, and session references like `S26` or `S45.5–46` become links into Rejsen. The rows of the table in the last section are short threads.

The other views in the tab are computed on every build from the logs and never infer anything: **Glemte** (mentioned in 2+ sessions but not in the last 12), **Næste skridt** (the group's NEXT lines), **Spørgsmål** (questions written in the logs). The reader also shows which notes are **mentioned in the same sessions**.

### Automatic rebuilds
The "Rebuild atlas" workflow also runs every night (and on demand from the Actions tab), so newly published notes reach the site without anyone running `build.py`. It only publishes when the data changed. If the build reports a `PROBLEM`, the run fails, GitHub e-mails the owner, and the site keeps its last good version.

Notes renamed in the vault don't break the curated titles in `tools/curation.py`: when a title is missing, the build follows the notes' aliases (the renamed note must list the old title as an alias) and prints `followed rename: old -> new`.

### Moving and placing places on the map
1. On the site, open **Signaturer** and tick **Redigér placeringer**.
2. Drag pins into place. **Uplacerede steder** lists places without a position and new location notes the atlas doesn't know yet; pick one and click the map where it belongs.
3. Changes are kept in that browser only. To publish them, click **Gem for alle**: GitHub opens with the changes as a new file in `moves/`. Click **Commit changes** (needs write access to the repo). The workflow `.github/workflows/apply-moves.yml` ("Rebuild atlas") applies them, rebuilds and publishes; the map updates for everyone in a few minutes. Once the site has them, they are dropped from the browser automatically.
4. Or apply them by hand: click **Kopiér ændringer** and run

```bash
python3 tools/apply_moves.py moves.json   # or paste the JSON on stdin
python3 tools/build.py
```

## Layout
- `index.html`, `css/atlas.css`, `js/atlas.js`: the site (no build step)
- `data/erukana.json`: places, regions and sessions; `data/notes.json`: every note as reader-ready markdown with links and back-links (loaded when the reader is first opened)
- `maps/`: map images (WebP)
- `vendor/leaflet/`: Leaflet 1.9.4 (BSD-2-Clause); `vendor/marked/`: marked 12.0.2 (MIT)
- `docs/project-plan.md`: scope and decisions
