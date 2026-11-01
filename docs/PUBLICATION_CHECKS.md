# Public release checks

Prepared **2026-11-01**. This records checks performed for the open-source release; it is not a guarantee that every possible secret detector or legal issue has been exhausted.

## Publication status

**GitHub publication is blocked by authenticated repository creation.** The intended destination is `https://github.com/DemidovArtem/ai-coding-benchmarks`, which is not yet a verified live public repository. The available browser and GitHub CLI are signed out. SSH authenticates as `DemidovArtem`, but SSH cannot create a GitHub repository. The user currently cannot complete browser sign-in. A read-only GitHub API lookup found no existing public repository for this project; SSH lookup of the intended path returned “Repository not found”. No new duplicate repository was created.

The existing GitLab origin is retained. The application answers are prepared locally in ignored `OPENAI_FUND_APPLICATION.md`; no application was submitted.

To complete publication later, create an **empty public** repository at the intended GitHub path (no generated README/license/initial commit), then push the reviewed release commit as its `main` branch. Verify unauthenticated public access, commit ancestry, and the README figure. Remove the pending-publication notice from README and the application only after those checks. Do not push a mirror of private refs or ignored artifacts.

## History preservation

The starting release-preparation HEAD is `18539d6f2201317ec2568334d76a862e93fd9130`. All **103 existing commits** are ancestors of that HEAD; no other reachable commit was outside its ancestry. Preparation adds commits on top without rebasing, filtering, squashing, or replacing existing objects. Author names, emails, dates, and original commit IDs remain unchanged. This includes the maintainer's two historical author email addresses; preserving history also preserves that identity metadata.

No claim is made yet about a successful GitHub transfer: it has not happened. GitLab remains the existing backup remote. A subsequent GitHub push can preserve all 103 original commits without a history rewrite.

## Secret and privacy review

- Official **Gitleaks 8.30.1**, SHA-256-verified release binary, scanned `git --log-opts=--all` with full redaction. Scope: all 103 original commits, approximately 19.58 MB of changes.
- All 17 findings were individually checked against their historical source lines: **14 recorded file SHA-256 values**, **2 Sonar quality-profile UUIDs**, and **1 literal redaction-test fixture**. None was a credential. No broad rule suppression was applied.
- A separate exact-match scan checked all **1,918 reachable Git objects**, including commit metadata/messages and blobs, against current locally retained OAuth and Sonar credential values. **No matches.** Current tracked working files were also checked. This detects known current values; it cannot prove that every unknown or previously revoked credential is absent.
- History path review found no tracked `results/`, `vendor/`, `.env*`, `.codex/`, or `.serena/` trees. `.gitignore` excludes raw trials, local auth files, and environment files. The application file is also ignored.
- Public normalized reports intentionally retain source hashes, experiment session IDs, image identities, local usernames/paths, and Git provenance. Session IDs are not authentication tokens. Raw authenticated histories, closed database backups, account settings, and credentials are not published.
- The unrelated local `unit8-test.py` is not part of this release and is not staged.

The release working tree was scanned separately: the same 17 classified false positives, zero unresolved findings, and zero known-credential matches. Machine-readable validation is in [`reports/publication_validation.json`](../reports/publication_validation.json). Raw scanner logs stay outside the repository under `/tmp/ai-coding-release-audit/`; their findings are redacted.

## Licensing and attribution

The root MIT license covers original project code/documentation by Artem Demidov. Existing author records identify the maintainer; no third-party authorship of original project files was found in Git metadata. This is a provenance check, not a legal adjudication. Vendored profile assets and upstream source context keep their original licenses.

[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) includes full SWE-Milestone and ripgrep MIT notices, references the retained Ponytail MIT notice, and carries the applicable pinned Caveman NOTICE. Caveman v4.0.1 assets are Apache-2.0; the historical MIT text does not relicense all assets. Frozen asset bytes are not changed. External tools/images are not redistributed by this Git repository; any later binary/runtime distribution needs its own dependency notices.

The README explicitly credits Codex as the harness development tool under the maintainer's direction. New Codex-assisted commits use:

```text
Co-authored-by: Codex <codex@openai.com>
```

[GitHub documents the trailer format](https://docs.github.com/en/pull-requests/how-tos/commit-changes/creating-a-commit-with-multiple-authors). The address above appears in an [OpenAI-maintained repository commit that GitHub attributes to Codex](https://github.com/openai/swarm/commit/6af0b4c). This credits work on the new commit, not a human team member or rewritten historical work. Future agent commits follow the repository's AGENTS.md; no global Codex settings or commit hooks were installed.

## Reproducibility validation

A new local clone under `/tmp/ai-coding-release-audit/clean-clone` was overlaid with the intended release files. It contains no private `results/`, retained runtime, model history, dataset, application file, or user scratch file. A separate virtual environment used **CPython 3.12.3**, the documented setup requirements, **Matplotlib 3.10.5**, and **NumPy 2.2.6**.

1. Public rendering succeeded from tracked JSON alone: **24 method/step means**, all four methods, six steps. The PNG was visually inspected, including ranges, units, and the context-amendment footer.
2. Running all tests without the upstream source revealed six missing-import errors. Documentation was corrected rather than claiming a dependency-free test pass.
3. The documented public SWE-Milestone clone, pinned checkout, and OAuth/profile patch commands succeeded in that clean clone. No dataset or Docker image was acquired for these tests.
4. With that source dependency and temporary loopback sockets, the full suite passed: **127 tests, OK**. The tests did not run models, graders, or Sonar services.
5. No experiment scores or frozen implementation files were changed by this documentation work. The source-only patch corpus and original current-comparison JSON remain intact.

These checks validate public analysis and harness logic. **A full fresh-machine model run and native-session restoration were not performed.** Current runtime recipes depend on staged local closures and exact versions; portability work remains. No API billing estimate, statistical significance, or deterministic model behavior is claimed.

## Application source

The [official Codex Open Source Fund form](https://openai.com/form/codex-open-source-fund/) was checked on 2026-11-01. Its project fields match the prepared local answer file; its additional-information field is under the personal details section. The page describes grants of up to $25,000 in API credits. No amount, funding award, sponsorship, or application acceptance is claimed.
