# Implementation LOC breakdown

Counted on 20 October 2026 from tracked files at implementation commit `221aeca`. These are physical lines, including comments and blank lines; nonblank counts are also shown. Benchmark repositories, ignored runtime artifacts, generated reports and vendored skill assets are excluded from first-party Python totals.

| First-party component | Files | Physical LOC | Nonblank lines |
| --- | ---: | ---: | ---: |
| Runners and continuous execution | 4 | 1,060 | 963 |
| Profiles, skills and planning | 7 | 827 | 748 |
| Grading, metrics and reporting | 4 | 570 | 513 |
| Sonar integration | 4 | 554 | 497 |
| Audit, quota and security | 3 | 250 | 219 |
| Native-hook adapters | 2 | 100 | 85 |
| Package initializer | 1 | 1 | 1 |
| **Implementation Python** | **25** | **3,362** | **3,026** |
| Tests | 21 | 1,294 | 1,157 |
| **Implementation + tests** | **46** | **4,656** | **4,183** |

Component membership: runners include `runner.py`, `continuous.py`, `continuous_resume.py` and `resume_prepared.py`; reporting includes `collect.py`, `metrics.py`, `report.py` and `status.py`. Profiles include activation, skill trials/smokes, planning and Serena probes. Sonar includes client, bootstrap, loopback proxy and snapshot scanner.

The newly added continuous execution code is 448 lines in `continuous.py` plus 206 in `continuous_resume.py`: **654 implementation lines**. Its two focused test files contain 97 + 38 = **135 lines**. These are included in the totals above, not additional to them.

Separate tracked material at the same count: configuration/build files 2,073 physical lines; upstream OAuth patch 181 lines; vendored skill assets, including their docs/licenses, 2,552 lines. Frozen JSON records and generated reports are not implementation code. Counts use `len(path.read_text().splitlines())` over `git ls-files`; nonblank lines require `line.strip()` to be nonempty. These are not AST statement counts or production-only benchmark LOC.

## Benchmark implementations measured so far

| Phase 5 variant / step | Added production LOC | Deleted production LOC | Net | Churn |
| --- | ---: | ---: | ---: | ---: |
| Baseline, step 1 | 15 | 17 | −2 | 32 |
| Baseline, step 2, cumulative from initial source | 98 | 18 | 80 | 116 |
| Caveman, step 1 | 36 | 10 | 26 | 46 |

Benchmark production LOC excludes tests, inline Rust test regions, generated code and vendor files. Baseline step 2 is cumulative: do not add its row to step 1. The incremental churn of step 2 is 84. All three rows have accepted grader results and verified snapshots. The original Caveman step-2 quota stop and the partially executed Ponytail step have no completed submission metrics; their missing values remain null.

The three accepted task executions cannot establish a general quality or size advantage for any workflow. Live experiment state remains in [EXPERIMENT_STATUS.md](../EXPERIMENT_STATUS.md).
