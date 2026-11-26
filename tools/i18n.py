#!/usr/bin/env python3
"""FR/EN translation helper for the Charette family sites.

Workflow per page (paths relative to repo root):
  python tools/i18n.py extract caron/caron.htm
      -> writes tools/translations/caron/caron.htm.fr.txt (French segments, numbered)
  (translator writes tools/translations/caron/caron.htm.en.txt with the same @@ ids)
  python tools/i18n.py build caron/caron.htm
      -> writes caron/caron.en.htm, adds lang + FR|EN selector to both pages
  python tools/i18n.py relink
      -> in every *.en.htm(l), points internal page links at .en versions that exist
         (safe to re-run as more pages get translated)
  python tools/i18n.py status   -> lists pages and whether an English version exists

Segment file format:  a line "@@ <id>" followed by the segment's HTML (may span lines).
Segments keep inline tags (<font>, <b>, <a>, <br>...) which must be preserved in the
translation; block tags (p, td, div, table, li, h1..) split segments. Ids "aN" are
alt/title attribute values.
"""
import os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TDIR = os.path.join(ROOT, 'tools', 'translations')
SKIP_DIRS = {'.git', 'tools', 'math_anglais', '_borders', '_derived', '_overlay', '_themes', '_vti_cnf', '_vti_pvt', '_private'}

BLOCK = set('html head body title p div center table tbody thead tr td th ul ol li dl dt dd '
            'h1 h2 h3 h4 h5 h6 blockquote form select option textarea pre hr '
            'address caption map area frameset frame noframes meta link'.split())
TOKEN = re.compile(r'<!--.*?-->|<(script|style)\b.*?</\1\s*>|<[^>]+>|[^<]+', re.S | re.I)
TAGNAME = re.compile(r'<\s*/?\s*([a-zA-Z0-9]+)')
LETTER = re.compile(r'[A-Za-zÀ-ÿ]')
ATTR = re.compile(r'''(\s(?:alt|title)\s*=\s*)("[^"]*"|'[^']*')''', re.I)


def is_en(path):
    return bool(re.search(r'\.en\.html?$', path, re.I))


def en_name(path):
    b, e = os.path.splitext(path)
    return b + '.en' + e


def fr_name(path):
    return re.sub(r'\.en(\.html?)$', r'\1', path, flags=re.I)


def read(p):
    with open(p, encoding='utf-8', newline='') as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
    with open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(s)


def strip_switch(src):
    return re.sub(re.escape(SW_START) + '.*?' + re.escape(SW_END), '', src, flags=re.S)


def segments(src, number_title=False):
    """Return list of (id, start, end, text) for translatable spans. Call on strip_switch(src).
    The <title> text gets id 'title' (so changing a title never renumbers the other segments)."""
    toks = [(m.start(), m.end(), m.group(0)) for m in TOKEN.finditer(src)]
    segs, run, in_head, in_title = [], [], False, False
    n = a = 0

    def flush():
        nonlocal n, run
        texts = [i for i, t in enumerate(run) if not t[2].startswith('<') and LETTER.search(html.unescape(t[2]))]
        if texts and (not in_head or in_title):
            s0, e0 = run[texts[0]][0], run[texts[-1]][1]
            # trim surrounding whitespace / nbsp inside the first/last text tokens
            seg = src[s0:e0]
            lead = len(seg) - len(re.sub(r'^(?:\s|&nbsp;)+', '', seg))
            trail = len(seg) - len(re.sub(r'(?:\s|&nbsp;)+$', '', seg))
            s0 += lead; e0 -= trail
            if in_title and not number_title:
                segs.append(('title', s0, e0, src[s0:e0]))
            else:
                n += 1
                segs.append((str(n), s0, e0, src[s0:e0]))
        run = []

    for s, e, t in toks:
        if t.startswith('<'):
            if t.startswith('<!--') or re.match(r'<(script|style)\b', t, re.I):
                flush(); continue
            m = TAGNAME.match(t)
            name = m.group(1).lower() if m else ''
            closing = t.lstrip('<').lstrip().startswith('/')
            for am in ATTR.finditer(t):
                val = am.group(2)[1:-1]
                if LETTER.search(html.unescape(val)) and not in_head:
                    a += 1
                    vs = s + am.start(2) + 1
                    segs.append(('a%d' % a, vs, vs + len(val), val))
            if name in BLOCK:
                flush()
                if name == 'head': in_head = not closing
                if name == 'title': in_title = not closing
                continue
            run.append((s, e, t))
        else:
            run.append((s, e, t))
    flush()
    # drop attribute segments that sit inside a text segment (the translator edits them in place there)
    spans = [(a0, b0) for i, a0, b0, _ in segs if not i.startswith('a')]
    segs = [x for x in segs if not (x[0].startswith('a') and any(a0 <= x[1] < b0 for a0, b0 in spans))]
    return segs


MONTHS = {'janvier': 'January', 'février': 'February', 'fevrier': 'February', 'mars': 'March', 'avril': 'April',
          'mai': 'May', 'juin': 'June', 'juillet': 'July', 'août': 'August', 'aout': 'August',
          'septembre': 'September', 'octobre': 'October', 'novembre': 'November', 'décembre': 'December',
          'decembre': 'December'}
LABELS = {'né': 'born', 'née': 'born', 'décédé': 'died', 'décédée': 'died', 'baptisé': 'baptized',
          'baptisée': 'baptized', 'inhumé': 'buried', 'inhumée': 'buried', 'marié': 'married', 'mariée': 'married',
          'mariage': 'marriage', 'naissance': 'birth', 'décès': 'death', 'sépulture': 'burial', 'baptême': 'baptism',
          'vers': 'circa', 'le': ''}
FRWORDS = set('''le la les de du des et en à au aux un une sur dans par pour avec chez son sa ses leur leurs
nos notre vos votre mon ma mes qui que est sont il elle ils elles nous vous on ce cette ces
génération générations mariage naissance baptême sépulture décès deuxième troisième quatrième première premier
famille enfants enfant fils fille filles père mère épouse époux veuve veuf ancêtre ancêtres lignée église paroisse
rue chemin terre terres seigneurie accueil plan site suite retour page haut bas précédente suivante sources
source voir photo photos carte cartes acte actes contrat notaire recensement vie mort mariés frère soeur sœur
oncle tante cousin cousine parrain marraine grand-père grand-mère grands-parents petits-enfants baptisé née né
décédé décédée inhumé inhumée vers avant après sans titre nouvelle archives souvenirs les
registres registre état civil copie bibliographie voir suite fin début mariages baptêmes sépultures liste index'''.split())


def _strip(t):
    return html.unescape(re.sub(r'<[^>]+>', ' ', t)).replace('\xa0', ' ')


def auto(t):
    """Mechanical translation for segments that are only dates, date labels or proper names; else None."""
    m = re.match(r'^([^<>]+?\.(?:jpe?g|gif|png|bmp)\s*\(\d+\s*)octets(\))$', t.strip(), re.I)
    if m:
        return m.group(1) + 'bytes' + m.group(2)
    plain = _strip(t)
    words = re.findall(r"[^\s.,;:()«»\"'’\-–—/*?!]+(?:[-'’][^\s.,;:()«»\"'’\-–—/*?!]+)*", plain)
    if not words:
        return None
    mon = '|'.join(MONTHS)
    date_re = re.compile(r'(?:(1er|\d{1,2})(\s|&nbsp;)+)?(%s)((?:\s|&nbsp;)+)(\d{4})' % mon, re.I)
    lw = [w.lower() for w in words]
    # date-ish: every word is a number, a month, or a label
    if all(w.isdigit() or w in MONTHS or w == '1er' or w in LABELS for w in lw) and any(w in MONTHS for w in lw):
        def dm(m):
            d, mo, y = m.group(1), MONTHS[m.group(3).lower()], m.group(5)
            d = '1' if d == '1er' else d
            return ('%s %s, %s' % (mo, d, y)) if d else '%s %s' % (mo, y)
        out = date_re.sub(dm, t)
        if re.search(r'(?i)\b(%s)\b' % mon, re.sub(r'<[^>]+>', '', out)):
            return None  # some month left (odd layout, e.g. day/month split by newline) -> manual
        def lab(m):
            w = m.group(0); e = LABELS[w.lower()]
            return e.capitalize() if w[0].isupper() and e else e
        out = re.sub(r'(?<![\w-])(%s)(?![\w-])' % '|'.join(sorted((k for k in LABELS if LABELS[k]), key=len, reverse=True)), lab, out, flags=re.I)
        return out
    # proper names / numbers only
    if any(w.lower() in FRWORDS for w in words):
        return None
    if any(re.match(r"^[DL]['’]", w) and w.isupper() for w in words):
        return None
    caps = [w for w in words if w.isupper() and len(w) > 1]
    if len(caps) > 4:
        return None
    if all(w[0].isupper() or w.isdigit() or w.lower() in ('dit', 'dite', 'de', 'du', 'la', 'le', 'des', 'st', 'ste') for w in words) \
            and any(w[0].isupper() for w in words):
        return t
    if all(not LETTER.search(w) for w in words):
        return t
    return None


def seg_path(page, lang):
    return os.path.join(TDIR, page + '.%s.txt' % lang)


def dump(segs):
    return ''.join('@@ %s\n%s\n' % (i, t.replace('\r\n', '\n')) for i, _, _, t in segs)


def parse(txt):
    out, cur, buf = {}, None, []
    for line in txt.splitlines():
        m = re.match(r'^@@ (\S+)\s*$', line)
        if m:
            if cur is not None: out.setdefault(cur, '\n'.join(buf).strip('\n'))
            cur, buf = m.group(1), []
        else:
            buf.append(line)
    if cur is not None: out.setdefault(cur, '\n'.join(buf).strip('\n'))
    return out


_TM = None


def _norm(t):
    return re.sub(r'\s+', ' ', t.replace('\r', '')).strip()


def tm():
    """Translation memory: normalized French segment -> English, from every page already translated."""
    global _TM
    if _TM is None:
        _TM = {}
        for dp, dns, fns in os.walk(TDIR):
            for f in fns:
                if not f.endswith('.en.txt'):
                    continue
                page = os.path.relpath(os.path.join(dp, f), TDIR)[:-len('.en.txt')].replace(os.sep, '/')
                fp = os.path.join(ROOT, page)
                if not os.path.isfile(fp):
                    continue
                tr = parse(read(os.path.join(dp, f)))
                for i, _, _, t in segments(strip_switch(read(fp))):
                    if i in tr and i != 'title' and len(_norm(t)) > 3:
                        _TM.setdefault(_norm(t), tr[i])
    return _TM


def lookup(t):
    a = auto(t)
    if a is not None:
        return a
    return tm().get(_norm(t))


def extract(page):
    """Writes <page>.fr.txt with the segments that need a human translation, and <page>.auto.txt
    with the segments handled mechanically (dates, names) for review."""
    src = strip_switch(read(os.path.join(ROOT, page)))
    segs = segments(src)
    manual = [x for x in segs if lookup(x[3]) is None]
    autos = [(i, a, b, lookup(t)) for i, a, b, t in segs if lookup(t) is not None]
    write(seg_path(page, 'fr'), dump(manual))
    write(seg_path(page, 'auto'), dump(autos))
    print('%s: %d segments (%d manual, %d auto/memory)' % (page, len(segs), len(manual), len(autos)))


SW_START, SW_END = '<!--lang-switch-->', '<!--/lang-switch-->'
SW_STYLE = ('position:fixed;top:6px;right:8px;z-index:9999;margin:0;padding:2px 7px;'
            'font:12px/1.5 Arial,Helvetica,sans-serif;color:#555;background:rgba(255,255,255,.85);'
            'border:1px solid #ccc;border-radius:3px;text-align:right')


# page-mathieu (French) <-> math_anglais (Nicole's own English version): same file names
TWIN_FR, TWIN_EN = 'page-mathieu', 'math_anglais'


def twin(page_rel):
    """Return the counterpart path for page-mathieu/math_anglais twins, else None."""
    parts = page_rel.replace(os.sep, '/').split('/')
    if len(parts) == 2 and parts[0] in (TWIN_FR, TWIN_EN):
        o = TWIN_EN if parts[0] == TWIN_FR else TWIN_FR
        if os.path.isfile(os.path.join(ROOT, o, parts[1])):
            return o + '/' + parts[1]
    return None


def switcher(page_rel, lang):
    """page_rel: this page's path relative to ROOT."""
    tw = twin(page_rel)
    if tw:
        other = '../' + tw
    else:
        other = os.path.basename(en_name(page_rel) if lang == 'fr' else fr_name(page_rel))
    cur = '<b style="color:#000">%s</b>'
    link = '<a href="%s" hreflang="%s" lang="%s" style="color:#555;text-decoration:none" title="%s">%s</a>'
    if lang == 'fr':
        fr = cur % 'FR'; en = link % (other, 'en', 'en', 'English version', 'EN')
    else:
        fr = link % (other, 'fr', 'fr', 'Version française', 'FR'); en = cur % 'EN'
    return '%s<div id="lang-switch" style="%s">%s | %s</div>%s' % (SW_START, SW_STYLE, fr, en, SW_END)


def set_lang(src, lang, page_rel):
    src = re.sub(re.escape(SW_START) + '.*?' + re.escape(SW_END), '', src, flags=re.S)
    m = re.search(r'<html\b[^>]*>', src, re.I)
    if m:
        tag = m.group(0)
        if re.search(r'\slang\s*=', tag, re.I):
            new = re.sub(r'''(\slang\s*=\s*)("[^"]*"|'[^']*'|\S+)''', r'\1"%s"' % lang, tag, flags=re.I)
        else:
            new = tag[:-1] + ' lang="%s">' % lang
        src = src[:m.start()] + new + src[m.end():]
    src = re.sub(r'''(<meta\s+http-equiv=["']?Content-Language["']?\s+content=["'])[^"']*''', r'\g<1>%s' % lang, src, flags=re.I)
    m = re.search(r'<body\b[^>]*>', src, re.I)
    sw = switcher(page_rel, lang)
    if m:
        src = src[:m.end()] + sw + src[m.end():]
    else:
        print('  WARNING: no <body> in', page_rel)
    return src


HREF = re.compile(r'''(<(?:a|area)\b[^>]*?\shref\s*=\s*)("[^"]*"|'[^']*'|[^\s>]+)''', re.I)


def relink_src(src, page_rel):
    d = os.path.dirname(os.path.join(ROOT, page_rel))
    count = 0

    def fix(m):
        nonlocal count
        raw = m.group(2)
        q = raw[0] if raw[0] in '"\'' else ''
        url = raw[1:-1] if q else raw
        if re.match(r'^[a-z][a-z0-9+.-]*:', url, re.I) or url.startswith(('#', '/')):
            return m.group(0)
        path, sep, frag = url.partition('#')
        path, qs, query = path.partition('?')
        if not re.search(r'\.html?$', path, re.I) or is_en(path):
            return m.group(0)
        target = os.path.normpath(os.path.join(d, html.unescape(path)))
        if os.path.isfile(en_name(target)):
            count += 1
            new = en_name(path) + (qs + query) + (sep + frag)
            return m.group(1) + q + new + q
        tw = twin(os.path.relpath(target, ROOT))
        if tw and os.path.relpath(target, ROOT).replace(os.sep, '/').startswith(TWIN_FR + '/'):
            count += 1
            new = os.path.relpath(os.path.join(ROOT, tw), d).replace(os.sep, '/') + (qs + query) + (sep + frag)
            return m.group(1) + q + new + q
        return m.group(0)
    # skip links inside the selector itself
    parts = re.split('(' + re.escape(SW_START) + '.*?' + re.escape(SW_END) + ')', src, flags=re.S)
    out = ''.join(p if p.startswith(SW_START) else HREF.sub(fix, p) for p in parts)
    return out, count


def set_title(src, t):
    t = html.escape(html.unescape(t), quote=False)
    if re.search(r'<title[^>]*>.*?</title>', src, re.I | re.S):
        return re.sub(r'(<title[^>]*>).*?(</title>)', lambda m: m.group(1) + t + m.group(2), src, count=1, flags=re.I | re.S)
    return re.sub(r'(</head>)', '<title>%s</title>\\1' % t.replace('\\', '\\\\'), src, count=1, flags=re.I)


def set_fr_only(page):
    """For a French page whose English twin already exists elsewhere (math_anglais): just lang + selector."""
    p = os.path.join(ROOT, page)
    write(p, set_lang(read(p), 'fr' if not page.startswith(TWIN_EN) else 'en', page))
    print('selector only:', page)


def build(page):
    fr_path = os.path.join(ROOT, page)
    src = strip_switch(read(fr_path))
    segs = segments(src)
    tr = parse(read(seg_path(page, 'en')))
    missing = [i for i, _, _, t in segs if i not in tr and lookup(t) is None]
    if 'title' not in [x[0] for x in segs] and 'title' not in tr:
        print('  WARNING %s: page has no title - add @@ frtitle and @@ title' % page)
    if re.search(r'<title>\s*(Nouvelle page|Page d.accueil|Accueil)', src, re.I) and 'frtitle' not in tr:
        print('  NOTE %s: placeholder-like title, consider @@ frtitle' % page)
    if missing:
        print('  WARNING %s: %d untranslated segments: %s' % (page, len(missing), ' '.join(missing[:20])))
    # sanity: inline tag count must match
    for i, s, e, t in segs:
        if i in tr and not i.startswith('a') and i != 'title':
            ft = re.findall(r'<\s*/?\s*[a-zA-Z]+', t); et = re.findall(r'<\s*/?\s*[a-zA-Z]+', tr[i])
            if sorted(x.lower().replace(' ', '') for x in ft) != sorted(x.lower().replace(' ', '') for x in et):
                print('  WARNING %s seg %s: inline tags differ' % (page, i))
    out, pos = [], 0
    for i, s, e, t in sorted(segs, key=lambda x: x[1]):
        out.append(src[pos:s])
        val = tr.get(i)
        if val is None:
            val = lookup(t)
        if val is None:
            val = t
        if '\r\n' in src:
            val = val.replace('\r\n', '\n').replace('\n', '\r\n')
        if i.startswith('a'):
            val = val.replace('"', '&quot;')
        if i == 'title':
            val = html.escape(html.unescape(val), quote=False)
        elif not i.startswith('a'):
            def fixattr(m):
                v = m.group(2)[1:-1]
                a = auto(v) if LETTER.search(v) else None
                return m.group(1) + m.group(2)[0] + (a if a is not None else v) + m.group(2)[0]
            val = re.sub(r'(<img\b[^>]*?\s(?:alt|title)\s*=\s*)("[^"]*"|\'[^\']*\')', lambda m: fixattr(m), val)
        out.append(val)
        pos = e
    out.append(src[pos:])
    en_src = ''.join(out)
    if 'title' in tr:
        en_src = set_title(en_src, tr['title'])
    if 'frtitle' in tr:
        src = set_title(src, tr['frtitle'])
    en_rel = en_name(page)
    en_src = set_lang(en_src, 'en', en_rel)
    write(os.path.join(ROOT, en_rel), en_src)
    write(fr_path, set_lang(src, 'fr', page))
    print('%s -> %s (%d segments)' % (page, en_rel, len(segs)))


def all_pages():
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = sorted(x for x in dns if x not in SKIP_DIRS)
        for f in sorted(fns):
            if re.search(r'\.html?$', f, re.I) and not is_en(f):
                yield os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, '/')


def relink():
    tot = 0
    for page in all_pages():
        en_rel = en_name(page)
        p = os.path.join(ROOT, en_rel)
        if os.path.isfile(p):
            s, c = relink_src(read(p), en_rel)
            write(p, s); tot += c
            print('%-45s %d links -> .en' % (en_rel, c))
    print('total rewritten (this pass):', tot)


def status():
    pages = list(all_pages()); done = [p for p in pages if os.path.isfile(os.path.join(ROOT, en_name(p))) or (twin(p) and SW_START in read(os.path.join(ROOT, p)))]
    for p in pages:
        print(('EN ' if p in done else '   ') + p)
    print('%d/%d pages have an English version' % (len(done), len(pages)))


if __name__ == '__main__':
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'extract':
        for p in args: extract(p)
    elif cmd == 'build':
        for p in args: build(p)
    elif cmd == 'twin':
        for p in args: set_fr_only(p)
    elif cmd == 'relink': relink()
    elif cmd == 'status': status()
    else: print(__doc__)
