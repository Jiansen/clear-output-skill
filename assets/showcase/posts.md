# Clear Output — post drafts

Use the three portrait cards together for an introduction, or publish each example with its own caption. Chinese and English are separate versions so an English post can remain entirely in English. All comparisons are editorial illustrations; the project's measured results belong in the linked evaluation reports.

## 中文：项目介绍

配图顺序：[发布流程](release-zh-portrait.png)、[调试说明](debugging-zh-portrait.png)、[重试交互](retry-zh-portrait.png)。

> AI 给出答案后，我们还得看懂它、核对它。
>
> 我们开源了 Clear Output：一个兼容中文和英文的 skill，根据问题选择表达形式。
>
> 发布条件，用依赖图看清；调试说明，分清现象、假设和下一步；重试公式，做成能调参数的解释。原意、条件和不确定性都要保留。
>
> 下面三组图是表达方式示例。代码、安装说明和实际评测都在仓库里：
> https://github.com/Jiansen/clear-output-skill

## English: project introduction

Attach [release](release-en-portrait.png), [debugging](debugging-en-portrait.png), then [retry](retry-en-portrait.png).

> AI can do more of the work. We still need to understand and verify its output.
>
> We built Clear Output, an open-source skill for Chinese and English. It chooses a useful form for the question: a dependency diagram for a release gate, structured evidence for debugging, or working HTML for exploring retry timing.
>
> Meaning, conditions, uncertainty, and the task's language stay intact.
>
> The cards are illustrative examples. Installation instructions, code, and actual evaluations:
> https://github.com/Jiansen/clear-output-skill

## 中文：单独分享每个示例

### 01 · 发布流程

附件：[竖图](release-zh-portrait.png) / [横图](release-zh-landscape.png)

> 什么时候可以部署？
>
> 单元测试和安全扫描并行运行；两项都通过才部署，任何一项失败就停止发布。画成依赖图，就能直接核对这三个条件。
>
> Clear Output 表达示例：同一份信息，换一种便于理解的形式。
> https://github.com/Jiansen/clear-output-skill

替代文本：左侧是发布流程的文字说明。右侧从构建完成分出单元测试和安全扫描两条并行分支；两项通过才汇合到部署，任意一项失败都指向停止发布。

### 02 · 调试说明

附件：[竖图](debugging-zh-portrait.png) / [横图](debugging-zh-landscape.png)

> `ECONNRESET` 是已观察到的错误；“代理关闭了连接”仍是假设；查看代理日志是下一步。
>
> Clear Output 把它们分开，保留错误原文和不确定性。英文调试场景就保持英文。
>
> 这是一组编排后的表达示例：
> https://github.com/Jiansen/clear-output-skill

替代文本：同一段调试说明的两种呈现。右侧分别列出已观察到的请求失败和 ECONNRESET 错误、尚未确认的代理断开连接假设，以及查看代理日志的下一步。

### 03 · 重试交互

附件：[动图](retry-zh.gif) / [竖图](retry-zh-portrait.png)

> 重试公式写出来了，参数一变，结果会怎样？
>
> 基础等待为 1 秒、重试 3 次时，总等待 7 秒；基础等待改为 2 秒，总等待变成 14 秒。都不计执行耗时。
>
> 这是 Clear Output 的交互表达示例。动图来自实际运行的 HTML 页面，仓库里可以下载试用：
> https://github.com/Jiansen/clear-output-skill

替代文本：左侧给出指数退避规则，右侧有基础等待和重试次数两个滑块。动图依次展示总等待 7、14、30、0、7 秒，同时更新每次等待和总尝试次数。不计执行耗时，播放速度不代表重试时长。

## English: individual example posts

### 01 · Release

Attach [portrait](release-en-portrait.png) or [landscape](release-en-landscape.png).

> Two checks run in parallel. Either can stop a release; both must pass to deploy. A dependency diagram makes that gate explicit.
>
> An illustrative example from Clear Output:
> https://github.com/Jiansen/clear-output-skill

Alt text: A prose release rule becomes a dependency diagram. The completed build starts unit tests and a security scan in parallel. Both must pass to deploy. Either failure stops the release.

### 02 · Debugging

Attach [portrait](debugging-en-portrait.png) or [landscape](debugging-en-landscape.png).

> ECONNRESET is observed. A proxy closing the connection is a hypothesis. Checking proxy logs is the next step.
>
> Keep those distinct. Keep English debugging in English.
>
> Clear Output, illustrated:
> https://github.com/Jiansen/clear-output-skill

Alt text: The same debugging information is grouped into observed evidence, an unconfirmed hypothesis, and a next check. The exact ECONNRESET error is preserved; the possible proxy cause remains unconfirmed.

### 03 · Interactive explanation

Attach [GIF](retry-en.gif) or [portrait](retry-en-portrait.png).

> At 3 retries, a 1 s base delay gives 7 s of waiting. Change it to 2 s: 14 s. Execution time excluded.
>
> Clear Output's interactive example, captured from working HTML:
> https://github.com/Jiansen/clear-output-skill

Alt text: A backoff formula becomes a working explorer with base-delay and retry-count sliders. The animation updates total waits through 7, 14, 30, 0, and 7 seconds, alongside each retry's wait and the total attempt count. Execution time is excluded. Playback speed does not represent retry timing.

## Publication notes

- The project has installation instructions for Codex, Claude Code, and Cursor. Live output testing has been done in the Codex environment; do not label these images as live Claude or Cursor results.
- The before paragraphs and after layouts were composed for this showcase. Do not relabel them as “model without skill” versus “model with skill.”
- Avoid adding comprehension-speed, accuracy, or model-win-rate numbers. The existing [evaluation reports](../../evals/README.md) record what was actually tested and its limits.
- The retry GIF is a sequence of real UI states, not an explainer video with narration or a measurement of actual retry duration.
