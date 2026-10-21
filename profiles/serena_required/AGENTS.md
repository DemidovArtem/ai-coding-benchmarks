# Required Serena workflow

This profile evaluates a Serena-first coding workflow. Use the configured Serena MCP server for code navigation; installing it alone is insufficient.

Before shell commands, source reads or source edits:

1. Call Serena `initial_instructions`.
2. This independent trial starts cold. Call Serena `onboarding`, then carry out its applicable repository-orientation instructions using only this checkout. Do not import prior trial knowledge.
3. Use `get_symbols_overview` or `find_symbol` on relevant source to obtain real symbols. Prefer symbolic reads and reference queries to full-file source dumps.
4. Write a short factual repository-orientation note with Serena `write_memory`. Keep memories inside this trial; never include credentials or grader feedback.

Until that first orientation memory is written, do not use shell tools, including `rg`, `cat`, `ls`, or shell-based reads of non-code files. If onboarding asks for repository discovery, use Serena `list_dir`, `find_file`, `read_file`, and semantic tools instead. This startup restriction takes precedence over general suggestions to use shell tools in the onboarding instructions.

Shell tools remain appropriate for builds/tests and non-code files after the required startup steps. Prefer Serena for subsequent source navigation and references. Source edits must not precede successful semantic navigation.

If Serena is unavailable or its semantic tools fail, report the error and stop source work. Do not silently continue as an ordinary shell-only baseline. The runner checks actual successful MCP events; merely saying that Serena was used does not satisfy this profile.
