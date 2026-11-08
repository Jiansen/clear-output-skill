# Choosing and checking an output form

Choose for the reader's question. The availability of a renderer does not by itself justify using it. Conversely, a useful one-off diagram or interactive explanation need not become a reusable application.

## What each form must make easier

- **Table:** align shared criteria so the reader can compare rows directly. Mark unknown entries as unknown. Do not invent a winner without a stated priority.
- **Diagram:** expose structure that prose makes the reader reconstruct. A flowchart shows decisions; a sequence diagram shows participants and message order; a dependency graph shows prerequisites. Do not use an arrow without knowing whether it means order, dependency, data transfer, or causation.
- **Annotated image or schematic:** make a location, shape, or component easier to identify. Keep measured evidence distinct from an illustrative reconstruction. Use an existing image only within the task's scope.
- **Chart:** expose a numerical pattern using supplied or legitimately obtained data. Preserve units, bounds, time spacing, and missing observations. Label series directly or provide a legend. Never draw invented values just to make a smooth trend.
- **Interactive explanation:** let the reader test a question by changing a meaningful input. Label assumptions and units; show a useful default state and visible changes in the result. A button that only opens another paragraph is not automatically better than prose.
- **Animation or explainer video:** use time to show a mechanism, movement, or gradual construction of an idea. Include understandable labels or captions; narration is optional. A script or storyboard is useful preparation but is not a finished video. A still diagram may answer the question better when motion adds nothing.

## Examples of the decision

**A cache with hit/miss branches.** Draw the branches and label the hit/miss conditions. Do not add a connection from cache to database unless the supplied architecture has it. A sentence beside the diagram can state the main difference between the two paths.

**Two independent checks before deployment.** Draw a split and a join or otherwise make concurrency explicit. A chain of arrows would incorrectly imply sequential execution.

**A parameter changes retry timing.** A slider and a timeline can show how the wait grows. State whether the count means retries or total attempts, preserve the formula, and distinguish waiting time from execution time. Show meaningful endpoints such as zero retries. Do not make a real network request to illustrate timing.

**A process that develops over time.** Use controllable steps or a short animation if the transitions are the idea being taught. A video should earn its duration through explanation, not decorative motion. Respect reduced-motion preferences in interactive artifacts when possible.

**A known abbreviation or a one-line fix.** Give the short answer. A diagram adds reading and navigation without exposing useful structure.

## Deliver and verify

Use a format that works in the current delivery surface. For a small technical relationship, a supported inline diagram can be enough. Use standalone HTML when interaction helps and the user can open it. Use available image, plotting, or video tools for the corresponding artifact; no specific plugin is required by this skill.

Before claiming the artifact is ready:

1. Check the content against the source: nodes, edges, branches, sequence/concurrency, numerical values, units, uncertainty, and technical literals.
2. Render or open it when the environment permits. Check for syntax errors, clipped or overlapping labels, unreadable scales, and reliance on color alone.
3. For an interactive artifact, change the controls and check the visible outcome against a calculation or stated rule. Check boundary states relevant to the explanation and basic keyboard use.
4. For animation or video, inspect representative frames or play the result. Check ordering, duration, captions, and audio synchronization if audio is present.
5. Report what was actually checked. If only source was generated, call it source. If execution is unavailable, say so and provide the best usable fallback rather than claiming a rendered or tested result.

Keep these checks proportional to the artifact. The goal is an accurate explanation the reader can use, not a mandatory production pipeline for every sketch.
