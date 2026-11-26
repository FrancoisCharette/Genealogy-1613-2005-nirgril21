#!/usr/bin/env python3
"""Builds index.en.html (English home page) from index.html.
Drops the French description lines, keeps the English ones, translates titles/dates,
then adds lang + FR|EN selector to both via tools/i18n.py helpers."""
import os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import i18n

R = i18n.ROOT
src = i18n.read(os.path.join(R, 'index.html'))
src = re.sub(re.escape(i18n.SW_START) + '.*?' + re.escape(i18n.SW_END), '', src, flags=re.S)
en = re.sub(r'\n\s*<p class="fr">.*?</p>', '', src)
en = en.replace('.en { color:#7a6a58; font-style:italic; }', '.en { color:#5a4a3a; }')

TITLES = {
 "ZoneCharette — page d&#x27;accueil": "ZoneCharette — home page",
 "Les quatorze générations Charette d&#x27;Amérique": "The fourteen Charette generations in America",
 "1re génération — Mathieu Choret": "1st generation — Mathieu Choret",
 "2e génération — Pierre le Cadet": "2nd generation — Pierre le Cadet (the younger)",
 "3e génération — Pierre": "3rd generation — Pierre",
 "4e génération — Pierre et Marie Lemay": "4th generation — Pierre and Marie Lemay",
 "5e génération — Jean-Baptiste": "5th generation — Jean-Baptiste",
 "6e génération — Jacques": "6th generation — Jacques",
 "7e génération — Jacques": "7th generation — Jacques",
 "8e et 9e générations — Les deux Alphonse": "8th and 9th generations — The two Alphonses",
 "10e génération — Rosario et Marie-Anna": "10th generation — Rosario and Marie-Anna",
 "11e génération — Gérard Charette": "11th generation — Gérard Charette",
 "Les archives de la ZoneCharette": "The ZoneCharette archives",
 "Marie-Anna Caron et Rosario Charette": "Marie-Anna Caron and Rosario Charette",
 "Chez les Consigny": "At the Consignys'",
 "La der des ders — Charles Consigny, 1914–1919": "La der des ders (the war to end all wars) — Charles Consigny, 1914–1919",
 "Deux vies en parallèle": "Two parallel lives (Deux vies en parallèle)",
 "La Première Communion": "First Communion",
 "Le reposoir": "Le reposoir (the wayside altar)",
 "Mathieu Choret (version antérieure)": "Mathieu Choret (earlier version)",
}
for fr, e in TITLES.items():
    en = en.replace('>%s</a>' % fr, '>%s</a>' % e)

MONTHS = {'janv.': 'Jan.', 'févr.': 'Feb.', 'mars': 'March', 'avril': 'April', 'mai': 'May',
          'juin': 'June', 'août': 'Aug.', 'sept.': 'Sept.', 'oct.': 'Oct.', 'nov.': 'Nov.'}
def date(s):
    s = s.replace('Créé en', 'Created').replace('Créé le', 'Created').replace('mis à jour le', 'updated') \
         .replace('mis à jour en', 'updated').replace('Mis à jour en', 'Updated').replace('refait en', 'rebuilt') \
         .replace('Actes ajoutés en', 'Records added in')
    def md(m):
        d, mo, y = m.group(1), m.group(2), m.group(3)
        mo = MONTHS.get(mo, mo)
        return '%s %s, %s' % (mo, d, y) if d else '%s %s' % (mo, y)
    return re.sub(r'(?:(\d+)\s+)?(janv\.|févr\.|mars|avril|mai|juin|août|sept\.|oct\.|nov\.)\s+(\d{4})', md, s)
en = re.sub(r'(<p class="d">)(.*?)(</p>)', lambda m: m.group(1) + date(m.group(2)) + m.group(3), en)

REPL = [
 ('<title>Archives familiales Charette — les sites de Nicole</title>', '<title>Charette family archives — Nicole\'s websites</title>'),
 ('<h1>Archives familiales Charette</h1>', '<h1>Charette family archives</h1>'),
 ('<p class="sub">Les sites web de Nicole Charette (ZoneCharette, 2000–2010), remis en ligne tels quels.<br>\n  <em>Nicole Charette\'s family history websites (ZoneCharette, 2000–2010), restored as they were.</em></p>',
  '<p class="sub">Nicole Charette\'s family history websites (ZoneCharette, 2000–2010), restored as they were. The sites were written in French; each page now has an English translation (use the FR | EN switch at the top right).</p>'),
 ('<footer>Sites créés par Nicole Charette, révisés par Francine Charette. Archive privée de la famille — merci de ne pas diffuser l\'adresse.<br>\n  <em>Created by Nicole Charette, proofread by Francine Charette. Private family archive — please don\'t share the address publicly.</em></footer>',
  '<footer>Created by Nicole Charette, proofread by Francine Charette. Private family archive — please don\'t share the address publicly.</footer>'),
]
for a, b in REPL:
    if a not in en: print('WARNING: not found:', a[:60])
    en = en.replace(a, b)
left = [l for l in re.findall(r'>([^<>]*[éèàç][^<>]*)<', en) if l.strip()]
print('lines still containing French accents (names are expected):', left)
i18n.write(os.path.join(R, 'index.en.html'), i18n.set_lang(en, 'en', 'index.en.html'))
i18n.write(os.path.join(R, 'index.html'), i18n.set_lang(src, 'fr', 'index.html'))
print('index.en.html written')
