# SonarQube integration — current state

Sonar images загружены с разрешения пользователя и закреплены digest. Общая база и восемь graded solution snapshots реально проанализированы: exact snapshot binding, coverage 79 Rust files и неизменность 78 rules подтверждены для каждого scan. [Сводка и ограничения](../reports/sonar_pilot.md), [машинные результаты](../reports/sonar_pilot.json). API-only collector сам по себе не доказывает source binding; scan wrapper и canonical collector проверяют её отдельно.

## Реализовано

`experiment/sonar.py` использует только стандартную библиотеку:

- принимает только loopback HTTP URL `127.0.0.1`, игнорирует proxy environment, запрещает redirects и не пишет token в diagnostics;
- проверяет exact server version и task/project identity;
- ждёт Compute Engine SUCCESS; FAILED, CANCELED, timeout и неизвестный status дают отдельную ошибку;
- сверяет analysis ID до/после чтения measures, чтобы не приписать чужой latest scan старому snapshot;
- запрашивает только доступные metric keys и сохраняет отсутствующие значения как `null`;
- сохраняет raw responses, analyzer plugin metadata и quality profiles; требует Rust profile и ncloc;
- оставляет snapshot binding, Rust source coverage и new-code comparison **неподтверждёнными**, пока scanner launch не предоставит соответствующее доказательство.

`analysis_ok` относится к завершению API task и чтению measures. Оно само по себе не подтверждает, что scanner обработал нужный grader snapshot. API-only collector оставляет `snapshot_binding_verified=false` и `rust_coverage_verified=false`. `experiment.sonar_scan` выставляет их только после проверки tar SHA/tag bytes, staged source manifest, scanner task identity и полного Rust file coverage через Web API. Remediation effort не является human review time.

[Официальный Web API](https://docs.sonarsource.com/sonarqube-community-build/extension-guide/web-api) документирует bearer authentication и measures. [Background tasks](https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/background-tasks) объясняет, почему scanner success ещё не означает готовность server results. [Rust analysis](https://docs.sonarsource.com/sonarqube-community-build/analyzing-source-code/languages/rust) требует Cargo/Clippy и описывает external Clippy report import.

## Проверенные download candidates

[Machine-readable forecast](setup_candidates.json) получен из DockerHub metadata, без загрузки слоёв:

- Server: `sonarqube:26.9.0.129388-community`, digest `sha256:c0f1160bccfa435db4168c2d7df69af3c3ea7bfeb87395613014048fb33a68c1`.
- Scanner Docker image: `sonarsource/sonar-scanner-cli:12.2.0.4256_8.1.0`, digest `sha256:a3f4215076706c95a17a68c19322ee916e40a3acd081a8c1a1e839e0194afa57`.
- Сумма DockerHub `full_size`: **1489710351 bytes**, примерно **1,49 GB**. Фактическая загрузка зависит от platform и общих слоёв; unpacked size ещё не измерен.
- На Docker/root разделе было около 36 GiB свободно; MemAvailable — около 12 GiB. `vm.max_map_count=1048576`; sysctl не менялись.

Пользователь согласовал дополнительную загрузку 2026-10-19. Оба digest загружены для linux/amd64; local image IDs и размеры сохранены в JSON. Суммарный unpacked image size — 2430351264 bytes (общие слои не вычитаются). Scanner smoke: **8.1.0.6389**. Rust analyzer/rules ещё требуют проверки в запущенной 26.9 instance; `latest` не допускается.

`compose.yaml` закрепляет digest и `pull_policy: never`, публикует только `127.0.0.1:9000` и использует отдельную internal Docker network. Создание сети и запуск service отдельно согласованы пользователем 2026-10-19. Service запущен; host sysctl/firewall и benchmark quarantine не менялись. Docker 29.6.0 сохраняет PortBindings, но не публикует порт для internal-only сети. Поэтому `experiment.sonar_proxy` предоставляет loopback-only relay до IP закреплённого server container. Он проверяет image ID, running state и единственную internal network; external network не добавляется. Relay надо перезапустить после пересоздания container.

`Dockerfile.clippy` добавляет только Clippy 1.88.0 к исходному benchmark image. Производный image собран отдельно; Cargo/rustc/Clippy версии подтверждены без сети и записаны в JSON. Исходный benchmark image не изменён.

## Scan pipeline

`experiment.sonar_scan` проверяет исходный grader snapshot SHA и submission tag, восстанавливает common-base build support и накладывает только разрешённый capture. Все выбранные Rust-файлы solution сверяются byte-for-byte с graded tar. Исключённые embedded resources (completion scripts/help templates) берутся из common base и отдельно хешируются. Они нужны Cargo, но не входят в source analysis.

Clippy работает в отдельном непривилегированном контейнере: network none, no-new-privileges, cap-drop ALL, source mount read-only, без credentials. Cargo запускается offline/locked для workspace lib/bin с default features. `--cap-lints warn` сохраняет все lint diagnostics и позволяет завершить обход; compilation errors остаются fatal. Временный target directory имеет exec только внутри этого контейнера, без изменения benchmark quarantine.

Scanner получает отдельный project analysis token и только internal network. Build scripts с этим token не запускаются: auto Clippy выключен, импортируется сохранённый JSON report. Token отзывается в finally; ошибка отзыва фиксируется. Project private, key зависит от immutable snapshot identity. Scanner source mount read-only; JRE provisioning выключен, используется Java 21 из закреплённого image.

[Analysis protocol](analysis_protocol.json) закрепляет analyzer, scanner, Clippy, exclusions и все 78 активных Rust rules с параметрами/severity. До и после scan проверяется hash правил. Collector ждёт CE SUCCESS и сверяет analysis ID, затем scan wrapper подтверждает точное множество Rust components. Raw responses, scanner/Clippy logs, manifests и normalized measures сохраняются в ignored durable results.

```bash
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.sonar_scan results/trials/phase2_baseline_001 --kind base --output /tmp/ai-coding-sonar/unique-base-run --credentials results/sonar/private/credentials.json
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m experiment.sonar_scan results/trials/phase2_baseline_001 --kind solution --output /tmp/ai-coding-sonar/unique-solution-run --credentials results/sonar/private/credentials.json
```

Output directory должен быть новым; failed attempts сохраняются. Повторный scan того же snapshot использует тот же private project key; конкурирующие snapshots имеют разные keys. Перед публикацией в canonical records solution directory копируется в `results/trials/<trial>/sonar`, common base — в `results/sonar/common_base`. Collector повторно проверяет принадлежность Sonar result к graded submission и публикует matched aggregate deltas только при одинаковых starting tree/protocol/exclusions.

**Ограничение:** raw Rust snapshots включают различающийся inline test-код. Это точные snapshot metrics, а не production-only quality effect. Их нельзя смешивать с AST-filtered physical LOC или объяснять разницу только workflow. Отдельные project keys не дают достоверных new-code semantics: `new_maintainability_issues=null`, `new_code_comparison_valid=false`. Remediation effort — оценка Sonar, не human review time.

## Collector interface

```bash
.venv/bin/python -m experiment.sonar --help
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m pytest -q tests/test_sonar.py
```

После реального scanner launch collector принимает ceTaskId, project key, exact server version и output directory. Token читается только из `SONAR_TOKEN`; его значение не передаётся в command line. Не указывать вымышленные IDs или scores. Общие/new-code metrics и сравнения добавляются только при подтверждённой семантике reference state.

## Подтверждённый runtime

[Runtime report](../reports/sonar_runtime.json): server **26.9.0.129388**, Rust analyzer **1.8.1.3395**, Sonar way Rust profile — **78 active rules**. Наличие analyzer/profile само по себе не доказывает обработку snapshot; runtime proof дополняется exact bindings в каждом trial. H2 используется только для локального evaluation pilot; named volumes нужно сохранять вместе с private credentials.

```bash
docker compose -f sonar/compose.yaml up -d server
.venv/bin/python -m experiment.sonar_proxy
# In another terminal; do not print the credential file:
.venv/bin/python -m experiment.sonar_bootstrap --credentials results/sonar/private/credentials.json --report reports/sonar_runtime.json
```

Bootstrap повторно проверяет сохранённые credentials и не меняет уже защищённый password. Admin token не должен передаваться Cargo/build scripts или benchmark agents; scanner получит отдельный project analysis token.
