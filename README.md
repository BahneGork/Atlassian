# Atlassian

An interactive atlas of **Erukana**, the world of our RPG campaign.

The map is the navigation: pins and baronies open panels about each place, with links to the full notes on the published campaign notes site. **Rejsen** (the journey) replays the campaign session by session on the map.

## Run locally
The page loads its data with `fetch`, so it needs a web server:

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Update the atlas
Atlas content lives in two places:
- `tools/curation.py`: hand-curated places (map position, type, parent place), barony outlines and the session list
- `tools/build.py`: reads the campaign notes (read-only), adds descriptions, people and factions, and writes `data/erukana.json`

```bash
python3 tools/build.py            # notes default to ../digital-garden/GMnostes-repo/...
```

The build lists any location notes not yet in the atlas and any problems it finds.

## Layout
- `index.html`, `css/atlas.css`, `js/atlas.js`: the site (no build step)
- `maps/`: map images (WebP)
- `vendor/leaflet/`: Leaflet 1.9.4 (BSD-2-Clause)
- `docs/project-plan.md`: scope and decisions
