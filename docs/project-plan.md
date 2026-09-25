# Atlassian — Erukana Atlas — Project Plan

- **Created**: 2026-09-23 · **Revised**: 2026-09-25 (scope cut to a bespoke Erukana atlas)
- **Status**: Design
- **Constraint**: hosting and tooling must be free

## Vision
A bespoke interactive atlas of **Erukana** for the owner and their RPG group. The map is the navigation: pins and regions open panels that summarise what the group knows about each place and link to the full notes on the published Digital Garden.

**No generic system.** No upload, import, note-assignment UI, atlas picker or config schema. Claude reads the notes, decides what goes where, and writes the atlas data by hand. Code and data are still kept in separate files (cheap; keeps the code readable).

## Sources (verified)
- **Notes**: `digital-garden/GMnostes-repo/src/site/notes/02 Player/Erukana (Nissen)/` — Locations 89, People 151, Factions 76, ~43 session logs, lore/items/loot/missions ~120. Published on the garden (Netlify); each note has a `permalink`.
- **Main map**: `Erukana (Nissen)/Locations/Erukana.jpg` — 4096×3526, 7.9 MB. Pixel-identical to the 24 MB `Erukana-annotated.png`, so the JPG is used.
  - Printed labels for towns/castles/landmarks; barony banners (Valence, Blackmere, Botreaux, Ersby, Mowbray, Welles); faint dotted barony borders; background grid.
- **Candidate sub-maps**: `Grøndalen-Erukana.png` (5328², local area map), `Vinterskov - Grøndalen`, `Erukana_-_Bortholme_Region.png` (small). To be reviewed.

## How the atlas is built (Claude as the importer)
1. **Inventory**: read all Erukana notes; classify each as place / region / person / faction / session / other.
2. **Placement**: match place notes to printed map labels by inspecting full-resolution crops of the map; record pixel coordinates. Places not printed on the map are placed from note text ("north of X") and marked **approximate**, or attached to a region only.
3. **Regions**: trace baronies (dotted borders) and named areas (forests, mountains) as rough polygons.
4. **Relationships**: decide from note content who/what belongs to each place (people, factions, events, sessions visited). Judgement, not link-counting.
5. **Output**: `data/erukana.json` — places (point/region/approximate), memberships, panel text, garden URLs.
6. **Review**: owner checks placements and panel text; corrections go straight into the data.

**Updating**: after new sessions, the owner asks Claude to update the atlas; Claude diffs the notes repo since the last recorded update commit and edits the data. (Candidate: a small Claude Code skill to make this repeatable.)

## Site
- Single static page. **Leaflet** (`CRS.Simple`) for the image map.
- Map-first UI: breadcrumb (for sub-maps), search box, side panel. Deep links per place (`#kolitan`).
- Panel: title, short text, "here" lists (people, factions, sessions), link to the full garden note.
- Hosting: **GitHub Pages** (free, no build step, no Netlify credits). Map compressed/tiled as needed for phone load time.

## MVP
1. Main map with pins and barony regions from the inventory
2. Side panel with text, memberships, garden link
3. Search
4. Deep links

## Later
- Sub-maps (Grøndalen etc.) opened from their place on the main map
- Filter by category (towns, dungeons, factions…)
- "Our journey": session-by-session route of the party

## Decisions
- **Language**: as in the notes (mixed Danish/English), no translation.
- **Names**: session logs were written by ear, so note titles may differ from map labels (Colville/Coleville, Stirring/Sterling). Panels show the note title; the map spelling is kept as a search alias. Uncertain matches are listed for the owner to confirm.
- **Leaflet**: approved; copy kept in the repo.

## Open questions
1. Panel text: Claude-written summaries (richer, must be kept in sync) vs opening lines of the note?
2. Test batch first (baronies + ~10 visited places) before placing everything?
3. Which candidate sub-maps matter?

## Tags
#atlassian #erukana #project-plan #leaflet
