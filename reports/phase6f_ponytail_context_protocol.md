# Phase 6f: authorized Ponytail context amendment

On 2026-10-29 the user explicitly authorized removing only the API-rejected reasoning item from a checkpoint copy and marking the context change in the results. Two unchanged-context sixth-step invocations had already failed with `invalid_encrypted_content`, before model work. Both failed attempts and their original native history remain preserved.

The working history retains the same native session ID, all five submitted source edits, submission tags, user/assistant messages, tool records, and failed turns. Exactly one `response_item` of type `reasoning`, ID `rs_065c6469f16d8dd2016ae146d391e88191833fbd599d490df6`, is removed. The original live rollout is copied to the new private attempt directory before changing the container copy. SHA-256 checks and a unit test prove that every surviving record retains its original bytes. No other reasoning item may be removed under this authorization.

Attempt `phase6f_ponytail_r02_s06_resume02` uses the same source, runtime, native profile, sixth task and grading procedure. Its record carries `context_deviation` and `strict_history_continuation=false`. Native token counters are differenced against the fifth checkpoint; no previous source task is rerun. This observation may contribute to the requested descriptive mean, but its changed reasoning context must be visible in the run parameters and current graph annotation. It is not evidence of unchanged-context recovery.

A further API rejection stops the attempt. No seventh task or additional independent repetition is authorized by this amendment.
