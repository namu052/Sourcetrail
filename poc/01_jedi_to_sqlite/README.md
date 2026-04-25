# PoC 01 — Jedi to SourcetrailDB

이 PoC는 `tests/fixtures/sample-minimal/session_manager.py`를 읽어 Jedi 정의를 추출하고, Phase 0용 `.srctrldb` 파일을 생성한다.

## Run

```bash
uv run python poc/01_jedi_to_sqlite/run.py
```

## Outputs

- `poc/01_jedi_to_sqlite/artifacts/sample-minimal.srctrldb`
- `poc/01_jedi_to_sqlite/artifacts/sample-minimal.srctrlprj`
- `poc/01_jedi_to_sqlite/artifacts/report.json`

## Manual Gate Status

- 원본 Sourcetrail GUI `Version 2021.4.19 - 64bit` / `Database Version 25` 기준으로 `sample-minimal.srctrlprj` 열람 성공.
- Overview 패널에서 `41 symbols`, `40 references`, `0 errors (0 fatal)` 확인.
- Smart Search 기반 심볼 drill-down은 별도 후속 검증 항목으로 남겨둔다.

## G1 Manual Validation Helper

```bash
uv run python scripts/prepare_g1_validation.py --launch
```

기본 실행 파일 경로는 `C:\Program Files\Sourcetrail\Sourcetrail.exe` 이다.
이 스크립트는 다음을 수행한다.

- PoC 1 DB 재생성
- `artifacts/sample-minimal.srctrlprj` 준비
- 원하면 원본 Sourcetrail GUI를 `--project-file`로 실행
