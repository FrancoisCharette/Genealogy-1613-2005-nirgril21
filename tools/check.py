#!/usr/bin/env python3
"""Checks every page that has a FR|EN selector: selector target exists, and in English pages
every relative page/image link resolves on disk (reports links that were already broken in French too)."""
import os, re, sys, html, urllib.parse
sys.path.insert(0, os.path.dirname(__file__)); import i18n
R = i18n.ROOT
bad = 0; n = 0
for dp, dns, fns in os.walk(R):
    dns[:] = [d for d in dns if d not in ('.git', 'tools')]
    for f in fns:
        if not re.search(r'\.html?$', f, re.I): continue
        p = os.path.join(dp, f); src = i18n.read(p)
        m = re.search(re.escape(i18n.SW_START) + '.*?' + re.escape(i18n.SW_END), src, re.S)
        if not m: continue
        n += 1
        for h in re.findall(r'href="([^"]+)"', m.group(0)):
            if not os.path.isfile(os.path.normpath(os.path.join(dp, h))):
                print('SWITCH BROKEN', os.path.relpath(p, R), h); bad += 1
        if i18n.is_en(f):
            for h in re.findall(r'''<(?:a|area|img)\b[^>]*?\s(?:href|src)\s*=\s*["']?([^"'\s>]+)''', src, re.I):
                if re.match(r'(?i)^([a-z]+:|#)', h): continue
                path = urllib.parse.unquote(html.unescape(h.split('#')[0].split('?')[0]))
                if path and not os.path.exists(os.path.normpath(os.path.join(dp, path))):
                    frp = os.path.join(dp, i18n.fr_name(f))
                    pre = ' (also broken in French original)' if re.sub(r'\.en(\.html?)', r'\1', h, flags=re.I) in i18n.read(frp) else ''
                    print('LINK', os.path.relpath(p, R), h, pre); bad += 1 if not pre else 0
print('%d pages with selector checked, %d new problems' % (n, bad))
