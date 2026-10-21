#!/usr/bin/env python3
"""Render docs/og.png (the 1200x630 share image) from app/og.html. Needs Playwright with Chromium; not part of build.py."""
import os
from playwright.sync_api import sync_playwright
here = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1200, 'height': 630})
    pg.goto('file://' + os.path.join(here, 'og.html'))
    pg.evaluate('document.fonts.ready')
    pg.wait_for_timeout(400)
    pg.screenshot(path=os.path.join(here, '..', 'docs', 'og.png'))
    b.close()
print('wrote docs/og.png')
