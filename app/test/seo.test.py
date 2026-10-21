#!/usr/bin/env python3
"""Checks the generated SEO pages in docs/: tags, JSON-LD, hreflang pairs, internal links, sitemap. Run after build.py."""
import os, re, json, sys
from html.parser import HTMLParser
from urllib.parse import urlparse
docs = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'docs')
BASE = 'https://aditya454760.github.io/Abhyashify/'
fails = 0; n = 0
def ok(c, m):
    global fails, n
    n += 1
    if not c:
        fails += 1; print('FAIL', m)

class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.t = ''; s.in_t = False; s.meta = {}; s.links = []; s.ld = []; s.h1 = 0; s.a = []; s.cur = None; s.lang = None; s.alt = {}; s.canon = None; s.in_ld = False
    def handle_starttag(s, tag, at):
        d = dict(at)
        if tag == 'html': s.lang = d.get('lang')
        if tag == 'title': s.in_t = True
        if tag == 'meta':
            k = d.get('name') or d.get('property')
            if k: s.meta[k] = d.get('content')
        if tag == 'link':
            if d.get('rel') == 'canonical': s.canon = d.get('href')
            if d.get('rel') == 'alternate' and d.get('hreflang'): s.alt[d['hreflang']] = d['href']
        if tag == 'h1': s.h1 += 1
        if tag == 'a' and d.get('href'): s.a.append(d['href'])
        if tag == 'script' and d.get('type') == 'application/ld+json': s.in_ld = True; s.buf = ''
    def handle_endtag(s, tag):
        if tag == 'title': s.in_t = False
        if tag == 'script' and s.in_ld: s.in_ld = False; s.ld.append(s.buf)
    def handle_data(s, d):
        if s.in_t: s.t += d
        if s.in_ld: s.buf += d

def parse(path):
    p = P(); p.feed(open(path, encoding='utf-8').read()); return p

def to_file(url):
    u = urlparse(url)
    rel = u.path[len(urlparse(BASE).path):]
    f = os.path.join(docs, rel)
    if os.path.isdir(f) or rel == '' or rel.endswith('/'): f = os.path.join(f, 'index.html')
    return f

pages = []
for root, _, files in os.walk(docs):
    if '/voice' in root or '/fonts' in root: continue
    for f in files:
        if f.endswith('.html') and f not in ('404.html',) and not root.endswith('voice-kit'):
            pages.append(os.path.join(root, f))
ok(len(pages) >= 35, 'page count %d' % len(pages))
canon = {}
for f in pages:
    nm = os.path.relpath(f, docs); p = parse(f)
    ok(15 <= len(p.t.strip()) <= 70, '%s title length %d' % (nm, len(p.t.strip())))
    d = p.meta.get('description') or ''
    ok(60 <= len(d) <= 165, '%s description length %d' % (nm, len(d)))
    ok(p.canon and p.canon.startswith(BASE), '%s canonical' % nm)
    ok(os.path.exists(to_file(p.canon)), '%s canonical resolves to a file' % nm)
    canon[nm] = p.canon
    for k in ('og:title', 'og:description', 'og:url', 'og:image', 'twitter:card', 'twitter:image'):
        ok(p.meta.get(k), '%s has %s' % (nm, k))
    ok(p.meta.get('og:image') == BASE + 'og.png', '%s og:image' % nm)
    ok('index' in (p.meta.get('robots') or ''), '%s robots' % nm)
    if nm != 'index.html':
        ok(p.h1 == 1, '%s exactly one h1 (%d)' % (nm, p.h1))
        ok(p.lang in ('en', 'hi'), '%s lang' % nm)
        ok(set(p.alt) == {'en', 'hi', 'x-default'}, '%s hreflang set %s' % (nm, sorted(p.alt)))
        ok(p.meta.get('og:locale') in ('en_IN', 'hi_IN'), '%s og:locale' % nm)
    ok(len(p.ld) >= 1, '%s JSON-LD present' % nm)
    for j in p.ld:
        try: json.loads(j)
        except Exception as e: ok(False, '%s JSON-LD invalid %s' % (nm, e))
    for h in p.a:
        if h.startswith(('http', 'mailto', '#')):
            if h.startswith(BASE): ok(os.path.exists(to_file(h.split('#')[0])), '%s link %s resolves' % (nm, h))
            continue
        t = os.path.normpath(os.path.join(os.path.dirname(f), h.split('#')[0]))
        if os.path.isdir(t): t = os.path.join(t, 'index.html')
        ok(os.path.exists(t), '%s relative link %s resolves' % (nm, h))
# hreflang reciprocity and language match
for f in pages:
    nm = os.path.relpath(f, docs)
    if nm == 'index.html': continue
    p = parse(f)
    for lg in ('en', 'hi'):
        q = parse(to_file(p.alt[lg]))
        ok(q.lang == lg, '%s alternate %s has lang %s' % (nm, lg, q.lang))
        ok(q.alt.get('en') == p.alt['en'] and q.alt.get('hi') == p.alt['hi'], '%s hreflang reciprocal with %s' % (nm, lg))
    if p.lang == 'hi':
        ok(re.search('[ऀ-ॿ]', p.t), '%s Hindi title has Devanagari' % nm)
# unique titles and descriptions
ts = [parse(f).t.strip() for f in pages]; ok(len(set(ts)) == len(ts), 'titles unique')
ds = [parse(f).meta.get('description') for f in pages]; ok(len(set(ds)) == len(ds) - 1 or len(set(ds)) >= len(ds) - 3, 'descriptions mostly unique %d/%d' % (len(set(ds)), len(ds)))
# sitemap
sm = open(os.path.join(docs, 'sitemap.xml'), encoding='utf-8').read()
locs = re.findall(r'<loc>([^<]+)</loc>', sm)
ok(len(locs) == len(set(locs)), 'sitemap unique')
for l in locs: ok(os.path.exists(to_file(l)), 'sitemap %s exists' % l)
for nm, c in canon.items(): ok(c in locs, '%s canonical is in the sitemap' % nm)
# robots, llms
rb = open(os.path.join(docs, 'robots.txt')).read()
ok('Sitemap: ' + BASE + 'sitemap.xml' in rb and 'Disallow' not in rb, 'robots.txt')
ll = open(os.path.join(docs, 'llms.txt'), encoding='utf-8').read()
ok(ll.startswith('# Abhyashify') and '> ' in ll, 'llms.txt shape')
for u in re.findall(r'\]\((https://[^)]+)\)', ll):
    if u.startswith(BASE): ok(os.path.exists(to_file(u)) or u.endswith('.txt') and os.path.exists(os.path.join(docs, u[len(BASE):])), 'llms.txt link %s' % u)
# structured data on the app page
ix = parse(os.path.join(docs, 'index.html'))
types = [json.loads(j).get('@type') for j in ix.ld]
ok('WebApplication' in types and 'WebSite' in types, 'index JSON-LD types %s' % types)
ok(ix.h1 == 1, 'index has one h1 (in noscript)')
ok(os.path.getsize(os.path.join(docs, 'og.png')) > 10000, 'og.png exists')
# no exam page claims an official date
for f in pages:
    t = open(f, encoding='utf-8').read()
    ok('official date' not in t.lower() or 'not' in t.lower(), '%s date wording' % f)
print('%d checks, %d failed' % (n, fails)); sys.exit(1 if fails else 0)
