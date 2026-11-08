# Versions and updates / 版本与更新

Clear Output is distributed as skill files. This package does not install a background updater. Reading changed local skill files and downloading a new release from GitHub are separate operations. A marketplace's plugin-update behavior applies only to a plugin installed through that marketplace; this repository currently ships a standalone skill.

## Find out about a release

- Open [Jiansen/clear-output-skill](https://github.com/Jiansen/clear-output-skill), select **Watch → Custom → Releases**, and apply the setting. Delivery follows the user's GitHub notification preferences. [GitHub notification documentation](https://docs.github.com/en/subscriptions-and-notifications/get-started/configuring-notifications).
- Read [Releases](https://github.com/Jiansen/clear-output-skill/releases) and [CHANGELOG.md](../CHANGELOG.md). Commits to the default branch are not themselves release announcements.
- When asked, read the installed `VERSION` or `metadata.version` in `SKILL.md`. Early copies without a version file are **unversioned**; do not infer a version from a folder name or the current remote repository.

```bash
python3 scripts/clear_output.py --version
python3 scripts/check_update.py
```

The first command is local. The second explicitly requests public metadata from this repository's GitHub latest-release endpoint; it sends no document or conversation content and changes no files. Do not run it during ordinary writing tasks. An offline, rate-limited, or failed request reports `unavailable`; it does not mean the installed version is current. `same_version` compares version labels, not file integrity or local modifications. A local version ahead of the release is reported separately and is never downgraded by the script.

## Apply an update

Use the actual installed path; do not create a second copy in another skill directory. Check the current files and installation method first. Preserve local customizations, and keep backups outside directories that the host scans for skills.

| Installation | Update |
| --- | --- |
| Git clone tracking a branch | Review local changes, then `git -C "/actual/skill/path" pull --ff-only`. This follows that branch and can include changes newer than the latest release. |
| Git clone pinned to a tag | Fetch tags, inspect the chosen release, then check out its tag after preserving local edits. A detached tag does not update with `git pull`. |
| Installer download or copied directory without Git | Download `clear-output.zip` from the chosen release; inspect/compare it in a temporary directory, then replace the old skill directory after preserving customizations. Copy the whole package, including `references/`, `scripts/`, `VERSION`, and metadata. |
| Claude uploaded skill | Download the release ZIP and update/re-upload the skill through Claude's skill-management UI. Updating a local folder does not update an uploaded copy. |
| Project-committed skill | Update the committed files and let teammates obtain them through the project's normal Git workflow. |

Release assets include `SHA256SUMS` and a minimal `clear-output.zip`; each ZIP contains one top-level `clear-output/` directory. Compare its SHA-256 digest with the published checksum if verifying a download. A checksum detects differing bytes; it is not an independent signature.

After updating, re-read `VERSION`, verify required files, and start a fresh session if the host still uses the old copy. [Codex detects changed local skills](https://developers.openai.com/codex/skills/); that reload does not fetch remote files. [Cursor discovers local skill directories](https://cursor.com/docs/skills). [Claude plugin auto-updates](https://code.claude.com/docs/en/discover-plugins#keep-plugins-updated) concern marketplace plugins, not the local-folder installation above.

## 中文速览

1. 在 GitHub 仓库选择 **Watch → Custom → Releases**，订阅正式发布通知。通知的展示和邮件投递取决于个人设置。
2. 查看安装目录的 `VERSION`。需要时运行 `python3 scripts/check_update.py`，对比本地与最新正式版；此命令只检查，不升级。
3. Git 克隆版可在处理本地修改后 `pull --ff-only`；固定 tag 的安装需明确切换 tag。下载／复制版用 release ZIP 更新整个技能目录，保留自己的修改。Claude 上传版需要在 Claude 界面更新。
4. 更新后核对版本；必要时新开会话。请勿把备份放在宿主扫描的 skills 目录内，以免重复加载。

检查器不依赖联网。只有用户要求查询更新时才请求 GitHub，不会每次回复弹出升级提示或自动修改安装。
