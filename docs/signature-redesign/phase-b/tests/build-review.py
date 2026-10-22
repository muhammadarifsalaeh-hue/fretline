"""Build an offline Before/After image review; uses relative links, embeds no image bytes."""
from pathlib import Path
from html import escape
import json

OUT = Path(__file__).resolve().parents[1]
BEFORE = OUT.parent / 'audit' / 'before'
AFTER = OUT / 'after'
GROUPS = [('desktop', 'Desktop · 1440 × 1000'), ('tablet', 'Tablet · 768 × 1024'), ('mobile', 'Mobile · 390 × 844')]
ROUTES = [('home', 'Homepage'), ('catalog', 'Catalog'), ('detail', 'Pacifica detail'), ('brands', 'Brands'),
          ('brand-detail', 'Yamaha brand'), ('compare', 'Compare'), ('quiz-welcome', 'Quiz welcome'),
          ('quiz-question', 'Quiz question'), ('quiz-results', 'Quiz results'), ('wishlist', 'Wishlist')]
MISSING = []


def pair(filename, label):
    figures = []
    for stage, path, relative in [('Before', BEFORE / filename, '../audit/before/' + filename),
                                  ('After', AFTER / filename, 'after/' + filename)]:
        if path.is_file():
            content = f'<a href="{escape(relative)}"><img loading="lazy" src="{escape(relative)}" alt="{escape(label)} — {stage}"></a>'
        else:
            content = '<p class="missing">Screenshot has not been generated.</p>'
            MISSING.append({'stage': stage, 'file': filename})
        figures.append(f'<figure><figcaption>{stage}</figcaption>{content}</figure>')
    return '<div class="pair">' + ''.join(figures) + '</div>'


sections = []
for size, title in GROUPS:
    views = []
    for route, label in ROUTES:
        filename = route + '-' + size + '.png'
        views.append(f'<details><summary>{escape(label)}</summary>{pair(filename, label + " " + size)}</details>')
    sections.append(f'<section id="{size}"><h2>{title}</h2>' + ''.join(views) + '</section>')
extras = []
for route, label in ROUTES[:3]:
    extras.append(f'<details><summary>{escape(label)} · full page</summary>{pair(route + "-desktop-full.png", label + " full page")}</details>')
for route in ['catalog-empty', 'wishlist-empty', 'compare-empty']:
    extras.append(f'<details><summary>{escape(route)} · Mobile</summary>{pair(route + "-mobile.png", route)}</details>')
sections.append('<section id="extra"><h2>Full pages and empty states</h2>' + ''.join(extras) + '</section>')
html = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Fretline — Phase B review</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#0a0a0a;color:#f5f5f2}*{box-sizing:border-box}body{margin:0;padding:32px;max-width:1800px;margin-inline:auto}h1{font-size:32px;line-height:1.2;margin:0 0 16px}h2{font-size:24px;margin:40px 0 16px}p{max-width:80ch;line-height:1.65;color:#c2c2bc}nav{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}a{color:#d5b379}nav a{border:1px solid #3e382e;padding:12px;border-radius:8px;text-decoration:none}details{border-top:1px solid #333;margin:0}summary{cursor:pointer;padding:20px 8px;font-size:18px;min-height:48px}summary:focus-visible,a:focus-visible{outline:2px solid #d5b379;outline-offset:4px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start;margin:0 0 24px}figure{margin:0;min-width:0;border:1px solid #333;border-radius:8px;overflow:hidden;background:#141414}figcaption{padding:12px 16px;color:#c9b18a;font-weight:600}img{display:block;width:100%;height:auto}.missing{padding:24px;color:#e8b8a8}footer{margin-top:48px;padding:24px 0;border-top:1px solid #333;color:#aaa}@media(max-width:700px){body{padding:20px}.pair{grid-template-columns:1fr}h1{font-size:26px}}
</style><header><h1>Fretline · Phase B design review</h1><p>Before: unchanged app baseline 82fbe9b. After: Phase B shared components and design system. These are Chromium captures. Tablet and phone sizes are emulation; this report does not establish physical iPad or Safari compatibility.</p><p>The image links open the original PNGs. Expand any route to compare it at the same viewport; full-page views are also available below. Missing images remain explicitly marked.</p><nav><a href="#desktop">Desktop</a><a href="#tablet">Tablet</a><a href="#mobile">Mobile</a><a href="#extra">Full pages / empty states</a></nav></header>'''
html += ''.join(sections)
html += '<footer>Responsive overflow measurements also cover 1024 × 768 and 320 × 740 in after/measurements.json. Interactive outcomes and browser errors belong to acceptance-final.json; screenshots alone are not functional test results.</footer></html>\n'
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'review.html').write_text(html)
(OUT / 'review-manifest.json').write_text(json.dumps({'missingScreenshots': MISSING, 'expectedPairs': 36}, indent=2) + '\n')
print(str(OUT / 'review.html'))
print(f'36 pairs; {len(MISSING)} missing image(s).')
