"""Capture the preserved 3c1d70e build before the authorized visual update."""
from pathlib import Path
from hashlib import sha256
from urllib.request import urlopen
from playwright.sync_api import sync_playwright
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'before'
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://127.0.0.1:5451'
sizes = {'desktop': (1440, 1000), 'landscape': (1194, 834), 'portrait': (768, 1024), 'mobile': (390, 844), 'narrow': (320, 740), 'portrait-edge': (1024, 1366)}
report = {'base': BASE, 'commit': '3c1d70ec5bb2b7f2568ba2b061388a1a251ac540', 'servedHTMLSHA256': sha256(urlopen(BASE).read()).hexdigest(), 'captures': []}
assert report['servedHTMLSHA256'] == 'c462802a6f4b51b37cd043b678c44a501943649cf47d5ebdcd841ceb49f7b3d8'
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox', '--enable-unsafe-swiftshader'])
    for name, (w, h) in sizes.items():
        context = browser.new_context(viewport={'width': w, 'height': h}, has_touch=w < 1024, reduced_motion='reduce')
        page = context.new_page()
        page.goto(BASE, wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        for selector in ['#categories', '#home-features', '#featured']:
            page.locator(selector).scroll_into_view_if_needed()
            for im in page.locator(selector + ' img').all():
                im.evaluate('(i)=>i.decode().catch(()=>{})')
        page.evaluate('scrollTo(0,0)')
        files = []
        for suffix, selector in [('categories', '#categories'), ('features', '#home-features')]:
            file = f'chromium-{name}-{suffix}.png'
            page.locator(selector).screenshot(path=str(OUT / file), animations='disabled')
            files.append(file)
        file = f'chromium-{name}-home.png'
        page.screenshot(path=str(OUT / file), full_page=True, animations='disabled')
        files.append(file)
        report['captures'].append({'viewport': name, 'size': [w, h], 'files': files})
        context.close()
    browser.close()
(OUT / 'capture-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('BASELINE COMPLETE', len(report['captures']), 'viewports')
