# Archives familiales Charette — Genealogy

Nicole Charette's family history websites (ZoneCharette.ca, 2000–2010), restored as static pages for GitHub Pages.
Open `index.html` at the root for the list of sites.

Source: `D:\OneDrive\pictures\Archives\Nicoles sites Web` (copied, never modified).

## Sites and folder mapping

| Site | Original folder | Repo folder | Entry page |
|---|---|---|---|
| [ZoneCharette — page d'accueil](zone/index.html) | `zone` | `zone/` | `index.html` |
| [Les quatorze générations Charette d'Amérique](charette/index.html) | `charette` | `charette/` | `index.html` |
| [1re génération — Mathieu Choret](charettegen1/index.html) | `charettegen1` | `charettegen1/` | `index.html` |
| [2e génération — Pierre le Cadet](charettegen2/index.html) | `charettegen2` | `charettegen2/` | `index.html` |
| [3e génération — Pierre](charettegen3/index.html) | `charettegen3` | `charettegen3/` | `index.html` |
| [4e génération — Pierre et Marie Lemay](charettegen4/index.html) | `charettegen4` | `charettegen4/` | `index.html` |
| [5e génération — Jean-Baptiste](charettegen5/index.html) | `charettegen5` | `charettegen5/` | `index.html` |
| [6e génération — Jacques](charettegen6/index.html) | `charettegen6` | `charettegen6/` | `index.html` |
| [7e génération — Jacques](charettegen7/index.html) | `charettegen7` | `charettegen7/` | `index.html` |
| [8e et 9e générations — Les deux Alphonse](charettegen8-9/index.html) | `charettegen8-9` | `charettegen8-9/` | `index.html` |
| [10e génération — Rosario et Marie-Anna](charettegen10/index.html) | `charettegen10` | `charettegen10/` | `index.html` |
| [11e génération — Gérard Charette](charettegen11/index.html) | `charettegen11` | `charettegen11/` | `index.html` |
| [Les archives de la ZoneCharette](archives_zone/index.html) | `archives_zone` | `archives_zone/` | `index.html` |
| [Marie-Anna Caron et Rosario Charette](caron/index.html) | `Caron` | `caron/` | `index.html` |
| [Chez les Consigny](consigny_2/index.html) | `CONSIGNY_2` | `consigny_2/` | `index.html` |
| [La der des ders — Charles Consigny, 1914–1919](guerre-charles/index.html) | `GUERRE CHARLES` | `guerre-charles/` | `index.html` |
| [Deux vies en parallèle](2vies/index.html) | `2vies` | `2vies/` | `index.html` |
| [La Première Communion](communion/index.html) | `communion` | `communion/` | `index.html` |
| [Le reposoir](reposoir2/reposoir2.htm) | `reposoir2` | `reposoir2/` | `reposoir2.htm` |
| [Mathieu Choret (version antérieure)](page-mathieu/index.html) | `Page Mathieu` | `page-mathieu/` | `index.html` |
| [Mathieu Choret (English)](math_anglais/index.html) | `Math_anglais` | `math_anglais/` | `index.html` |

## What was changed from the originals

- Folder names made URL-safe (lowercase, no spaces).
- HTML converted from windows-1252 to UTF-8; `<meta charset="utf-8">` added.
- `<meta name="robots" content="noindex, nofollow">` on every page, plus `robots.txt` (disallow all), so search engines skip the site.
- Absolute links to `http://www.zonecharette.ca/genealogie_restraint/...` rewritten as relative links between the sites.
- Link/filename case mismatches fixed (GitHub Pages is case-sensitive); entry pages renamed to `index.html` where they were `index.htm`, `INDEX.htm` or `index.htmL`.
- FrontPage helper files (`_vti_*`, `__ti_*`, `_private`, …) left out. Images themselves are untouched, except that 14th-generation photo filenames that contained names were renamed (the photos were kept).
- `.nojekyll` so folders starting with `_` (FrontPage `_borders`) are served.
- For privacy, dates were removed from the 13th-generation pages (`charette/gen13.htm` and its English twin); names and dates were removed from the 14th-generation pages (`charette/gen14.htm` and its English twin). The new site in `histoire/` already omitted that information.

Not included: the `Vidéos` folder (3.8 GB) and `Archives ZoneCharette - tous les sites.pdf` (133 MB, over GitHub's 100 MB file limit).

## Preview locally

```
cd W:\projects\26familyGenealogy
python -m http.server 8000
```
then open http://localhost:8000/

## Version anglaise / English version

*FR —* Chaque page française a maintenant une jumelle anglaise (`page.en.htm` à côté de `page.htm`) et un sélecteur **FR | EN** en haut de page. Le texte est traduit, les images sont inchangées. Les contradictions repérées en cours de traduction sont listées dans [`INCONSISTENCIES.md`](INCONSISTENCIES.md) (rien n'a été corrigé).

*EN —* Every French page now has an English twin next to it and a **FR | EN** switch at the top. Only the text is translated; images are untouched. Contradictions found while translating are listed in [`INCONSISTENCIES.md`](INCONSISTENCIES.md) (nothing was corrected).

- **Naming:** `vie.htm` → `vie.en.htm`, `index.html` → `index.en.html`. The root `index.en.html` lists the English sites.
- **Not translated:** `math_anglais/` (it is already English; `page-mathieu/` pages switch FR | EN to their `math_anglais/` twins) and the FrontPage `_borders` / `_derived` helper folders.
- **Translations live in** `tools/translations/<site>/<page>.fr.txt` (French segments extracted from the page), `<page>.en.txt` (English, written by hand) and `<page>.auto.txt` (reused boilerplate such as menus and footers). The `.en.htm` pages are generated from these files, so edit the `.en.txt` and rebuild rather than editing an `.en.htm` by hand.

### Using `tools/i18n.py`

Run from the repo root (`cd W:\projects\26familyGenealogy`):

```
python tools/i18n.py extract charettegen5/vie.htm   # write the numbered French segments (.fr.txt)
python tools/i18n.py build   charettegen5/vie.htm   # make vie.en.htm from the .en.txt, add the FR | EN switch to both
python tools/i18n.py relink                          # point links in every .en page at English pages that exist
python tools/i18n.py status                          # list pages and whether each has an English version
python tools/i18n.py twin    page-mathieu/voyage.htm # only add the FR | EN switch (page-mathieu pages, whose English twin is in math_anglais/)
python tools/check.py                                # check every FR | EN switch target and the links in English pages
```

**`.en.txt` format:** a line `@@ <id>` followed by the English text for the segment with the same id in the `.fr.txt` (it may span several lines). Keep the inline tags (`<b>`, `<font>`, `<a href=…>`, `<br>`) exactly as in the French, or `build` prints a warning. Ids starting with `a` are image `alt`/`title` text.

- `@@ title` sets the English page title. If the French title was empty or a placeholder, add `@@ frtitle` too; it gives the French page a real title.
- If an id appears twice, the **first** one wins, so replace a segment rather than appending a second copy.
- Segments missing from the `.en.txt` fall back to `.auto.txt`; `build` warns about any still missing.

**To fix a translation:** edit the `.en.txt` file, run `build` on that page, then `relink`, and commit both the `.en.txt` and the `.en.htm`. **For a new or changed French page:** run `extract`, update the `.en.txt` to match the new ids, then `build` and `relink`.
