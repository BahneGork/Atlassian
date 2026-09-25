"""Hand-curated atlas data for Erukana.

Positions are pixel coordinates (x, y) on the source map images, read off a grid
overlay. `approx=True` marks places not printed on the map, placed from what the
notes say (e.g. "south of Astley"). Every place is keyed to a note title in
02 Player/Erukana (Nissen)/Locations.

Kegville, Dark Gem, Det Røde pas, Sir Seillings mausoleum, Miragehill and the Queensguard
Chapterhouse come from the owner's own Obsidian Leaflet pins (vault "Diamor", map id
testid99), converted with x = lng * 512, y = -lat * 512.
"""

GARDEN_URL = ""  # e.g. "https://<site>.netlify.app" (no trailing slash)

MAPS = {
    # Image is Erukana2.jpg (2048 px wide); positions stay in the original 4096 px space.
    "erukana": {"name": "Erukana", "image": "maps/erukana.webp", "size": [4096, 3526]},
    "nordheim": {"name": "Nordheim", "image": "maps/nordheim.webp", "size": [2048, 1165],
                 "note": "Nordheim"},
}

# Links between maps, drawn as signposts at the map edge.
PORTALS = [
    {"map": "erukana", "to": "nordheim", "label": "Nordheim", "hint": "over havet mod nord", "at": [1250, 110]},
    {"map": "nordheim", "to": "erukana", "label": "Erukana", "hint": "syd for Drakespear", "at": [1760, 1085]},
]

# kind: by | borg | taarn | hule | helligt | havn | vildmark | sted
# id -> dict(note, map, at, kind, approx, parent, region, aliases, summary, where)
PLACES = {
    # --- Welles ---
    "astley": dict(note="Astley", map="erukana", at=[2460, 2432], kind="by", region="welles"),
    "soltraeet": dict(note="Soltræet", parent="astley", kind="helligt"),
    "visdommens-kammer": dict(note="Visdommens kammer", parent="soltraeet", kind="sted"),
    "krypten": dict(note="Krypten", parent="soltraeet", kind="hule"),
    "hjertekammeret": dict(note="Hjertekammeret", parent="soltraeet", kind="hule"),
    "paladine-templet": dict(note="paladine templet i Astley", parent="astley", kind="helligt"),
    "paladine-bibliotek": dict(note="Paladine's bibliotek i Astley", parent="paladine-templet", kind="sted"),
    "svinestien": dict(note="Svinestien - Bar i Astley shanty town", parent="astley", kind="sted", name="Svinestien"),
    "kongens-hvil": dict(note="kongens hvil", parent="astley", kind="sted", name="Kongens Hvil"),
    "den-braekkede-knogle": dict(note="Den brækkede knogle", parent="astley", kind="sted"),
    "sangstrup": dict(note="Sangstrup home", parent="astley", kind="sted", name="Sangstrup-gården"),
    "alistair": dict(note="Alistairs handelsforretning", parent="astley", kind="sted",
                     name="Waning Moon merchant house"),
    "feywood": dict(note="Feywood", map="erukana", at=[2650, 2520], kind="vildmark", region="welles"),
    "mausoleum": dict(note="Sir Seillings mausoleum", map="erukana", at=[2590, 2743], kind="hule", region="welles", aliases=["mausoleum"]),
    "stirling": dict(note="Stirring", map="erukana", at=[2745, 2330], approx=True, kind="borg",
                     region="welles", name="Stirling", aliases=["Stirring", "Jarlsborg"],
                     where="Nord for Feywood og øst for Astley ifølge noterne. "
                           "Ikke det samme som kortets 'Sterling' i Botreaux."),
    "mistville": dict(note="Mistville", map="erukana", at=[2290, 2395], approx=True, kind="by",
                      region="welles",
                      summary="Lille landsby i Baroniet Welles tæt ved grænsen til Eresby. "
                              "Her fandt gruppen Brakeshield-statuen hos Archibald Oddsmoke, "
                              "og her nedkæmpede de nekromantikeren Ulrick Stadtfeldt og hans udøde. "
                              "Gruppen blev æresmedlemmer af byen."),
    "kroen-maanehvil": dict(note="Kroen Månehvil", parent="mistville", kind="sted"),
    "dvalin": dict(note="Dvalin Werewolf caves", map="erukana", at=[2240, 2350], approx=True,
                   kind="hule", region="welles", name="Dvalins huler",
                   where="I skoven lige uden for Mistville.",
                   summary="Huler i skoven uden for Mistville, hvor varulven Dvalin Hammerhånd "
                           "havde opholdt sig. Gruppen fandt hans kone Celia død her."),
    "gamle-tempel": dict(note="Det gamle tempel nordøst for Colville", map="erukana", at=[2570, 2600],
                         approx=True, kind="helligt", region="welles", name="Det gamle tempel",
                         where="En halv dags rejse nordøst for Colville."),
    "colville": dict(note="Colville", map="erukana", at=[2425, 2686], kind="by", region="welles",
                     aliases=["Coleville"]),
    "southwatch": dict(note="Southwatch", map="erukana", at=[2440, 2874], kind="by", region="welles"),
    "castle-brienne": dict(note="Castle Brienne", map="erukana", at=[2340, 2925], kind="borg", region="welles"),
    "rode-pas": dict(note="Det Røde pas", map="erukana", at=[2804, 2593], kind="vildmark"),

    # --- Eresby ---
    "dark-gem": dict(note="Dark Gem Kobold clan caves", map="erukana", at=[2173, 2316], kind="hule", region="eresby", name="Dark Gem-hulerne",
                     summary="Kobold-klanen Dark Gems huler. Her fandt gruppen timeglasset og "
                             "tids-scrollen i session 1 og mødte hviskeren i mørket, som fortalte "
                             "om glemte dværgehaller dybere nede."),
    "tunnel-violet": dict(note="Dark Gem Cave - Tunnel med violet lys", parent="dark-gem", kind="sted",
                          name="Tunnel med violet lys"),
    "tunnel-vandrisle": dict(note="Dark Gem Cave - Tunnel med vandrisle lyde", parent="dark-gem", kind="sted",
                             name="Tunnel med vandrisle-lyde"),
    "tunnel-affald": dict(note="Dark Gem Cave - Tunnel til affaldsrum", parent="dark-gem", kind="sted",
                          name="Tunnel til affaldsrum"),
    "dvaerge-haller": dict(note="gamle glemte dværge haller", parent="dark-gem", kind="hule",
                           name="De glemte dværgehaller"),
    "kegville": dict(note="Kegville", map="erukana", at=[2114, 2087], kind="by",
                     region="eresby", aliases=["The Bronze Keg", "Bronze Keg"]),
    "segreve": dict(note="Segreve", map="erukana", at=[2436, 1990], kind="by", region="eresby",
                    aliases=["Segrave"]),
    "pembroke": dict(note="Pembroke", map="erukana", at=[2080, 1880], kind="by"),
    "stampenborg": dict(note="Stampenborg", map="erukana", at=[2805, 1735], kind="borg", region="eresby"),
    "arcana": dict(note="Arcana tårnet", map="erukana", at=[2005, 3020], approx=True, kind="taarn",
                   aliases=["Arkana", "Vogter tårnet"],
                   where="Muligvis kortets 'Arkana' – noterne kalder det 'det sydlige wizard-tårn'. "
                         "Turen (20.5) har ingen sessionslog – den står i missionsnoten 'The fall of Arcana tower'."),
    "grimrock": dict(note="Grimrock Woods", map="erukana", at=[2870, 1590], kind="vildmark"),
    "miragehill": dict(note="Miragehill", map="erukana", at=[3075, 1606], approx=True, kind="by",
                       where="På østsiden af Grimrock Woods."),

    # --- Mowbray & the west ---
    "forgotten-tower": dict(note="The Forgotten tower", map="erukana", at=[1913, 2195], kind="taarn",
                            region="mowbray"),
    "ironreach": dict(note="bjergene i vest og syd", map="erukana", at=[925, 2075], kind="vildmark",
                      name="Bjergene i vest og syd", aliases=["Ironreach mountains"]),
    "slatestone": dict(note="Slatestone", map="erukana", at=[845, 1530], kind="borg"),
    "silverstream": dict(note="Silverstream dværge hallerne", map="erukana", at=[1660, 2590], kind="borg",
                         name="Silverstream",
                         summary="Den dværgehal blandt Bjergenes Børn, der er mest åben mod omverdenen. "
                                 "Grundlagt af en klan fra Slatestone, og anerkender i dag ikke "
                                 "Slatestones hersker – hvilket har ført til mindre krige mellem hallerne."),
    "blackforge": dict(note="Blackforge", map="erukana", at=[1806, 1738], region="mowbray", kind="by"),

    # --- Botreaux, Valence, Blackmere ---
    "botreaux-by": dict(note="Botreaux", map="erukana", at=[2300, 810], kind="by", region="botreaux"),
    "castle-botreaux": dict(note="Castle Botreaux", parent="botreaux-by", kind="borg"),
    "castle-de-ros": dict(note="Castle De Ros", map="erukana", at=[2340, 1455], kind="borg", region="botreaux"),
    "sentinel": dict(note="tårnet The Sentinel", map="erukana", at=[2230, 1055], kind="taarn",
                     region="botreaux", name="The Sentinel"),
    "wolfenburg": dict(note="Wolfenburg", map="erukana", at=[3180, 1090], kind="by", region="botreaux"),
    "feucenberg": dict(note="Castle Feucenberg", map="erukana", at=[2980, 1270], approx=True, kind="borg",
                       region="botreaux", where="Nær Wolfenburg – sandsynligvis den unavngivne borg på kortet."),
    "chapterhouse": dict(note="Queensguard Chapterhouse Erukana", map="erukana", at=[2694, 1273],
                         approx=True, kind="borg", region="botreaux", name="Queensguard Chapterhouse",
                         where="Usikker placering. Nu ødelagt."),
    "mortimor": dict(note="Mortimor", map="erukana", at=[2565, 230], kind="by", region="valence"),
    "vigils-rock": dict(note="Vigil's Rock", map="erukana", at=[3410, 420], kind="havn", region="blackmere"),
    "highhome": dict(note="Highhome", map="erukana", at=[3920, 470], kind="by", region="blackmere"),
    "solstice": dict(note="Solstice", map="erukana", at=[1994, 3300], kind="by", aliases=["soltice"]),

    # --- Nordheim ---
    "stormbjerget": dict(note="StormBjerget", map="nordheim", at=[870, 520], kind="vildmark",
                         aliases=["Storms Peak"]),
    "knoglestammens-huler": dict(note="knoglestammens huler", parent="stormbjerget", kind="hule",
                                 name="Knoglestammens huler", aliases=["knoglestammens huler 1"]),
    "sorrow-vale": dict(note="Sorrow Vale", map="nordheim", at=[1200, 560], kind="vildmark",
                        aliases=["Sorrows Vale"]),
    "crater-shrine": dict(note="Crater shrine of Mielikki", map="nordheim", at=[1040, 545], kind="helligt",
                          aliases=["Nayaru's Blessing"]),
    "vardestjernen": dict(note="Vardestjernen", map="nordheim", at=[1330, 445], approx=True, kind="hule",
                          aliases=["Varde stjernen"],
                          where="Nord-øst for Sorrow Vale – en dags rejse efter mantaen."),
    "port-drakkan": dict(note="Port Drakkan", map="nordheim", at=[1907, 318], kind="havn"),
    "vinterspiret": dict(note="Vinterspiret", parent="port-drakkan", kind="taarn"),
    "port-alexander": dict(note="Port Alexander", map="nordheim", at=[1812, 752], kind="havn"),
    "grondalen": dict(note="Grøndalen", region="nordheim", kind="vildmark",
                      where="Et sted i Nordheim – ikke tegnet på kortet.",
                      summary="Dal i Nordheim, hvor timeglasset sendte gruppen hen. En blå drage og "
                              "den korrumperede nekromantiker Malgazar havde forpestet dalen; efter "
                              "sejren blev naturen spolet tilbage."),
    "vinterskov": dict(note="Vinterskov", parent="grondalen", kind="by", aliases=["Vinterskov 1"],
                       summary="Nordisk tømmerby i Grøndalen. Kroværten Håkan tegnede et kort over dalen "
                               "i jorden på disken."),
    "troldmand-ruin": dict(note="Troldmands tårn ruin i nordlandet", region="nordheim", kind="taarn",
                           name="Troldmandstårn-ruinen", where="Et sted i nordlandet."),

    # --- Beyond the maps ---
    "anaksa": dict(note="Anaksa", offmap="east", kind="by"),
    "deltafloden": dict(note="Deltafloden", parent="anaksa", kind="helligt"),
    "sistana": dict(note="sistana", offmap="east", kind="vildmark", name="Sistana"),
    "orkenen": dict(note="den endeløse ørken", offmap="east", kind="vildmark", name="Den endeløse ørken"),
    "kolitan": dict(note="Kolitan", offmap="east", kind="by", where="I Julland."),
    "landet-mod-nord": dict(note="landet mod nord over havet", offmap="other", kind="vildmark",
                            name="Landet mod nord over havet"),
    "zezstanie": dict(note="Zezstanie", offmap="other", kind="by"),
    "angramar": dict(note="Angramar", offmap="other", kind="hule"),
    "mistport": dict(note="mistport", offmap="other", kind="havn", name="Mistport"),
    "whisperwind": dict(note="The Whisperwind Airship", offmap="other", kind="havn", name="Whisperwind",
                        summary="Det flyvende skib, som gruppen fandt fortøjret ved Vinterspiret i Port Drakkan "
                                "og styrer med en metal-wand. Draconians bordede skibet og tog Evelyn til fange."),
    "stormens-ed": dict(note="stormens ed", offmap="other", kind="havn", name="Stormens Ed",
                        where="Et helligt skib i 'himmerige' – nået gennem en portal."),
}

OFFMAP = {
    "east": {"name": "Det forbudte øst", "map": "erukana", "at": [3950, 1600],
             "hint": "Anaksa, Sistana, ørkenen"},
    "other": {"name": "Andre steder", "hint": "Steder uden kendt placering"},
}

# Barony / duchy outlines on the Erukana map, traced roughly along the dotted borders.
REGIONS = {
    "botreaux": dict(note="Hertugdømmet Bortreaux", name="Hertugdømmet Botreaux", map="erukana",
                     label=[2280, 890], poly=[
                         [1760, 880], [2000, 760], [2330, 650], [2700, 720], [3040, 690], [3150, 900],
                         [3240, 1100], [3230, 1440], [3000, 1440], [2850, 1400], [2500, 1440],
                         [2200, 1515], [1950, 1500], [1760, 1440], [1700, 1150]]),
    "valence": dict(note="Baroniet Valence", name="Baroniet Valence", map="erukana", label=[2720, 250],
                    aliases=["Valence"], poly=[
                        [2330, 650], [2380, 230], [2560, 160], [2760, 230], [2950, 370], [3100, 400],
                        [3165, 480], [3050, 690], [2900, 720], [2700, 720], [2500, 670]]),
    "blackmere": dict(note="Baroniet Blackmere", name="Baroniet Blackmere", map="erukana", label=[3450, 210],
                      poly=[[2950, 370], [3000, 180], [3200, 120], [3500, 180], [3800, 330], [4000, 480],
                            [3900, 520], [3500, 450], [3300, 450], [3165, 480], [3100, 400]]),
    "eresby": dict(note="Baroniet Eresby", name="Baroniet Eresby", map="erukana", label=[2320, 1775],
                   poly=[[2080, 1606], [2300, 1560], [2500, 1450], [2850, 1400], [3230, 1450], [3260, 1850],
                         [2950, 2000], [2740, 2310], [2400, 2300], [2248, 2286], [2110, 2150],
                         [2060, 1900], [2050, 1700]]),
    "mowbray": dict(note="Baroniet Mowbray", name="Baroniet Mowbray", map="erukana", label=[1650, 1920],
                    poly=[[1425, 1760], [1500, 1660], [1650, 1630], [1850, 1600], [1960, 1500], [2080, 1606],
                          [2050, 1700], [2060, 1900], [2090, 2050], [2110, 2150], [2150, 2260],
                          [1900, 2280], [1500, 2300], [1300, 2150], [1250, 1900]]),
    "welles": dict(note="Baroniet Welles", name="Baroniet Welles", map="erukana", label=[2290, 2510],
                   poly=[[2197, 2300], [2740, 2310], [2850, 2400], [2800, 2650], [2700, 2800], [2560, 2940],
                         [2339, 2981], [2258, 2859], [2177, 2777], [2136, 2605], [2197, 2412]]),
    "nordheim": dict(note="Nordheim", name="Nordheim", map="nordheim", poly=None,
                     summary="Nordlandet over havet nord for Erukana. Hjem for nordiske klaner og stammer "
                             "som Frostløberne, Bjergkloen, Sortvingen og Flodhviskerne – og for de ukendte "
                             "stammer som Langfods-stammen og Knoglefolket."),
}

# The journey: one entry per session log. Places are PLACES ids. An optional 4th item names
# the note to read for entries that have no session log.
SESSIONS = [
    (1, "Bagholdet og Dark Gem-hulerne", ["dark-gem"]),
    (2, "Uge på The Bronze Keg", ["kegville"]),
    (3, "Rejsen til Mistville – de blå nomader", ["kegville", "mistville"]),
    (4, "Varulvens huler", ["dvalin"]),
    (5, "Mistvilles udøde", ["mistville"]),
    (6, "Mod Astley – to roseriddere", ["astley"]),
    (7, "Fanget i Astley", ["astley", "kongens-hvil"]),
    (8, "Redningen og Tidsrummet", []),
    (9, "Dusøren på Feywood-bæstet", ["svinestien", "paladine-bibliotek", "feywood"]),
    (10, "Sumpen og Blackspear-ruinerne", ["feywood"]),
    (11, "Feywoods korruption", ["feywood"]),
    (12, "Downtime i Astley", ["astley", "soltraeet"]),
    (13, "Snestorm i Grøndalen", ["grondalen", "vinterskov"]),
    (14, "Graven i Grøndalen", ["grondalen"]),
    (15, "Alterrummet", ["grondalen"]),
    (16, "Malgazar falder", ["grondalen", "astley"]),
    (17, "Tilbage i Astley", ["astley", "soltraeet"]),
    (18, "Den brækkede knogle", ["den-braekkede-knogle"]),
    (19, "Baghold på Alistair-palæet", ["astley"]),
    (20, "Vinterfesten", ["astley"]),
    # No session log: the trip is only in the mission note, which is read in its place.
    (20.5, "The fall of Arcana tower – Isilme", ["arcana"], "Arcana Tower Explosion"),
    (21, "Winstons ridderslag – varehus 13", ["astley"]),
    (22, "Slaget i himmerige", ["stormens-ed"]),
    (23, "Stormens Ed", ["stormens-ed"]),
    (24, "Pirat-kaptajnen og ild-elementalen", []),
    (25, "Spøgelsesbyen", []),
    (26, "Mod StormBjerget", ["stormbjerget", "knoglestammens-huler"]),
    (27, "Knoglestammen", ["knoglestammens-huler"]),
    (28, "Blod i sneen", ["knoglestammens-huler"]),
    (29, "Windbreaker waystation", ["crater-shrine"]),
    (30, "Earthshaker-slaget", ["crater-shrine"]),
    (31, "Mantaens gave", ["crater-shrine", "sorrow-vale"]),
    (32, "Efter orkerne", ["vardestjernen"]),
    (33, "Frostkæmpen i Varde stjernen", ["vardestjernen"]),
    (34, "Staven", ["vardestjernen"]),
    (35, "Shieldheim", []),
    (36, "Helvedesmaskinen", []),
    (37, "Tempus' lynkile", []),
    (38, "Delegationen til Lord Magdova", ["stirling"]),
    (39, "Tilbage til Vardestjernen", ["vardestjernen"]),
    (40, "Vardestjernens dybder", ["vardestjernen", "port-drakkan"]),
    (41, "Besøg i Soltræet", ["soltraeet", "visdommens-kammer", "krypten"]),
    (42, "ShipJacking", ["port-drakkan", "vinterspiret"]),
    (43, "Sejlads i skyerne", ["vardestjernen", "port-alexander"]),
    (44, "Redningsmission i Feywood – den lilla horde", ["feywood", "astley"]),
    (45, "Dracolichen angriber", ["soltraeet"]),
    (45.5, "Logans tur til Skullborg", []),
    (46, "Under Soltræet", ["soltraeet", "hjertekammeret"]),
    (47, "Efter drageessensen", ["astley", "mausoleum", "gamle-tempel"]),
]

# Location values in People/Factions properties that name a place differently than its note.
# Values are PLACES ids, or "region:<id>".
LOCATION_ALIASES = {
    "Bronzekeg": "kegville", "Dark Gem Clan Caves": "dark-gem", "Stirling": "stirling",
    "Hertugdømmet Botreaux": "region:botreaux", "Vinterspiret 1": "vinterspiret",
    "Nordlandet": "region:nordheim", "Nord Heim": "region:nordheim", "De Ældstes Haller": "dvaerge-haller",
    "Baroniet Botreaux": "region:botreaux", "Bortreaux": "botreaux-by", "Welles": "region:welles",
    "Eresby": "region:eresby", "Slatestone dværgehallerne": "slatestone", "Sir Seillings mausoleum 1": "mausoleum",
    "Kobold hulerne": "dark-gem", "Windbreaker waystation": "crater-shrine", "Whisperwind": "whisperwind",
    "Nord distriktet": "astley", "Vestporten": "astley", "Varehusområdet": "astley",
    "Inn near Grøndalen": "vinterskov", "Nordlandet (jagthytte)": "region:nordheim", "Ettin-øerne": "region:nordheim",
    "De 6 sølvstykker": "port-drakkan", "De 6 sølvstykker (tavern)": "port-drakkan",
    "Jullan": "kolitan", "Jullan/Yuulan": "kolitan", "Highguard Chapterhouse": "anaksa",
}

# Location notes that are overviews or misfiled, not places to put on a map.
NOT_PLACES = {"Erukana", "ErukanaMap", "Locationsvisited", "Region - Bortholme - Erukana",
              "States and Baronies of Erukana", "Troldmands tårne", "Vinterskov - Grøndalen - Erukana.png", "skur",
              "Nord Heim", "Erukana1"}

# The party (player characters and companions), shown in the people register with a "Gruppen" filter.
# Some live in Characters/, some in People/. Titles as in the notes.
PARTY = ["Clarabel Lancaster", "Sir Winston", "Nibar", "Vargoth Sul", "Logan", "Isilme", "Bjørn of Nordheim",
         "Viktor Baigorri", "Fritte", "Corwin"]
# Status the notes lack but the logs state (note title -> (status, source)).
PARTY_STATUS = {
    "Vargoth Sul": ("dead", "Faldt i frostkæmpe-bagholdet i session 27, begravet i session 28."),
    "Corwin": ("", "Ifølge Bahne: Ærketroldmanden Ægrin antydede i session 47, at Corwin måske er blevet en skurk. "
                   "Det står ikke i loggen."),
}
# Class per party member, according to Bahne (overrides the character notes). Race: (race, source) where
# no character note gives it but the logs do.
PARTY_CLASS = {
    "Bjørn of Nordheim": "Barbarian",
    "Sir Winston": "Fighter (Battlemaster), ridder af Queensguarden",
    "Clarabel Lancaster": "War cleric af Mielikki",
    "Corwin": "Druid",
    "Evelyn Adair": "Life cleric af Mishakal",
    "Isilme": "Druid (Circle of the Moon)",
    "Logan": "Fighter (Battlemaster) / Rogue (Assassin)",
    "Nibar": "Wizard (Evoker)",
    "Vargoth Sul": "War cleric",
    "Viktor Baigorri": "Fighter (Eldritch Knight) / Wizard",
}
PARTY_RACE = {"Evelyn Adair": "Human", "Corwin": "Human", "Isilme": "Elf"}

# Party members without a note of their own: shown from what the logs say.
PARTY_EXTRA = {
    "Evelyn Adair": dict(aliases=["Evelyn", "Adare", "Adair"], race="", social="", role="", dead=True,
                         statusNote="Ifølge Bahne: død. Gav frivilligt sin essens til tidsartifaktet i session 46, "
                                    "til kun kroppen var tilbage."),
}

# Entries in People/Factions notes that link to a place but are not people or factions there.
NOT_PEOPLE = {"Mielikki", "Paladine", "Bahamut", "Morgion", "Orker", "Hydra", "Segreve", "Silverstream",
              "Jullan", "Logan", "Nibar", "knight aberrants", "Queensguard Lord Command Promotion Ritual",
              "Baronen af Morbray"}
