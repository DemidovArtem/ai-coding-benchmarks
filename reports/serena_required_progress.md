# Serena-first: обязательное использование, отдельный вариант

Статус: **policy реализована; smoke заблокирован quarantine до модели**. Measured benchmark trial ещё не запускался. Исходный `phase3_serena_001` с нулём MCP calls сохранён и не переименован в успешное использование Serena.

## Что показала диагностика

В исходном measured trial сервер действительно запустился с 23 tools, RustAnalyzer стартовал без ошибок, запрос `ListToolsRequest` обработан. `required=true` присутствовал в effective profile. В trace нет MCP calls и нет явного startup failure. Это доказывает работу подключения, но не намерение модели использовать его. Без отдельной Serena-first policy task был выполнен shell-инструментами. Сам размер repository не обязывает модель выбрать MCP.

В локальном `/home/artem-demidov/PycharmProjects/DS/llm-auto-tuning-ml/AGENTS.md:133` найден пользовательский принцип Serena-first: для индексируемого Python-кода сначала symbolic navigation, rg/line reads как fallback. Он использован как образец policy, адаптированный для Rust; private configs, memories и unrelated project instructions не копируются.

## Новый workflow

В контейнере `serena_required` после clean baseline audit устанавливается отдельный read-only `/home/fakeroot/.codex/AGENTS.md`. Он требует `initial_instructions`, cold `onboarding`, реальные символы через `get_symbols_overview`/`find_symbol` и factual note через `write_memory` до shell/source work. Сам benchmark checkout не получает AGENTS-файл. MCP/network/model/runtime остаются такими же; hooks и plugins дополнительно не включаются.

`experiment.serena_required.verify_required_usage` проверяет реальные successful MCP events и их порядок. Zero usage, failed/empty semantic results, преждевременные shell/source edits дают отдельный activation/policy failure; такой результат нельзя засчитать как обычный baseline или валидный mandatory-Serena trial. Это не обещание, что модель никогда не нарушит policy: нарушение обнаруживается и делает trial невалидным.

Neutral smoke использует новый однофайловый Cargo repository, пустые memories и общий pinned runtime. Сам user prompt не называет MCP tools: обязательный порядок задаёт именно AGENTS.md. Model должна выполнить onboarding и symbolic navigation, затем описать функцию без изменения source. Её usage/time — setup overhead, вне benchmark A/B. Source hash проверяется до/после; никакие smoke memories не передаются в реальные trials.

После успешного smoke новый measured вариант требует отдельного frozen cohort/протокола и учёта cold onboarding. Старое сравнение доступности Serena и новый Serena-first workflow — разные экспериментальные условия.

## Последовательные задачи

Схема «первая правка, вторая, третья» соответствует Phase 5. Нужны один постоянный executor, immutable submission на каждом шаге, prep/ack перед публикацией следующего SRS, одинаковая dependency-consistent trajectory и per-step grader/Git/Sonar. Обновлённая Serena policy сама по себе эту интеграцию не реализует. [Существующий точный blocker и следующий slice](continuous_feasibility.md).

Первый neutral smoke остановлен до model turn: pinned quarantine probe установил TCP reachability к запрещённому `static.crates.io`. Это отдельный infrastructure/security blocker, а не проверка или отказ Serena policy. Результат и свежая quota snapshot сохранены; model usage отсутствует. Host proxy env отсутствует; registry DNS на момент диагностики входит в запрещённый Fastly CIDR. Для установления причины выполняется отдельный zero-model network diagnostic с прежними правилами; scoring/quarantine не ослабляются.
