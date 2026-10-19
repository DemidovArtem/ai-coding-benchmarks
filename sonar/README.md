# SonarQube integration — current state

API collector реализован и проверен на local HTTP fixtures. Sonar images загружены с разрешения пользователя 2026-10-19; scanner version smoke выполнен offline. SonarQube service запущен и защищён. Before/after analysis ещё не выполнялся. Это незавершённая часть Phase 4, не доказательство Rust analysis или snapshot binding.

## Реализовано

`experiment/sonar.py` использует только стандартную библиотеку:

- принимает только loopback HTTP URL `127.0.0.1`, игнорирует proxy environment, запрещает redirects и не пишет token в diagnostics;
- проверяет exact server version и task/project identity;
- ждёт Compute Engine SUCCESS; FAILED, CANCELED, timeout и неизвестный status дают отдельную ошибку;
- сверяет analysis ID до/после чтения measures, чтобы не приписать чужой latest scan старому snapshot;
- запрашивает только доступные metric keys и сохраняет отсутствующие значения как `null`;
- сохраняет raw responses, analyzer plugin metadata и quality profiles; требует Rust profile и ncloc;
- оставляет snapshot binding, Rust source coverage и new-code comparison **неподтверждёнными**, пока scanner launch не предоставит соответствующее доказательство.

`analysis_ok` относится к завершению API task и чтению measures. Оно само по себе не подтверждает, что scanner обработал нужный grader snapshot. `snapshot_binding_verified=false` и `rust_coverage_verified=false` нельзя заменять ручным утверждением. Remediation effort не является human review time.

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

## Следующий полный slice

1. Подготовить reviewable scanner launch: immutable grader snapshot + common base, stable отдельные project keys через `project_key(trial_id, snapshot_sha256)`, одинаковые source exclusions, scanner version и rule-profile provenance.
2. Подготовить Cargo/Clippy отдельно от процесса, которому передаётся Sonar token. Нельзя ослаблять benchmark quarantine для scanner или передавать token agent/build scripts.
3. Service и loopback relay запущены. `experiment.sonar_bootstrap` сменил начальный admin password и проверил token. Credentials сохраняются атомарно в ignored private directory (0700), file 0600; значения не попадают в CLI args, reports или Git.
4. Проверить Rust coverage, exact snapshot binding, реальные before/after measures и matched deltas; затем подключить их к canonical results. Сейчас этого доказательства нет.

## Collector interface

```bash
.venv/bin/python -m experiment.sonar --help
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m pytest -q tests/test_sonar.py
```

После реального scanner launch collector принимает ceTaskId, project key, exact server version и output directory. Token читается только из `SONAR_TOKEN`; его значение не передаётся в command line. Не указывать вымышленные IDs или scores. Общие/new-code metrics и сравнения добавляются только при подтверждённой семантике reference state.

## Подтверждённый runtime

[Runtime report](../reports/sonar_runtime.json): server **26.9.0.129388**, Rust analyzer **1.8.1.3395**, Sonar way Rust profile — **78 active rules**. Наличие analyzer/profile пока не доказывает обработку конкретного snapshot. H2 используется только для локального evaluation pilot; named volumes нужно сохранять вместе с private credentials.

```bash
docker compose -f sonar/compose.yaml up -d server
.venv/bin/python -m experiment.sonar_proxy
# In another terminal; do not print the credential file:
.venv/bin/python -m experiment.sonar_bootstrap --credentials results/sonar/private/credentials.json --report reports/sonar_runtime.json
```

Bootstrap повторно проверяет сохранённые credentials и не меняет уже защищённый password. Admin token не должен передаваться Cargo/build scripts или benchmark agents; scanner получит отдельный project analysis token.
