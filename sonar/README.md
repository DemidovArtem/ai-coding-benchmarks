# SonarQube integration — current state

API collector реализован и проверен на local HTTP fixtures. Настоящий SonarQube/scanner ещё не запускался; before/after scores отсутствуют. Это незавершённая часть Phase 4, не доказательство Rust analysis или snapshot binding.

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

Это **candidates**, а не проверенный runtime pin. Rust analyzer/rules должны быть подтверждены в реально запущенной 26.9 instance; `latest` не допускается. Первоначальное разрешение владельца покрывало только два benchmark-образа, не эти образы. Пока их не скачивать.

## Следующий полный slice

1. Подготовить reviewable scanner launch: immutable grader snapshot + common base, stable отдельные project keys через `project_key(trial_id, snapshot_sha256)`, одинаковые source exclusions, scanner version и rule-profile provenance.
2. Подготовить Cargo/Clippy отдельно от процесса, которому передаётся Sonar token. Нельзя ослаблять benchmark quarantine для scanner или передавать token agent/build scripts.
3. После подготовки setup/launch согласовать конкретную дополнительную загрузку по §0 handoff; запустить service только на `127.0.0.1`, создать защищённый admin password/token без записи в Git/CLI args.
4. Проверить Rust coverage, exact snapshot binding, реальные before/after measures и matched deltas; затем подключить их к canonical results. Сейчас этого доказательства нет.

## Collector interface

```bash
.venv/bin/python -m experiment.sonar --help
PYTHONPATH=vendor/SWE-Milestone .venv/bin/python -m pytest -q tests/test_sonar.py
```

После реального scanner launch collector принимает ceTaskId, project key, exact server version и output directory. Token читается только из `SONAR_TOKEN`; его значение не передаётся в command line. Не указывать вымышленные IDs или scores. Общие/new-code metrics и сравнения добавляются только при подтверждённой семантике reference state.
