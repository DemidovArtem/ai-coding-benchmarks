# Phase 6f: Ponytail repetition 2 exact-context retry

The first sixth-step invocation failed before model work with API `invalid_encrypted_content`: reasoning hydration could not decrypt or parse an item already present in the fifth checkpoint. The fifth checkpoint SHA-256 matches the frozen selection. Source remains clean at the fifth submission. Available quota does not explain this failure. The underlying service-side cause is unconfirmed.

One retry is permitted in the same retained container and native session, with the same runtime, profile, task, previous submission tags, messages and encrypted reasoning. No history item is removed, replaced or compacted. The failed invocation remains in the register. A repeated rejection stops this trajectory; it does not authorize a context reset or another experiment.

The adapter reuses the audited sixth-step recovery pattern. Its digest and retained source/history checks are recorded in `phase6f_ponytail_resume_preflight.json`. Successful recovery must pass the original dispatch, native skill activation, ancestry, grading, Sonar and durable checkpoint checks. Usage is measured against the fifth checkpoint, and failed attempts do not become additional repetitions.

OpenAI's [conversation state guide](https://developers.openai.com/api/docs/guides/conversation-state#manually-manage-conversation-state) requires preserving complete response output, including encrypted reasoning, when replaying stateless reasoning history. It does not document the cause of this specific error. No assumption about account identity or corruption is treated as a finding.
