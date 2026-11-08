# Cases where shorter wording can change meaning

These examples are invented. They illustrate reasoning, not mandatory output templates.

## Missing precision

Source: `内存占用过高时，请尽快处理。否则可能影响请求。`

Faithful rewrite: `内存占用过高时，请尽快处理。否则，请求可能受到影响。`

If operational instructions are needed, identify the missing threshold, action, and response time. Do not invent `90%`, a restart, or a deadline.

## Recommendation and approximation

Source: `建议先备份。等待约 5 秒后，可以重试。`

Keep the backup a recommendation, the delay approximate, and the retry optional. A numbered list does not authorize changing all three into commands.

English source: `The worker may retry up to 3 times unless the operator cancels the job.`

Keep possible retry, the upper bound, and the cancellation exception together. `The worker retries 3 times` changes all three.

## Actor and capability

Source: `选择“保存”后，系统写入配置并重新加载服务。`

The reader selects the control. The system performs the other actions. Do not give the reader three manual steps.

`Operators are allowed to cancel a job` describes permission. `The worker supports CSV input` describes capability. A single replacement for every use of `can` loses this distinction.

## Language belongs to the task

- A Chinese request to revise an English README: preserve English in the README, use Chinese for the requested explanation of edits.
- A Chinese question with an English traceback: explain in Chinese and preserve any quoted traceback.
- An English debugging question after a Chinese discussion: follow the user's switch to English.
- Chinese UI copy requested inside an English conversation: write the UI copy in Chinese; keep accompanying reasoning in English unless asked otherwise.
- A JSON-only request: return only the requested JSON. Do not add an introduction, translation, or compliance summary.

## Uncertainty and evidence

`No error appears in the logs` does not prove `the operation succeeded`.
`Code changed` does not prove `the fix works`.
`The job has finished` may assert a current state that `the job finished` does not capture as clearly.

Report the actual evidence and its scope. A possible cause stays possible until evidence establishes it.

## Technical terms and simultaneous actions

Keep `闭环控制`, `访问控制`, and domain-specific terminology when they name real concepts. Clarify them when useful; do not replace them because a substring also appears in a jargon list.

Source: `按住按钮，同时转动旋钮。`

Keep the actions simultaneous. Splitting this into successive steps changes the operation.
