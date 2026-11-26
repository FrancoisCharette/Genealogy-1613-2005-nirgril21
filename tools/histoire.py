#!/usr/bin/env python3
"""Generate the modern chronological site in histoire/ from histoire/data/*.json.

    python tools/histoire.py          # (re)build every page of histoire/
    python tools/histoire.py --check  # build, then check every link and image in histoire/

Data files (edit these, then rebuild):
  histoire/data/periods.json  periods shown on the home page (status "ready" = has a page)
  histoire/data/events.json   events (see README); "undated": true + "period" puts one under "Souvenirs non datés"
  histoire/data/people.json   person pages
  histoire/data/sites.json    titles of the 21 original sites (for "Source" links)

Excerpts ("Texte de Nicole") are read live from the original pages: {"page": "2vies/index.html", "seg": "3"}
uses segment 3 of that page as numbered by tools/i18n.py (same id in the French page and its .en twin).
Run `python tools/histoire.py --segs 2vies/index.html` to list the segment ids of a page.
Nothing outside histoire/ is ever written.
"""
import os, re, sys, json, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import i18n  # noqa: E402

H = os.path.join(ROOT, 'histoire')
LANGS = ('fr', 'en')
T = {
    'site': {'fr': 'Histoire de famille', 'en': 'Family history'},
    'brand_sub': {'fr': 'Charette · Caron · Côté · Consigny', 'en': 'Charette · Caron · Côté · Consigny'},
    'home': {'fr': 'Accueil', 'en': 'Home'},
    'people': {'fr': 'Personnes', 'en': 'People'},
    'originals': {'fr': "Sites d'origine", 'en': 'Original sites'},
    'source': {'fr': 'Source', 'en': 'Source'},
    'sources': {'fr': 'Sources', 'en': 'Sources'},
    'orig_page': {'fr': "page d'origine", 'en': 'original page'},
    'nicole': {'fr': 'Texte de Nicole', 'en': "Nicole's text"},
    'in_words': {'fr': 'Dans les mots de Nicole', 'en': "In Nicole's words"},
    'differ': {'fr': 'Les sources diffèrent', 'en': 'Sources differ'},
    'note': {'fr': 'À noter', 'en': 'Note'},
    'soon': {'fr': 'à venir', 'en': 'coming soon'},
    'open': {'fr': 'Ouvrir la période', 'en': 'Open this period'},
    'likely': {'fr': "Sites d'origine à intégrer", 'en': 'Original sites to draw from'},
    'all': {'fr': 'Tous', 'en': 'Everyone'},
    'filter': {'fr': 'Afficher :', 'en': 'Show:'},
    'events': {'fr': 'événements', 'en': 'events'},
    'key_dates': {'fr': 'Repères', 'en': 'Key facts'},
    'timeline': {'fr': 'Repères dans la chronologie', 'en': 'In the timeline'},
    'undated': {'fr': 'Souvenirs non datés', 'en': 'Undated memories'},
    'undated_s': {'fr': 'sans date', 'en': 'undated'},
    'periods': {'fr': 'Périodes', 'en': 'Periods'},
    'prev': {'fr': 'Période précédente', 'en': 'Previous period'},
    'next': {'fr': 'Période suivante', 'en': 'Next period'},
    'family': {'fr': 'Famille', 'en': 'Family'},
    'spouse': {'fr': 'Conjoint·e', 'en': 'Spouse'},
    'parents': {'fr': 'Parents', 'en': 'Parents'},
    'children': {'fr': 'Enfants', 'en': 'Children'},
    'footer': {'fr': "Contenu tiré des sites web de Nicole Charette (ZoneCharette, 2000–2010), révisés par Francine Charette. "
                     "Archive privée de la famille : merci de ne pas diffuser l'adresse.",
               'en': "Content drawn from Nicole Charette's websites (ZoneCharette, 2000–2010), proofread by Francine Charette. "
                     "Private family archive: please don't share the address publicly."},
    'kinds': {'birth': {'fr': 'Naissance', 'en': 'Birth'}, 'marriage': {'fr': 'Mariage', 'en': 'Marriage'},
              'death': {'fr': 'Décès', 'en': 'Death'}, 'war': {'fr': 'Guerre', 'en': 'War'},
              'home': {'fr': 'Logement', 'en': 'Home'}, 'work': {'fr': 'Travail', 'en': 'Work'},
              'family': {'fr': 'Famille', 'en': 'Family'}, 'context': {'fr': 'Contexte', 'en': 'Context'}},
}
MONTHS = {'fr': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
          'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']}


def load(name):
    with open(os.path.join(H, 'data', name), encoding='utf-8') as f:
        return json.load(f)


def esc(s):
    return html.escape(s, quote=True)


def nm(p, lang):
    """Name of a person entry: a string, or {"fr": ..., "en": ...}."""
    n = p['name'] if isinstance(p, dict) and 'name' in p else p
    return n[lang] if isinstance(n, dict) else n


def initials(name):
    w = [x for x in re.split(r'[\s\-()]+', name) if x and x[0].isupper()]
    return ''.join(x[0] for x in w[:2]) or name[:1]


def period_of(e, periods):
    """Id of the period an event belongs to: [start, end) except the last period, which takes everything after its start."""
    if e.get('undated'):
        return e['period']
    y = int(e['sort'][:4])
    for i, p in enumerate(periods):
        y0, y1 = (int(x) for x in p['id'].split('-'))
        if (i == 0 and y < y0) or y0 <= y < y1 or (i == len(periods) - 1 and y >= y0):
            return p['id']
    return periods[-1]['id']


_PERIODS = []


def suffix(lang):
    return '' if lang == 'fr' else '.en'


def fname(base, lang):
    return base + suffix(lang) + '.html'


def en_twin(rel):
    b, e = os.path.splitext(rel)
    return b + '.en' + e


def orig_href(rel, lang, up):
    """Link from a histoire page `up` levels deep to an original page, using the English twin when it exists."""
    if lang == 'en' and os.path.exists(os.path.join(ROOT, en_twin(rel))):
        rel = en_twin(rel)
    return '../' * up + rel


def fmt_date(sort, lang):
    p = sort.split('-')
    if len(p) == 1:
        return p[0]
    m = MONTHS[lang][int(p[1]) - 1]
    if len(p) == 2:
        return ('%s %s' % (m, p[0])) if lang == 'fr' else '%s %s' % (m, p[0])
    d = int(p[2])
    if lang == 'fr':
        return '%s %s %s' % ('1er' if d == 1 else d, m, p[0])
    return '%s %d, %s' % (m, d, p[0])


# ---------- excerpts from original pages ----------
_SEG = {}


def page_segs(rel):
    if rel not in _SEG:
        out = {}
        for lang, path in (('fr', rel), ('en', en_twin(rel))):
            full = os.path.join(ROOT, path)
            if not os.path.exists(full):
                continue
            src = i18n.strip_switch(i18n.read(full))
            out[lang] = {i: t for i, _, _, t in i18n.segments(src) if not i.startswith('a')}
        _SEG[rel] = out
    return _SEG[rel]


def clean(frag):
    s = re.sub(r'(?is)<br\s*/?>', ' ', frag)
    s = re.sub(r'(?is)<(/?)(b|strong)\b[^>]*>', r'<\1b>', s)
    s = re.sub(r'(?is)<(/?)(i|em)\b[^>]*>', r'<\1i>', s)
    s = re.sub(r'(?is)<(?!/?(b|i)>)[^>]+>', '', s)
    s = html.unescape(s).replace('\xa0', ' ')
    s = esc(s).replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>').replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'<b>\s*</b>|<i>\s*</i>', '', s)
    # balance stray tags left by FrontPage markup
    for t in ('b', 'i'):
        o, c = s.count('<%s>' % t), s.count('</%s>' % t)
        if o > c:
            s += '</%s>' % t * (o - c)
        elif c > o:
            s = '<%s>' % t * (c - o) + s
    return s


def excerpt(page, seg, lang):
    segs = page_segs(page)
    t = segs.get(lang, {}).get(seg) or segs.get('fr', {}).get(seg)
    if t is None:
        raise SystemExit('excerpt not found: %s seg %s' % (page, seg))
    return clean(t)


# ---------- page chrome ----------
CSS_V = "2"


def page(lang, up, title, body, here_base, desc=''):
    other = 'en' if lang == 'fr' else 'fr'
    root = '../' * up
    me = os.path.basename(here_base)
    sw = ('<b>FR</b> <span aria-hidden="true">|</span> <a href="%s" hreflang="en" lang="en">EN</a>' % fname(me, 'en')) if lang == 'fr' else \
         ('<a href="%s" hreflang="fr" lang="fr">FR</a> <span aria-hidden="true">|</span> <b>EN</b>' % fname(me, 'fr'))
    hroot = '../' * (up - 1)
    nav = ('<a href="{h}{home}">{t_home}</a><a href="{h}{ppl}">{t_ppl}</a>'
           '<a href="{r}{orig}">{t_orig}</a>').format(
        h=hroot, home=fname('index', lang), ppl='personnes/' + fname('index', lang),
        t_home=T['home'][lang], t_ppl=T['people'][lang], r=root, orig='index.html' if lang == 'fr' else 'index.en.html',
        t_orig=T['originals'][lang])
    pnav = ''.join('<a href="%s%s"%s>%s</a>' % (hroot, fname(p['id'], lang), ' aria-current="page"' if here_base == p['id'] else '',
                                                 esc(p['range'][lang])) for p in _PERIODS)
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — {T['site'][lang]}</title>
<link rel="alternate" hreflang="{other}" href="{fname(me, other)}">
<link rel="stylesheet" href="{hroot}assets/style.css?v={CSS_V}">
</head>
<body>
<header class="top">
  <div class="wrap top-in">
    <a class="brand" href="{hroot}{fname('index', lang)}"><span class="brand-t">{T['site'][lang]}</span><span class="brand-s">{T['brand_sub'][lang]}</span></a>
    <nav class="nav">{nav}</nav>
    <div class="lang">{sw}</div>
  </div>
  <nav class="pnav wrap" aria-label="{T['periods'][lang]}">{pnav}</nav>
</header>
<main class="wrap">
{body}
</main>
<footer class="foot"><div class="wrap">{esc(T['footer'][lang])}</div></footer>
<script src="{hroot}assets/site.js"></script>
</body>
</html>
'''


def src_label(rel, lang, sites):
    site = rel.split('/')[0]
    title = sites['titles'].get(site, {}).get(lang, site)
    pg = os.path.splitext(rel.split('/', 1)[1])[0]
    entry = os.path.splitext(sites['entry'].get(site, 'index.html'))[0]
    return title if pg == entry else '%s — %s' % (title, pg.split('/')[-1])


def src_links(sources, lang, up, sites):
    return ['<a href="%s">%s</a>' % (esc(orig_href(rel, lang, up)), esc(src_label(rel, lang, sites))) for rel in sources]


def figure(img, lang, up, cls='fig', name=''):
    if not img:
        return ('<div class="%s ph" aria-hidden="true"><span>%s</span></div>' % (cls, esc(initials(name)))) if name else ''
    cap = img['caption'][lang]
    return ('<figure class="%s"><a href="%s"><img loading="lazy" src="%s" alt="%s"></a><figcaption>%s</figcaption></figure>'
            % (cls, esc('../' * up + img['src']), esc('../' * up + img['src']), esc(cap), esc(cap)))


def conflict_box(c, lang, up, sites):
    rows = []
    for v in c['variants']:
        rows.append('<li><span class="cv">%s</span> — %s</li>' % (esc(v['value'][lang]), ', '.join(src_links(v['sources'], lang, up, sites))))
    note = c.get('note', {}).get(lang, '')
    head = T['differ'][lang] if len(c['variants']) > 1 else T['note'][lang]
    return ('<div class="conflict" role="note"><p class="ch">%s</p><ul>%s</ul>%s</div>'
            % (head, ''.join(rows), ('<p class="cn">%s</p>' % esc(note)) if note else ''))


def event_html(e, lang, up, sites, people_idx, show_people=True):
    when = e.get('when', {}).get(lang) or (T['undated_s'][lang] if e.get('undated') else fmt_date(e['sort'], lang))
    kind = T['kinds'][e['kind']][lang]
    chips = ''
    if show_people and e['people']:
        chips = '<p class="chips">' + ''.join(
            '<a class="chip" href="%spersonnes/%s">%s</a>' % ('../' * (up - 1), fname(p, lang), esc(nm(people_idx[p], lang)))
            for p in e['people'] if p in people_idx) + '</p>'
    text = ('<p class="et">%s</p>' % esc(e['text'][lang])) if e.get('text') else ''
    ex = ''
    if e.get('excerpt'):
        qs = ''.join('<blockquote>%s <cite><a href="%s">%s</a></cite></blockquote>' % (
            excerpt(x['page'], x['seg'], lang), esc(orig_href(x['page'], lang, up)), T['orig_page'][lang]) for x in e['excerpt'])
        ex = '<details class="ex"><summary>%s</summary>%s</details>' % (T['nicole'][lang], qs)
    conf = conflict_box(e['conflict'], lang, up, sites) if e.get('conflict') else ''
    srcs = '<p class="src">%s : %s</p>' % (T['sources'][lang] if len(e['sources']) > 1 else T['source'][lang],
                                           ' · '.join(src_links(e['sources'], lang, up, sites)))
    if lang == 'en':
        srcs = srcs.replace(' : ', ': ', 1)
    ppl = ' '.join(e['people'])
    return f'''<article class="ev k-{e['kind']}" id="{e['id']}" data-people="{ppl}">
  <div class="ev-date"><time>{esc(when)}</time><span class="kind">{kind}</span></div>
  <div class="ev-body">
    <h3><a class="anchor" href="#{e['id']}">{esc(e['title'][lang])}</a></h3>
    {text}{conf}{figure(e.get('image'), lang, up)}{ex}{chips}{srcs}
  </div>
</article>'''


def entry_rel(site, lang):
    """Entry page of an original site (English twin for 'en'); math_anglais has no twin."""
    sites = load('sites.json')
    rel = site + '/' + sites['entry'].get(site, 'index.html')
    if lang == 'en' and os.path.exists(os.path.join(ROOT, en_twin(rel))):
        rel = en_twin(rel)
    return rel


def pcard(p, lang, prefix):
    pic = ('<img loading="lazy" src="%s%s" alt="">' % (prefix, esc(p['portrait']['src']))) if p.get('portrait') else \
          '<span class="pc-ph" aria-hidden="true">%s</span>' % esc(initials(nm(p, lang)))
    return pic + '<span class="pc-n">%s</span><span class="pc-y">%s</span>' % (esc(nm(p, lang)), esc(p['years']))


def build():
    periods, events, people, sites = load('periods.json'), load('events.json'), load('people.json'), load('sites.json')
    _PERIODS[:] = [p for p in periods if p['status'] == 'ready']
    pidx = {p['id']: p for p in people}
    events.sort(key=lambda e: (e['sort'] + '-00-00')[:10] if not e.get('undated') else '9999')
    for e in events:
        e['_per'] = period_of(e, periods)
    written = []

    def write(rel, s):
        full = os.path.join(H, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8', newline='\n') as f:
            f.write(s)
        written.append(rel)

    def per_people(pid):
        """People with a page who take part in the events of a period, in the order of people.json."""
        ids = {x for e in events if e['_per'] == pid for x in e['people']}
        return [p for p in people if p['id'] in ids]

    for lang in LANGS:
        # ---- home ----
        cards = []
        for p in periods:
            sl = ''.join('<li><a href="../%s">%s</a></li>' % (esc(entry_rel(site, lang)), esc(sites['titles'][site][lang]))
                         for site in p['sites'])
            if p['status'] == 'ready':
                n = sum(1 for e in events if e['_per'] == p['id'])
                cards.append(f'''<li class="per ready"><a class="per-link" href="{fname(p['id'], lang)}">
  <span class="per-range">{esc(p['range'][lang])}</span><span class="per-title">{esc(p['title'][lang])}</span>
  <span class="per-meta">{n} {T['events'][lang]} · {len(per_people(p['id']))} {T['people'][lang].lower()}</span>
  <span class="per-intro">{esc(p.get('intro', {}).get(lang, ''))}</span><span class="per-go">{T['open'][lang]} →</span></a></li>''')
            else:
                cards.append(f'''<li class="per soon"><div class="per-link">
  <span class="per-range">{esc(p['range'][lang])}</span><span class="per-title">{esc(p['title'][lang])}</span>
  <span class="badge">{T['soon'][lang]}</span>
  <details class="per-sites"><summary>{T['likely'][lang]}</summary><ul>{sl}</ul></details></div></li>''')
        intro = {
            'fr': "<p class=\"lead\">Entre 2000 et 2010, Nicole Charette a raconté l'histoire de la famille dans une vingtaine de petits sites web. "
                  "Ce site-ci reprend leur contenu, en français et en anglais, et le remet <b>dans l'ordre chronologique</b>, "
                  "période par période. Chaque événement renvoie à la page d'origine d'où il vient.</p>"
                  "<p>Rien n'est inventé ni corrigé : quand deux pages ne donnent pas la même date, les deux sont affichées "
                  "avec la mention <span class=\"pill\">Les sources diffèrent</span>. Les sites d'origine restent consultables tels quels "
                  "(<a href=\"../index.html\">liste des sites d'origine</a>).</p>",
            'en': "<p class=\"lead\">Between 2000 and 2010, Nicole Charette told the family's story in about twenty small websites. "
                  "This site takes their content, in French and English, and puts it back <b>in chronological order</b>, "
                  "period by period. Every event links back to the original page it comes from.</p>"
                  "<p>Nothing is invented or corrected: when two pages give different dates, both are shown with the label "
                  "<span class=\"pill\">Sources differ</span>. The original sites are still available as they were "
                  "(<a href=\"../index.en.html\">list of the original sites</a>).</p>"}[lang]
        groups = ''.join('<h3 class="pgroup">%s — %s</h3><ul class="pcards">%s</ul>' % (
            esc(pr['range'][lang]), esc(pr['title'][lang]),
            ''.join('<li><a href="personnes/%s">%s</a></li>' % (fname(p['id'], lang), pcard(p, lang, '../')) for p in people if p.get('period') == pr['id']))
            for pr in _PERIODS if any(p.get('period') == pr['id'] for p in people))
        body = f'''<section class="hero"><h1>{ {'fr': "D'une génération à l'autre", 'en': 'From one generation to the next'}[lang] }</h1>{intro}</section>
<section><h2>{ {'fr': 'Les périodes', 'en': 'The periods'}[lang] }</h2><ol class="periods">{''.join(cards)}</ol></section>
<section><h2>{T['people'][lang]}</h2>{groups}</section>'''
        write(fname('index', lang), page(lang, 1, T['site'][lang], body, 'index'))

        # ---- period pages ----
        for i, p in enumerate(_PERIODS):
            evs = [e for e in events if e['_per'] == p['id'] and not e.get('undated')]
            und = [e for e in events if e['_per'] == p['id'] and e.get('undated')]
            decades, parts = [], []
            for e in evs:
                d = e['sort'][:3] + '0'
                if d not in decades:
                    decades.append(d)
                    parts.append('<h2 class="decade" id="d%s"><span>%s</span></h2>' % (d, d))
                parts.append(event_html(e, lang, 1, sites, pidx))
            dnav = ''.join('<a href="#d%s">%s</a>' % (d, d) for d in decades)
            if und:
                parts.append('<h2 class="decade undated" id="sans-date"><span>%s</span></h2>' % T['undated'][lang])
                parts.extend(event_html(e, lang, 1, sites, pidx) for e in und)
                dnav += '<a href="#sans-date">%s</a>' % T['undated_s'][lang]
            pp = per_people(p['id'])
            filt = '<div class="filter" hidden><span>%s</span><button type="button" data-p="" aria-pressed="true">%s</button>%s</div>' % (
                T['filter'][lang], T['all'][lang], ''.join('<button type="button" data-p="%s" aria-pressed="false">%s</button>' % (x['id'], esc(nm(x, lang))) for x in pp))
            nconf = sum(1 for e in evs + und if e.get('conflict') and len(e['conflict']['variants']) > 1)
            pn = []
            if i > 0:
                q = _PERIODS[i - 1]
                pn.append('<a class="prev" href="%s">← %s<br><b>%s</b></a>' % (fname(q['id'], lang), T['prev'][lang], esc(q['range'][lang] + ' — ' + q['title'][lang])))
            if i < len(_PERIODS) - 1:
                q = _PERIODS[i + 1]
                pn.append('<a class="next" href="%s">%s →<br><b>%s</b></a>' % (fname(q['id'], lang), T['next'][lang], esc(q['range'][lang] + ' — ' + q['title'][lang])))
            body = f'''<section class="hero"><p class="kicker">{esc(p['range'][lang])}</p><h1>{esc(p['title'][lang])}</h1>
<p class="lead">{esc(p.get('intro', {}).get(lang, ''))}</p>
<p class="meta">{len(evs) + len(und)} {T['events'][lang]} · <span class="pill">{T['differ'][lang]}</span> ×{nconf}</p></section>
<nav class="decades" aria-label="{ {'fr': 'Décennies', 'en': 'Decades'}[lang] }">{dnav}</nav>
{filt}
<div class="timeline">
{''.join(parts)}
</div>
<nav class="pernext">{''.join(pn)}</nav>'''
            write(fname(p['id'], lang), page(lang, 1, p['range'][lang] + ' — ' + p['title'][lang], body, p['id']))

        # ---- people ----
        groups = ''.join('<h2 class="pgroup">%s — %s</h2><ul class="pcards">%s</ul>' % (
            esc(pr['range'][lang]), esc(pr['title'][lang]),
            ''.join('<li><a href="%s">%s</a></li>' % (fname(p['id'], lang), pcard(p, lang, '../../')) for p in people if p.get('period') == pr['id']))
            for pr in _PERIODS if any(p.get('period') == pr['id'] for p in people))
        write('personnes/' + fname('index', lang), page(lang, 2, T['people'][lang],
              '<section class="hero"><h1>%s</h1><p class="lead">%s</p></section>%s' % (
                  T['people'][lang], {'fr': 'Les personnes et familles principales, classées selon la période où elles vivent.',
                                      'en': 'The main people and families, grouped by the period they lived in.'}[lang], groups), 'personnes/index'))
        for p in people:
            facts = ''.join('<dt>%s</dt><dd>%s <span class="fs">%s</span></dd>' % (
                esc(f['label'][lang]), esc(f['value'][lang]), ' · '.join(src_links(f['sources'], lang, 2, sites))) for f in p['facts'])
            fam = []
            if p.get('parents'):
                fam.append('<dt>%s</dt><dd>%s</dd>' % (T['parents'][lang], esc(p['parents'][lang])))
            if p.get('spouse') in pidx:
                fam.append('<dt>%s</dt><dd><a href="%s">%s</a></dd>' % (T['spouse'][lang], fname(p['spouse'], lang), esc(nm(pidx[p['spouse']], lang))))
            elif p.get('spouse_name'):
                sn = p['spouse_name']
                fam.append('<dt>%s</dt><dd>%s</dd>' % (T['spouse'][lang], esc(sn[lang] if isinstance(sn, dict) else sn)))
            if p.get('children'):
                fam.append('<dt>%s</dt><dd>%s</dd>' % (T['children'][lang], ', '.join(
                    ('<a href="%s">%s</a>' % (fname(c['id'], lang), esc(c['name'][lang]))) if c.get('id') in pidx else esc(c['name'][lang]) for c in p['children'])))
            evs = [e for e in events if p['id'] in e['people']]
            tl = ''.join('<li><time>%s</time> <a href="../%s#%s">%s</a>%s</li>' % (
                esc(e.get('when', {}).get(lang) or (T['undated_s'][lang] if e.get('undated') else fmt_date(e['sort'], lang))),
                fname(e['_per'], lang), e['id'], esc(e['title'][lang]),
                (' <span class="pill sm">%s</span>' % T['differ'][lang]) if e.get('conflict') and len(e['conflict']['variants']) > 1 else '') for e in evs)
            exs = ''.join('<blockquote>%s <cite><a href="%s">%s</a></cite></blockquote>' % (
                excerpt(x['page'], x['seg'], lang), esc(orig_href(x['page'], lang, 2)), esc(src_label(x['page'], lang, sites))) for x in p['excerpts'])
            body = f'''<section class="person">
<div class="p-head">{figure(p.get('portrait'), lang, 2, 'portrait', nm(p, lang))}
<div><p class="kicker">{esc(p['years'])}</p><h1>{esc(nm(p, lang))}</h1><p class="lead">{esc(p['summary'][lang])}</p>
<h2 class="sm">{T['key_dates'][lang]}</h2><dl class="facts">{facts}</dl>
<h2 class="sm">{T['family'][lang]}</h2><dl class="facts">{''.join(fam)}</dl></div></div>
<h2>{T['timeline'][lang]}</h2><ol class="mini">{tl}</ol>
<h2>{T['in_words'][lang]}</h2><div class="words">{exs}</div>
</section>'''
            write('personnes/' + fname(p['id'], lang), page(lang, 2, nm(p, lang), body, 'personnes/' + p['id']))
    return written


def check():
    """Every href/src in histoire/*.html must exist (case-sensitive), and every #anchor must exist."""
    bad = 0
    ids = {}
    files = []
    for dp, _, fn in os.walk(H):
        for f in fn:
            if f.endswith('.html'):
                files.append(os.path.join(dp, f))
    for f in files:
        ids[f] = set(re.findall(r'\sid="([^"]+)"', open(f, encoding='utf-8').read()))
    n = 0
    for f in files:
        s = open(f, encoding='utf-8').read()
        for u in re.findall(r'(?:href|src)="([^"]+)"', s):
            n += 1
            if re.match(r'^[a-z]+:', u):
                print('EXTERNAL', os.path.relpath(f, ROOT), u); bad += 1; continue
            path, _, frag = html.unescape(u).partition('#')
            path = path.split('?')[0]
            tgt = os.path.normpath(os.path.join(os.path.dirname(f), path)) if path else f
            d, b = os.path.split(tgt)
            if not (os.path.isdir(d) and b in os.listdir(d)):
                print('MISSING', os.path.relpath(f, ROOT), u); bad += 1; continue
            if frag and tgt.endswith('.html') and tgt in ids and frag not in ids[tgt]:
                print('NO ANCHOR', os.path.relpath(f, ROOT), u); bad += 1
    print('checked %d links/images in %d pages: %d problem(s)' % (n, len(files), bad))
    return bad


if __name__ == '__main__':
    if '--segs' in sys.argv:
        for rel in sys.argv[sys.argv.index('--segs') + 1:]:
            for k, v in page_segs(rel).get('fr', {}).items():
                print(k, '|', re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', v)))[:110])
        sys.exit(0)
    w = build()
    print('wrote %d pages in histoire/' % len(w))
    if '--check' in sys.argv:
        sys.exit(1 if check() else 0)
