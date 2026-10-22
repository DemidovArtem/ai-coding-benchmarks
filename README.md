# AI-assisted coding experiment

Реализация [плана](AI_Coding_Experiment_Codex_Handoff.md): SWE-Milestone, Codex с ChatGPT OAuth, шесть изолированных вариантов, Git и SonarQube.

**Новый разрешённый этап:** baseline, Caveman, Ponytail и Serena, два независимых круга по пять последовательных правок. [Протокол Phase 6](reports/phase6_protocol.md), [средние кривые](reports/plots/MEAN_CURVES.md). Serena сохраняет memories внутри траектории и начинает cold в следующем повторе. Plan исключён из новых запусков.

**[Живой реестр экспериментов — результаты, метрики и будущие этапы](EXPERIMENT_STATUS.md).** Обновляется после запуска, завершения, ошибки или изменения плана. Регенерация из сохранённых records: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.status`.

**Isolated pilot v1 завершён:** все шесть variants реально выполнены через unchanged grader в двух matched cohorts; все получили resolved=true. [Итоговый отчёт](reports/pilot_report.md), [результаты](reports/summary.md), [проверка требований](reports/implementation_status.md). На том историческом этапе continuous был отложен. Текущие continuous trials и их ограничения отражены в живом реестре ниже. Raw artifacts сохранены в ignored results/trials; /tmp содержит рабочие копии.

- [Аудит среды и следующие действия](environment_report.md)
- [Закреплённые параметры](experiment.yaml) — JSON, совместимый с YAML 1.2; неизвестные значения остаются `null`.
- [Состояние требований](reports/implementation_status.md)
- [Размеры образов](reports/image_budget.json), [снимок квоты](reports/quota_before_setup.json)

## Проверка без benchmark-квоты

```bash
uv venv --python 3.13.14 .venv
uv pip install --python .venv/bin/python -r requirements-setup.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m experiment.audit --output reports/environment.json
```

Аудит проверяет source pins и setup; текущую квоту проверяет trial runner отдельно. Успешный static audit не разрешает обход quota gate и не доказывает завершённость v1. Runtime storage проверяется отдельно от заполненного рабочего раздела. Аудит не запускает агента, не скачивает образы, не меняет глобальные настройки Codex, Docker или firewall. Он сохраняет версии, хеши и только разрешённые признаки загрязнения профиля. Содержимое `auth.json` не читается.

## Восстановление исходников

Clone и runtime-артефакты исключены из Git. Выполнять из корня проекта, если каталогов ещё нет:

```bash
git clone https://github.com/DeepCommit-ai/SWE-Milestone.git vendor/SWE-Milestone
git -C vendor/SWE-Milestone checkout 17a8f1593e172e26b36cea15e2b30fb9536c93f5
git -C vendor/SWE-Milestone switch -c experiment/oauth-profiles
git -C vendor/SWE-Milestone apply ../../patches/swe-milestone-oauth.patch
git -C vendor/SWE-Milestone add -u
git -C vendor/SWE-Milestone commit -m "fix(codex): isolate profiles and pin milestone CLI"
git -c filter.lfs.smudge= -c filter.lfs.required=false clone --depth 1 --branch v1.0.2 https://huggingface.co/datasets/DeepCommit-ai/SWE-Milestone-data results/setup/dataset
git -C results/setup/dataset sparse-checkout set BurntSushi_ripgrep_14.1.1_15.0.0 config
git -C results/setup/dataset rev-parse HEAD
```

Upstream проверяется по исходному commit ancestry, точному patched Git tree и хешу patch. Локальный commit SHA после применения patch может отличаться из-за author/committer metadata; исходники обязаны совпадать byte-for-byte.

Dataset HEAD должен быть `3500478e740d42583277c2658aa7729eb36e10f4`. Полный checkout занимает около 187 МБ; после sparse-checkout ripgrep/config — около 13 МБ. Blob-filter clone на Hugging Face завершился ошибкой `expected 'packfile'`; обычный clone с последующим локальным sparse-checkout сработал. Git LFS отсутствует; если будущая версия содержит LFS pointers, сначала установить Git LFS. Не запускать benchmark с pointers вместо данных.

## Границы запуска

Только ChatGPT OAuth. Наличие `OPENAI_API_KEY`, `CODEX_API_KEY` или `UNIFIED_API_KEY` блокирует запуск; платного fallback нет. Benchmark-контейнеры не должны получать глобальные AGENTS, plugins, MCP, hooks или raw config пользователя.

[Single-milestone help](reports/run_milestone_help.txt) после локального patch содержит `--agent-version`; `--repo-name` не нужен. [Agent patch](patches/swe-milestone-oauth.patch) удаляет host config mount и его копирование при OAuth refresh, передаёт точный CLI pin и проверяет версию перед агентом. [Continuous help](reports/run_e2e_help.txt) содержит `--milestones`, но prefix из двух узлов не даёт сильной зависимости. Для Phase 5 закреплена пара glob milestones с сильной зависимостью; trial-local selection и planning dispatch ещё не реализованы.

Phase 6 требует отдельного разрешения после pilot report. Тесты аудита не подтверждают работоспособность evaluator, skill activation, SonarQube или continuous flow.

## Smoke runner

```bash
.venv/bin/python -m experiment.quota --output reports/quota_before_baseline_smoke.json
.venv/bin/python -m experiment.runner host-smoke --output /tmp/ai-coding-experiment/host_oauth_smoke_002
.venv/bin/python -m experiment.runner milestone-smoke --output /tmp/ai-coding-experiment/baseline_smoke_001
```

Не повторять уже выполненный host smoke без причины. Каталог output должен быть новым; runner не перезаписывает попытки. Baseline сохраняет default protected quarantine, unchanged grader, один executor attempt и исходный prompt. Перед агентом проверяются профиль, отсутствие MCP/skill/memory contamination, read-only host auth mount, версия CLI и network lockdown. Host smoke использует read-only sandbox; bypass остаётся только в изолированном benchmark-контейнере, как в upstream.

## Сбор результатов

```bash
.venv/bin/python -m experiment.collect results/trials/baseline_smoke_001 --output results/baseline_smoke_report
```

Collector не запускает grader заново. Он проверяет snapshot hash, submission tag и Rust content против bundle, затем считает test-excluded footprint. Неизвестные метрики остаются `null`; raw grader decisions сохраняются. [JSONL](results/results.jsonl), [CSV](results/results.csv), [summary](reports/summary.md) содержат smoke, три Phase 2 trials и четыре Phase 3 trials. Выводы ограничены одним заданием без повторений.

## Matched planning trials

[Замороженный протокол Phase 2](reports/phase2_protocol.md) описывает read-only mount, session isolation и quota gates. Запускать по одному:

```bash
.venv/bin/python -m experiment.runner trial --variant baseline --output /tmp/ai-coding-experiment/phase2_baseline_001
.venv/bin/python -m experiment.runner trial --variant plan --output /tmp/ai-coding-experiment/phase2_plan_001
.venv/bin/python -m experiment.runner trial --variant goal_plan --output /tmp/ai-coding-experiment/phase2_goal_plan_001
```

Каждый следующий запуск выполняется только после проверки terminal state предыдущего и текущей квоты. Planner failure не запускает executor. Output directories не перезаписываются.

[Phase 2 report](reports/phase2_progress.md): baseline, plan и goal_plan завершены, у всех grader resolved=true. Goal_plan продолжен после quota pause с сохранением исходного handoff. Все результаты относятся к одному заданию, без повторений.

## Sonar preparation

[SonarQube](sonar/README.md) работает локально на 127.0.0.1:9000. Общая база и восемь решений проанализированы; [результаты и ограничения](reports/sonar_pilot.md). Raw Sonar snapshots включают разные inline tests, поэтому эти дельты нельзя считать production-only эффектом.

## Skill cohort

[Phase 3 завершена](reports/phase3_progress.md): baseline/ponytail/caveman/serena получили resolved=true на одном общем runtime. [Protocol](reports/phase3_protocol.md) и [отдельная frozen конфигурация](reports/phase3_experiment.json) фиксируют image/activation/source hashes до измерений. Baseline не активирует hooks/MCP; Phase 2 baseline не подменяет baseline нового окружения.

Ponytail/Caveman имеют реальные native-hook audits. Serena прошла Codex MCP symbol smoke после фикса Rust env и required startup. В measured trial Serena не вызвала MCP и не выполнила onboarding: usage=0, memories=0, при подтверждённом server/RustAnalyzer startup. Польза MCP/памяти этим запуском не установлена.

Continuous реализован: Phase 5 дала 12 принятых двухшаговых submissions в историческом cohort. В Phase 6 подтверждены реальные Serena calls и сохранение memories между правками; четвёртый grader остановился на source-overlay collision. [Результаты и диагностика](reports/phase6_progress.md). Для исправленной пятишаговой матрицы подготовлен [отдельный протокол Phase 6b](reports/phase6b_protocol.md); прежние frozen cohorts не смешиваются.

## Пятишаговая матрица Phase 6b

[Отдельная frozen конфигурация](reports/phase6b_experiment.json) задаёт baseline, Caveman, Ponytail и Serena, два круга по пять задач. Запуск подготовленной очереди: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.phase6b`. Выполненные траектории пропускаются; незавершённая траектория требует явного recovery и не запускается заново под прежним ID. [Zero-model preflight](reports/phase6b_preflight.json), [порядок и ограничения](reports/phase6b_protocol.md). Актуальное число выполненных шагов — только в [живом реестре](EXPERIMENT_STATUS.md).
