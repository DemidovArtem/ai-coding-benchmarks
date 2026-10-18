# AI-assisted coding experiment

Реализация [плана](AI_Coding_Experiment_Codex_Handoff.md): SWE-Milestone, Codex с ChatGPT OAuth, шесть изолированных вариантов, Git и SonarQube.

**Phase 1: два образа скачаны после согласования; host OAuth smoke успешен. Container/grader smoke — следующий gate.** Полный v1 не завершён. Runtime artifacts размещаются в `/tmp/ai-coding-experiment`; до очистки `/tmp` их нужно сохранить отдельно.

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

Последняя команда сейчас ожидаемо возвращает код `1`: container activation ещё не подтверждена. Runtime storage проверяется отдельно от заполненного рабочего раздела. Аудит не запускает агента, не скачивает образы, не меняет глобальные настройки Codex, Docker или firewall. Он сохраняет версии, хеши и только разрешённые признаки загрязнения профиля. Содержимое `auth.json` не читается.

## Восстановление исходников

Clone и runtime-артефакты исключены из Git. Выполнять из корня проекта, если каталогов ещё нет:

```bash
git clone https://github.com/DeepCommit-ai/SWE-Milestone.git vendor/SWE-Milestone
git -C vendor/SWE-Milestone checkout 17a8f1593e172e26b36cea15e2b30fb9536c93f5
git -C vendor/SWE-Milestone switch -c experiment/oauth-profiles
git -c filter.lfs.smudge= -c filter.lfs.required=false clone --depth 1 --branch v1.0.2 https://huggingface.co/datasets/DeepCommit-ai/SWE-Milestone-data results/setup/dataset
git -C results/setup/dataset sparse-checkout set BurntSushi_ripgrep_14.1.1_15.0.0 config
git -C results/setup/dataset rev-parse HEAD
```

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
