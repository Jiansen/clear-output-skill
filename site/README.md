# Public demo

The [live demo](https://jiansen.github.io/clear-output-skill/) uses the exact example source in `assets/readme/examples.html`, with a bilingual introduction, installation command, and copyable sample prompt. It calls no model and includes no analytics script. The example calculator works in the browser. The authored examples are not measured model A/B results.

Build with `python3 tools/build_site.py`; serve `dist/site/` with a local HTTP server. The repository's Pages workflow publishes this directory on relevant pushes to `main`. No skill runtime files change when the site changes.

`intro.html`, `install.html`, `style.css`, and `interface.js` provide the surrounding interface. `social-card.html` is the source for the 1200 × 630 PNG used in link previews; render it with Chrome at that viewport after edits. The demo's canonical URL and sitemap use this repository's GitHub Pages address.

Before publishing, check both languages at desktop and phone widths, all six visible examples, retry endpoints, the agent-specific prompt prefixes, clipboard success/fallback, and anchor links. The original example renderer separately checks all 72 retry parameter combinations.
