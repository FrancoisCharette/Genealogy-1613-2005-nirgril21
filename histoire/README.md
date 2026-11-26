# histoire/ — le nouveau site chronologique / the new chronological site

*FR —* Une deuxième version, moderne, des sites de Nicole : le même contenu, en français et en anglais, remis en ordre chronologique. Les 21 sites d'origine ne sont pas modifiés ; chaque événement renvoie à sa page d'origine. Rien n'est inventé ni corrigé : quand les pages ne concordent pas, les deux valeurs sont affichées sous « Les sources diffèrent » (voir aussi `../INCONSISTENCIES.md`).

*EN —* A second, modern version of Nicole's sites: the same content, in French and English, put back in chronological order. The 21 original sites are untouched; every event links to the page it came from. Nothing is invented or corrected: when pages disagree, both values are shown under "Sources differ" (see also `../INCONSISTENCIES.md`).

## Pages

| Page | FR | EN |
|---|---|---|
| Home (periods 1613–2005, people) | `index.html` | `index.en.html` |
| Period c. 1613–1700 | `1613-1700.html` | `1613-1700.en.html` |
| Period 1700–1800 | `1700-1800.html` | `1700-1800.en.html` |
| Period 1800–1890 | `1800-1890.html` | `1800-1890.en.html` |
| Period 1890–1950 | `1890-1950.html` | `1890-1950.en.html` |
| Period 1950–2005 | `1950-2005.html` | `1950-2005.en.html` |
| People list | `personnes/index.html` | `personnes/index.en.html` |
| One person | `personnes/<id>.html` | `personnes/<id>.en.html` |

Plain static HTML + `assets/style.css` + a tiny `assets/site.js` (filter by person). No external fonts, CDNs or build step on GitHub Pages; every page has `noindex, nofollow`. Photos are not copied: pages point to the images already in the original site folders (`../charettegen10/images/...`).

## How it is built

**Never edit the `.html` files in `histoire/` by hand**: they are generated.

```
python tools/histoire.py          # rebuild all histoire/ pages from histoire/data/*.json
python tools/histoire.py --check  # rebuild + check every link, image and #anchor (case-sensitive)
python tools/histoire.py --segs caron/rosario.htm   # list the paragraph ids of an original page
```

Data (`histoire/data/`):

- `periods.json` — the periods on the home page. `"status": "ready"` makes a period page `<id>.html` (events whose `sort` year is ≥ the first year and < the second, e.g. `1890-1950` takes 1890–1949; the first period also takes earlier years, the last one also takes later years); `"soon"` shows "à venir / coming soon" plus the original sites to draw from.
- `events.json` — one object per event:
  - `id` (anchor), `sort` (`YYYY`, `YYYY-MM` or `YYYY-MM-DD`), `kind` (`birth`, `marriage`, `death`, `war`, `home`, `work`, `family`, `context`), `people` (ids from people.json)
  - `title` and optional `text`: `{"fr": …, "en": …}` — short, factual, taken from the pages (same translation rules: names and French place names kept, French terms glossed)
  - optional `when` `{"fr","en"}` to override the displayed date (e.g. "16 janvier 1917 ou 1916")
  - `sources`: original pages, e.g. `"charettegen10/m_a-ros.htm"` (the EN page links to the `.en` twin automatically)
  - optional `image` `{"src": "consigny_2/IMAGES/maries1.jpg", "caption": {"fr","en"}}` — use the caption from the original page
  - optional `excerpt`: `[{"page": "2vies/index.html", "seg": "3"}]` — Nicole's own paragraph, shown under "Texte de Nicole / Nicole's text", taken live from the French page and its existing English translation (ids from `--segs`)
  - optional `"undated": true` with `"period": "1890-1950"` (and `"sort": ""`): listed at the end of that period under "Souvenirs non datés / Undated memories"
  - optional `conflict`: `{"note": {"fr","en"}, "variants": [{"value": {"fr","en"}, "sources": [...]}, …]}` — two or more variants show "Les sources diffèrent / Sources differ"; one variant shows a "Note" (e.g. an age that doesn't match the dates). Events with conflicting dates are sorted under the earliest value; no value is chosen.
- `people.json` — person or family pages: `name` (a string, or `{"fr","en"}`), `years`, `period` (where the person is listed), optional `portrait` (initials are shown when there is none), key facts with sources, `spouse` (an id) or `spouse_name`, `parents`, `children`, excerpts. A person's timeline is every event whose `people` contains their id; each line links to the right period page.
- `sites.json` — titles of the original sites (used for "Source" links).

## Adding events or periods

1. Add events to `events.json` (sources, excerpts, conflicts as above), and any new people to `people.json`.
2. A new period goes in `periods.json` with `"status": "ready"` and an `intro`; it appears automatically in the period bar under the header, on the home page and in the previous/next links.
3. Run `python tools/histoire.py --check` (0 problems), then preview at `http://127.0.0.1:8000/histoire/`.

## Privacy

The site leaves out the young children of the 13th and 14th generations (charette/gen13, gen14) and anything else about living minors (names with birth dates, photos), the names of grandchildren born after 1946, and Nicole's email address. Living adults appear only as Nicole presents them, briefly (e.g. Gérard and Jacqueline's nine children are mentioned, not named or pictured). Keep it that way when adding events.
