# Changelog

Versioned releases package the same skill for Codex, Claude, and Cursor. Earlier repository snapshots had no release version. This is the first tagged release; no earlier tagged release is implied.

## [0.1.0] - 2026-11-08

Clear Output adds optional local checks while preserving its Chinese, English, mixed-language, and visual explanation workflows.

- Check explicit literals and JSON contracts; inspect source/output differences in numbers, selected units, and meaning-bearing markers.
- Count English words and Chinese Han characters separately, protect common code/quote/link spans, and support optional project glossaries and length advice.
- Keep checks advisory where context matters. No automatic rewriting, quality score, model API, or required Python runtime for the instruction-only workflow.
- Add an installed version, read-only update checker, bilingual upgrade guidance, and a minimal skill ZIP with SHA-256 checksum.
- Publish tagged releases after automated checks. Subscribe through **Watch → Custom → Releases** on GitHub.

中文：新增可选的本地双语检查器，检查原文保留、JSON 格式、数值及语气标记变化；提供项目术语表接口。中文与英文分别统计，常见代码和引用受到保护。新增版本号、更新检查命令、升级说明和可直接上传的技能 ZIP。

**Upgrade / 升级：** Follow [the update guide](https://github.com/Jiansen/clear-output-skill/blob/main/references/updates.md). Existing Git clones can update their branch; downloaded/copied installations should replace the complete skill package after preserving local customizations. Python 3.10+ is only needed for optional scripts. Existing language and output-format preferences remain in force.

**Validation scope / 验证范围：** Deterministic checks and regression tests cover mechanical behavior. They do not establish semantic equivalence, improved human comprehension, or live Claude/Cursor compatibility. Source-comparison heuristics can miss changes or flag valid paraphrases; review their evidence in context.
