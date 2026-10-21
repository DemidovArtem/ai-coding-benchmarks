# Serena continuous workflow

This isolated trajectory uses Serena for real semantic navigation and persistent project memory.

At every turn, the first shell command must read the host-supplied task file exactly as requested. This task-delivery read is the only exception to the startup shell restriction below. It contains the current SRS and whether this is a cold or warm memory turn.

After that read, before any other shell command, source read, or source edit:

1. Call Serena `initial_instructions`.
2. On the first turn only, call `onboarding` and follow its repository-orientation instructions using Serena tools. On later turns, do not repeat onboarding: list memories and call `read_memory` for a note retained from an earlier turn.
3. Obtain real symbols relevant to the current task using `get_symbols_overview` or `find_symbol`.
4. Use `write_memory` to record the orientation or current task context before shell/source work. After implementation, update memories with factual changes and useful context for the next task.

Until the startup memory note is written, use Serena `list_dir`, `find_file`, and `read_file` for discovery, including non-code files. Do not run `rg`, `cat`, or `ls` through shell except for the initial task-delivery read. This restriction takes precedence over general shell suggestions in onboarding instructions.

Retain `.serena/memories` across all five tasks in this trajectory. Never delete, reset, import or commit the memory directory. It is ignored by Git and excluded from grader snapshots. The next independent repetition starts cold and must not reuse this trajectory's memories. Do not place credentials or grader outputs in memory. Grader feedback is unavailable by design.

After orientation, use shell for builds/tests and Serena for semantic navigation and edits where appropriate. If MCP or semantic tools fail, stop and report the error instead of silently acting as a shell-only baseline. Implement only the supplied task, commit and tag it, then stop until the next task arrives.
