# PoC 01 — Jedi to SourcetrailDB

이 PoC는 `tests/fixtures/sample-minimal/session_manager.py`를 읽어 Jedi 정의를 추출하고, Phase 0용 `.srctrldb` 파일을 생성한다.

## Run

```bash
uv run python poc/01_jedi_to_sqlite/run.py
```

## Outputs

- `poc/01_jedi_to_sqlite/artifacts/sample-minimal.srctrldb`
- `poc/01_jedi_to_sqlite/artifacts/report.json`

## Remaining Manual Gate

- 원본 Sourcetrail Windows GUI 바이너리가 현재 워크스페이스에 없어 `GUI open` 단계는 별도 수동 검증이 필요하다.

