# Research brief: configuration matters, but effects need replication

**Artem Demidov · independent research · 5 November 2026**

Project: [AI Coding Agent Configuration Benchmarks](https://github.com/DemidovArtem/ai-coding-benchmarks).

## Question and contribution

How do coding-agent skills, semantic tools, and workflow settings affect correctness, code growth, static maintainability, and token use over successive changes? Current experiments keep the model fixed. They measure configuration effects, not superiority between models.

The contribution is an implemented, inspectable research pipeline: isolated agent profiles, real SWE-Milestone tasks and graders, retained source/session checkpoints, measured tool use, immutable patches, and snapshot-bound SonarQube analysis. Public analysis can be redrawn from tracked JSON without authentication, Docker, or new model calls. Private authenticated state is excluded.

## Evidence available now

- The initial isolated pilot contains seven measured trials in two separate matched cohorts. All meet the original grader's acceptance requirements; each condition has only one observation.
- The later ripgrep experiment has seven six-step trajectories: two each for baseline, Caveman, and Ponytail, one for Serena. Its 42 step observations are dependent within trajectories, not 42 independent replications.
- After six changes, Ponytail's mean production churn is 449 lines versus 578.5 for baseline (22.4% lower). Mean cumulative output is 62,766 versus 67,311.5 tokens (6.8% lower). These are descriptive observations from this small sample.
- Caveman has higher mean cumulative output here, 85,989.5 tokens, without a clear quality advantage. Shorter communication instructions do not establish lower total agent usage.
- Serena's sixth step records 71 successful MCP calls, including 24 semantic calls, and verified memory continuity from 12 to 13 files. Functioning tools are established; an effectiveness advantage is not.
- All seven sixth-step evaluations are valid but unresolved, with 7/8 new tests passing. Fifth-step correctness scores are invalid because of a documented grader dependency issue.

Source: [results and ranges](RESULTS.md), [methodology](METHODOLOGY.md), [public attempt CSV](data/trials.csv), and [source patches](../reports/patches/manifest.json).

## What these results do not establish

There is no statistically significant winner, no demonstrated universal token saving, and no direct measurement of human review time. Sonar includes inline tests and benchmark masking. Runtime differences, fixed ordering, small sample sizes, and recovery attempts limit interpretation. One Ponytail continuation has an explicitly disclosed reasoning-context amendment. Model execution is not assumed deterministic.

The next study is a separate scikit-learn cohort: six dependent or dependency-closed changes, four configurations, and two independent repetitions each. Each step runs across all methods before the next step starts. Source, session and Serena memories persist within a trajectory; every new repetition starts cold. Environment and storage preflight are unfinished; no new-repository results exist yet. [Plan](SECOND_REPOSITORY.md).

## Funding relevance

The project provides a concrete pilot and reusable evidence collection rather than an untested proposal. Funding could support independent replications, additional repositories, portable execution, predefined statistical analysis, and a separately designed API-funded cohort with actual billing measurements. Existing experiments use ChatGPT OAuth and report tokens, not dollar savings. No grant award, endorsement, funding commitment, or completed grant submission is claimed.

## Suggested LinkedIn text

> I've open-sourced a research prototype studying how coding-agent configuration affects software engineering over successive changes.
>
> In an exploratory ripgrep experiment, Ponytail produced 22.4% less production-code churn and used 6.8% fewer output tokens on average than baseline after six changes. There were only two trajectories per method, and the quality metrics did not establish a winner. All seventh-step work remains unmeasured; all seven sixth-step graders were valid but unresolved.
>
> The repository includes English methodology, graphs, normalized trial records, source patches, and analysis that can be redrawn without model calls. It also documents grading issues and recovery exceptions, including one amended reasoning context. The harness was built with OpenAI Codex under my direction.
>
> Next: test whether the observations survive a second repository and independent repetitions. Feedback on the study design and replication is welcome.
>
> https://github.com/DemidovArtem/ai-coding-benchmarks

This is a draft for the maintainer to review and post; no message has been published to LinkedIn.
