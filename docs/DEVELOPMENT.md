# DEVELOPMENT

Phase 0 기준 개발자 진입 문서다. 상세 정책은 `docs/references/build-and-test.md`, `docs/sop/codex.md`, `docs/golden-rules.md`가 SoT다.

## Environment

- Windows 10/11
- Python 3.12
- `uv`
- PyQt6 + PyQt6-QScintilla

## Setup

```bash
uv sync --all-extras
```

## Common Commands

```bash
bash scripts/verify-all.sh
bash scripts/run-tests.sh
bash scripts/run-tests.sh -m unit
bash scripts/run-tests.sh -m ui
uv run python -m sourcetrail_remake --auto-quit-ms 100
uv run srm-index tests/fixtures/sample-minimal
uv run srm-gui --auto-quit-ms 100
```

## Repository Focus

- Python work happens under `src/sourcetrail_remake/`.
- C++ legacy paths are read-only reference.
- Phase 0 PoCs live under `poc/`.

## Deliverables Added In Phase 0

- `pyproject.toml` / `uv.lock`
- `.github/workflows/ci.yml`
- `.pre-commit-config.yaml`
- `docs/ARCHITECTURE.md`
- `docs/db-schema.md`
- `docs/plan/phase-1-wbs-detail.md`
- `poc/01_jedi_to_sqlite/`
- `poc/02_editor_hello/`
- `poc/03_graph_hello/`

