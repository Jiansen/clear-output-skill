#!/usr/bin/env python3
"""Build the public demo from the same source as the README cards."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://jiansen.github.io/clear-output-skill/'


def build(output):
    source = (ROOT / 'assets/readme/examples.html').read_text(encoding='utf-8')
    source = source.replace('<title>Clear Output — everyday and technical examples</title>',
        '<title>Clear Output — clearer AI answers in English and Chinese</title>\n'
        '<meta name="description" content="An open-source agent skill for clear explanations, comparisons, plans, and summaries. Explore six bilingual examples and a working interactive explanation.">\n'
        f'<link rel="canonical" href="{URL}">\n'
        '<meta property="og:type" content="website">\n'
        '<meta property="og:title" content="Clear Output — make AI answers easier to understand and check">\n'
        '<meta property="og:description" content="One skill for English and Chinese. Faithful writing, useful diagrams, and working interaction. Explore examples and install for Codex, Claude Code, or Cursor.">\n'
        f'<meta property="og:url" content="{URL}">\n'
        f'<meta property="og:image" content="{URL}social-card.png">\n'
        '<meta property="og:image:width" content="1200">\n'
        '<meta property="og:image:height" content="630">\n'
        '<meta property="og:image:alt" content="Clear Output: make AI answers easier to understand and check. Words, diagrams, interaction. English and Chinese.">\n'
        '<meta name="twitter:card" content="summary_large_image">')
    source = source.replace('</style>', (ROOT / 'site/style.css').read_text() + '\n</style>', 1)
    source = source.replace('<header class="toolbar">', (ROOT / 'site/intro.html').read_text() + '\n<header class="toolbar">', 1)
    source = source.replace('<h1 id="page-title">', '<h2 id="page-title">').replace('in code</h1>', 'in code</h2>')
    source = source.replace('<footer class="footer"', (ROOT / 'site/install.html').read_text() + '\n<footer class="footer"', 1)
    source = source.replace('</body>', '<script>\n' + (ROOT / 'site/interface.js').read_text() + '\n</script>\n</body>')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(source, encoding='utf-8')
    (output / '.nojekyll').write_text('')
    (output / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + URL + 'sitemap.xml\n')
    (output / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>' + URL + '</loc></url></urlset>\n')
    shutil.copyfile(ROOT / 'site/social-card.png', output / 'social-card.png')
    print('Built demo:', output / 'index.html')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist/site')
    build(parser.parse_args().output_dir)
