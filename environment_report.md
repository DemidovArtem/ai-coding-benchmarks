# Аудит среды — Phase 0

**Обновление Phase 1:** загрузка двух образов согласована владельцем и завершена; [image identities](reports/downloaded_images.json). [Host OAuth smoke](reports/host_oauth_smoke.json) успешен. Agent-only patch и runner реализованы; [actual grader smoke завершён успешно](reports/phase1_smoke.md), artifacts сохранены в workspace. Ниже сохранён исходный снимок Phase 0.

Наблюдения: 19 октября 2026, Europe/Zurich; машинные timestamp сохранены в UTC. Цель v1 остаётся активной. Benchmark inference, host `codex exec` и grader не запускались. Phase 0 не расходовала benchmark-квоту; работа самого Codex в этой беседе расходует обычную квоту подписки.

## Проверенная среда

- Linux 6.17.0-35-generic, x86_64; 22 логических CPU.
- RAM: 30 GiB, примерно 13 GiB доступно на момент проверки; swap 8 GiB.
- Codex CLI **0.163.0**; `codex login status`: **Logged in using ChatGPT**. CLI выводит этот статус в stderr при exit code 0; preflight учитывает это.
- Host model: **gpt-6.1-sol**, reasoning **high**. Локальный models cache от 2026-10-18 содержит этот ID и поддерживаемый `high`. Доступность при inference пока не доказана.
- Docker client/server **29.6.0**, daemon доступен. Docker Root Dir: `/var/lib/docker` на корневом разделе, свободно примерно **44 GiB**.
- Рабочий `/home`: свободно примерно **1,9 GiB**; это ниже выбранного консервативного бюджета 5 GB для artifacts. Ничего из пользовательских файлов не удалялось.
- Системный Python **3.12.3**; изолированная `.venv` — **3.13.14**. uv **0.12.7**; Git **2.43.0**. Git LFS отсутствует.
- В `.venv` установлены только `PyYAML==6.0.3`, `pathspec==0.12.1`, `ast-grep-cli==0.51.0`. Настоящий `--help` harness проверен после установки Rust test filter. Без ast-grep `run_e2e` отказывался работать; проверка не отключалась.
- Cargo, Clippy и SonarScanner в host PATH не найдены. Rust toolchain внутри benchmark-образов ещё не проверен.
- GitHub, Hugging Face и Docker registry доступны. Слои Docker-образов не скачивались. Upstream source занимает около 14 МБ; sparse dataset — около 13 МБ.

[Машинный аудит](reports/environment.json) воспроизводится через `python -m experiment.audit`. Он намеренно возвращает `ready_for_smoke: false` до закрытия блокеров.

## Авторизация, квота и изоляция

`OPENAI_API_KEY`, `CODEX_API_KEY`, `UNIFIED_API_KEY` отсутствуют. Платные API не использовались. [Официальная документация](https://learn.chatgpt.com/docs/auth) различает доступ через ChatGPT subscription и API key billing; эксперимент закрепляет первый вариант.

[Quota snapshot](reports/quota_before_setup.json) получен через локальный `codex app-server`, методом `account/rateLimits/read`, без создания thread/turn. Использовано примерно **33%** окна 300 минут и **33%** окна 10080 минут. Reset timestamps сохранены. Эти значения округлены, меняются со временем и не являются точной стоимостью задачи; перед smoke их нужно обновить.

Host config содержит MCP, plugins, hooks, global AGENTS и skills. Их нельзя переносить в baseline. Сохранены только признаки наличия и количество MCP, без private settings, endpoints, credentials или env dump. `auth.json` не читался, не копировался и не коммитился.

Upstream `CodexFramework.get_container_mounts()` монтирует не только auth, но и **глобальный config.toml** read-only. Генерация чистого config внутри контейнера не устраняет доступ к этому host mount. Перед smoke удалить только config mount в agent adapter, сохранить минимальный OAuth mount и все запреты server-side/web/connected tools. Нельзя проверять baseline прямо из этого проекта с унаследованными host skills.

## Закреплённые источники и реальный lifecycle

- SWE-Milestone: `17a8f1593e172e26b36cea15e2b30fb9536c93f5`, локальная ветка `experiment/oauth-profiles`, diff пуст. Изучены README, setup, advanced, running-trials, Codex adapter, run_e2e, orchestrator, config и DAG selection.
- Benchmark/dataset version: **v1.0.2**, dataset commit `3500478e740d42583277c2658aa7729eb36e10f4`.
- Manifest, agent adapter, grading config, quarantine policy, dataset repository config и шесть metadata/DAG файлов закреплены SHA-256 в [experiment.yaml](experiment.yaml). Dataset clone чистый; filtered clone не использован как runtime authority.
- Первый isolated smoke: **maintenance_fixes_1_sub-01**, metadata main branch **master**. У узла нет входящих dependencies; выбор сделан до измерений. Protected runtime должен использовать **base-offline**, evaluator — pinned milestone image.
- [run_milestone --help](reports/run_milestone_help.txt) проверен реально. Есть `--workspace-root`, `--milestone-id`, `--srs-path`, `--agent`, `--model`, `--reasoning-effort`, `--timeout`, `--keep`. **Нет `--repo-name` и `--agent-version`**. Single-milestone runner пока не передаёт CLI version selector; adapter должен обеспечить точную установку 0.163.0.
- [run_e2e --help](reports/run_e2e_help.txt) содержит `--agent-version` и **`--milestones N`**, с dependency-closed topological prefix. Новый механизм early-stop для prefix не требуется.
- Однако первые два curated узла связаны только Weak edge, а default `ignore_weak_dependencies: true`. Поэтому для Phase 5 выбраны **milestone_seed_5f5da48_1_sub-01**, **milestone_seed_5f5da48_1_sub-02**: Strong FUNC edge, внешних входящих prerequisites нет ни в dependencies.csv, ни в additional_dependencies.csv. Их trial-local selection нужно реализовать без изменения исходного dataset. Pilot помечается non-official subset.
- Подготовку plan/goal_plan перед каждым unlocked milestone с сохранением executor session ещё нужно встроить в dispatch. Независимые `codex exec` не заменяют continuous trial.
- Evaluator, tests, quarantine, network policy и scoring не менялись.

## Конкретная загрузка для следующего этапа

[Registry manifest measurements](reports/image_budget.json) получены без скачивания слоёв:

| Назначение | Immutable digest | Сжатые bytes |
| --- | --- | ---: |
| Agent base-offline | `sha256:a22b225816bfc9fa243456a710bfc6e25ba6342c1162053a7876a73bfdec7e58` | 954017008 |
| Grader maintenance_fixes_1_sub-01 | `sha256:3157aa5b52406ddc6e48df65bf8f5003d650327c83cf89b11874c7f01113b425` | 1164863467 |

Сумма — **2118880475 bytes**, около **2,12 GB / 1,97 GiB**. Это верхняя оценка сетевой загрузки без вычета общих/кешированных слоёв. Распакованный размер ещё неизвестен. Предлагаемый резерв **12 GB** на Docker/один trial — бюджет, а не измеренный размер. На Docker-разделе место есть; runtime snapshots/логи предлагается размещать в `/tmp/ai-coding-experiment` на том же свободном разделе. `/tmp` не является долговременным хранилищем: итоговые artifacts нужно перенести до очистки/reboot.

После разрешения загрузки выполнить **только эти два pull по digest** и retag в соответствующие local refs из experiment.yaml. Не запускать `pull_images.sh --repo ripgrep`: он скачает все milestones.

```bash
docker pull hyd2apse/swe-milestone__burntsushi_ripgrep_14.1.1_15.0.0__base-offline@sha256:a22b225816bfc9fa243456a710bfc6e25ba6342c1162053a7876a73bfdec7e58
docker pull hyd2apse/swe-milestone__burntsushi_ripgrep_14.1.1_15.0.0__maintenance_fixes_1_sub-01@sha256:3157aa5b52406ddc6e48df65bf8f5003d650327c83cf89b11874c7f01113b425
```

## Блокеры и следующий шаг

1. Требуется разрешение владельца на substantial image download — это прямое требование §0 handoff. Нужны только два образа выше.
2. Требуется место для runtime artifacts: согласовать `/tmp/ai-coding-experiment` либо освободить минимум 5 GB в `/home`. Docker storage и глобальные настройки не переносить автоматически.
3. Реализовать минимальный OAuth-only adapter: не монтировать host config, закрепить CLI 0.163.0 в single runner, проверить sanitized effective config и quarantine внутри контейнера. Потом один host OAuth smoke и один actual grader smoke, с обновлённой квотой. Если OAuth не работает, диагностировать без API key fallback и без ослабления firewall.
4. Skills/MCP profiles и Sonar ещё не установлены для эксперимента. Их версии остаются `null`, а activation — false. Host Ponytail/Caveman не считаются экспериментальными профилями. Sonar pin и проверка Rust support потребуются в Phase 4; `latest` запрещён.

Привилегированные network/firewall изменения, глобальные Codex изменения и Phase 6 не выполнялись. Никакого full matrix launch до smoke gates.
