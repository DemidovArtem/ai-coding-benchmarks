# Phase 3 progress

Status: **baseline, Ponytail and Caveman complete; Serena running**. Baseline grader resolved=true, production +78/−24, collection errors absent. Its Sonar scan is bound to the graded snapshot and verifies all 79 Rust files.

All three skill activation smokes now passed on the exact common image. Serena's two integration problems were fixed: explicit offline Rust paths, then `required=true` to avoid the default one-second optional-MCP catalog grace. Codex successfully called `initial_instructions` and `get_symbols_overview`; failures and setup usage remain separately retained. The model was not forced to use Serena in measured prompts.

[Protocol](phase3_protocol.md) and [frozen configuration](phase3_experiment.json) are committed before measured runs. Setup fingerprint: `50313521937dfb0f67c1771bfe3b28f55415dbd082893e97f5a71237dd94278f`. Common image: `sha256:3407cf8372c295e58722ff3ce33a0797e59e768cdaec496e20a15ef876505269`.

Current order: baseline, Ponytail, Caveman, Serena. Each uses fresh protected state and the same original task/starting tree. Phase 2 remains a separate cohort. Before every model invocation, the runner re-reads limits and stops at 85% in either window. Startup smokes are setup overhead, not task results.

Next: finish baseline and verify its immutable snapshot, then run the three skills sequentially and collect Git/usage/Sonar. [Machine-readable progress](phase3_progress.json). Continuous remains explicitly deferred; Phase 6 is not running.

Ponytail: grader resolved=true, production +70/−22, native-hook activation verified in its measured trial; snapshot collection and Sonar succeeded. Its production churn is 92 versus baseline 102 (−10 lines on this single task). No general skill-quality conclusion follows from one repetition.

Caveman: grader resolved=true, production +77/−21, churn 98 versus baseline 102 (−4). Native-hook activation, source snapshot and Sonar binding verified; collection errors absent.
