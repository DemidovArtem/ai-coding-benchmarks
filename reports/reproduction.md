# Воспроизведение isolated pilot

Эксперимент имеет два frozen cohort: planning (`experiment.yaml`) и skills (`reports/phase3_experiment.json`). Их baseline нельзя смешивать. Команды ниже запускают новые trials, а не воспроизводят прежний ответ модели побитно: inference недетерминирован, repeats требуют отдельного бюджета.

## Проверка сохранённых результатов без модели

1. Убедиться, что ignored `results/trials`, `results/sonar`, `vendor/SWE-Milestone`, dataset и `.venv` сохранены. Tracked reports содержат нормализованные результаты; raw traces, grader outputs и Git bundles в GitLab не отправляются.
2. Выполнить `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m pytest -q tests` и `git diff --check`.
3. Проверить pins: `.venv/bin/python -m experiment.audit --output /tmp/current_environment.json`. Исторический environment report не заменяет текущую проверку версии CLI/source tree.
4. Collector заново сверяет snapshot SHA, authoritative tag и Rust bytes с bundle, не запускает grader: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.collect results/trials/phase3_serena_001 --output /tmp/serena_recollected`. Путь output выбрать новый. Аналогично для остальных trials.
5. Sonar scan proofs/API responses находятся в `results/trials/<id>/sonar`, common base — `results/sonar/common_base`. `reports/sonar_pilot.json` связывает project/task/analysis IDs с каждым immutable snapshot. При необходимости повторный scan запускается по инструкции `sonar/README.md`; tokens не передаются в Cargo или model environment.

`PYTHONDONTWRITEBYTECODE=1` предотвращает generated `.pyc` в pinned dataset checkout. Dirty checkout блокирует model calls; не отключать этот gate ради generated caches или произвольных локальных изменений.

## Новый model trial

Сначала проверить live quota через `experiment.quota`; при 85% в любом окне trial runner остановится. Нужны ChatGPT OAuth, pinned CLI 0.163.0, отсутствие paid API keys, проверенные source pins и достаточно места. Каждый output должен быть новым, а предыдущий model trial — terminal. OS lock обеспечивает один model trial одновременно.

Phase 2 команды описаны в `reports/phase2_protocol.md`; Phase 3 — в `reports/phase3_protocol.md`. Не повторять успешные activation smokes без причины: их evidence на точном общем image уже заморожен. Profile setup всегда создаёт fresh container; `.serena` state и skill hook state не копируются из прежних trials. Если меняется runtime/profile/activation evidence, нужен новый явно названный cohort и fresh matched baseline, а не редактирование существующих frozen inputs.

Общий skill image сохранён локально как `ai-coding-skill-runtime:rust-1.88.0-python-3.13.14`, immutable ID `sha256:3407cf8372c295e58722ff3ce33a0797e59e768cdaec496e20a15ef876505269`. Проверить `docker image inspect --format '{{.Id}}' ai-coding-skill-runtime:rust-1.88.0-python-3.13.14`. Рецепт — `profiles/runtime/Dockerfile`; exact public Python/dependency inventory, 72 distribution versions, Node hash и Rust component URLs/SHA — в runtime manifests. Build context `/tmp/ai-coding-serena-runtime` был временным и после рестарта может отсутствовать; это не влияет на существующий immutable image или durable trial proofs. Для rebuild сначала восстановить тот же public interpreter/package closure из указанных installed paths и подтвердить полный inventory hash (`results/setup/serena/inventory.json`), не копируя user config/memories/credentials. Если closure или required binaries больше недоступны, rebuild требует отдельного setup; не заменять их новыми версиями незаметно.

## Локальный Sonar после рестарта

`docker compose -f sonar/compose.yaml up -d server` использует уже загруженный pinned image (`pull_policy: never`) и прежние named volumes. `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m experiment.sonar_proxy` открывает только 127.0.0.1:9000 и проверяет pinned server/internal network. Не запускать второй relay на занятом порту. Credentials остаются в private ignored файле и не выводятся. При остановке временного relay UI недоступен до его следующего запуска, но volume/API artifacts сохраняются.

Continuous требует отдельной dispatch integration по `reports/continuous_feasibility.md`. Independent trials этим workflow не заменяют continuous context. Larger repo/full chain/repetitions относятся к Phase 6 и не запускаются автоматически.
