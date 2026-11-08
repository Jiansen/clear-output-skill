# Publishing a skill update

1. Update `VERSION`, `SKILL.md`'s `metadata.version`, and the matching `CHANGELOG.md` section. Use stable `major.minor.patch` versions and a `v`-prefixed tag. Describe behavior changes, upgrade steps, and actual validation limits in the notes.
2. Run `python3 -m unittest discover -s tests -v`. Build with `python3 tools/build_release.py --output-dir dist --tag vX.Y.Z`; inspect the ZIP and notes. The builder checks version consistency and excludes evaluation data, media, dependencies, and local caches.
3. Commit and push the reviewed change. Check the branch workflow before tagging the exact tested commit. Do not move an existing published tag; use a new version for a correction.
4. Push `vX.Y.Z`. The release workflow runs the tests on Linux and Windows with Python 3.10 and 3.14. Only after all checks succeed does it publish the GitHub Release, `clear-output.zip`, and `SHA256SUMS`.
5. Inspect the published assets and run `python3 scripts/check_update.py`. Confirm that release notes and installation instructions describe the shipped package.

GitHub handles notifications for users who subscribe to Releases. A commit or tag alone is not a release notification. The skill does not contact users, poll from normal writing tasks, or install background update hooks. Users choose when to update their local or uploaded copy.

The release ZIP contains `SKILL.md`, `VERSION`, `CHANGELOG.md`, `LICENSE`, `references/`, `scripts/`, and `agents/`. Do not attach the full development checkout as the skill-upload asset. The source-code archives GitHub adds automatically are separate from this minimal skill package.
