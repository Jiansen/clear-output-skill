# Changelog

Versioned releases package the same skill for Codex, Claude, and Cursor. Repository snapshots before 0.1.0 had no release version.

## [0.1.1] - 2026-11-08

- Show six examples directly in both READMEs, including everyday decisions, meeting notes, and reading a survey alongside the original release, debugging, and retry examples.
- Use compact paired cards that wrap on narrow screens. Keep the existing technical examples' source wording, titles, and key labels. Fold host-specific installation details without removing their content.
- Broaden the skill's discovery description beyond technical content and add corresponding output-form guidance. The checker's behavior and dependencies are unchanged.
- Preserve the distinction between editorial examples and measured model results. The new nontechnical scenarios are fictional.

中文：中英文 README 直接展示六个示例，新增日常选择、会议行动项和调查解读。采用紧凑双栏卡片，窄屏自动换行；原有技术示例保留原文与关键说明。安装细节按宿主收起，技能描述同步覆盖非技术场景。

**Validation / 验证：** Check original-example content preservation, image layout, bilingual controls, all 72 retry parameter states, rendered README layouts, and the existing Python regression suite. These checks do not measure human comprehension or prove model-quality gains.

**Upgrade / 升级：** [Update the complete skill package](https://github.com/Jiansen/clear-output-skill/blob/main/references/updates.md) to receive the broader discovery description and examples. Python remains optional; no checker configuration changes are required.

## [0.1.0] - 2026-11-08

The first tagged release adds optional local checks while preserving Clear Output's Chinese, English, mixed-language, and visual explanation workflows.

- Check explicit literals and JSON contracts; inspect source/output differences in numbers, selected units, and meaning-bearing markers.
- Count English words and Chinese Han characters separately, protect common code/quote/link spans, and support optional project glossaries and length advice.
- Keep checks advisory where context matters. No automatic rewriting, quality score, model API, or required Python runtime for the instruction-only workflow.
- Add an installed version, read-only update checker, bilingual upgrade guidance, and a minimal skill ZIP with SHA-256 checksum.
- Publish tagged releases after automated checks. Subscribe through **Watch → Custom → Releases** on GitHub.

中文：新增可选的本地双语检查器，检查原文保留、JSON 格式、数值及语气标记变化；提供项目术语表接口。中文与英文分别统计，常见代码和引用受到保护。新增版本号、更新检查命令、升级说明和可直接上传的技能 ZIP。

**Upgrade / 升级：** Follow [the update guide](https://github.com/Jiansen/clear-output-skill/blob/main/references/updates.md). Existing Git clones can update their branch; downloaded/copied installations should replace the complete skill package after preserving local customizations. Python 3.10+ is only needed for optional scripts. Existing language and output-format preferences remain in force.

**Validation scope / 验证范围：** Deterministic checks and regression tests cover mechanical behavior. They do not establish semantic equivalence, improved human comprehension, or live Claude/Cursor compatibility. Source-comparison heuristics can miss changes or flag valid paraphrases; review their evidence in context.
