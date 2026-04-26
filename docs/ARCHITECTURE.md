# ARCHITECTURE

Phase 0에서는 전체 기능 구현보다 구조 고정과 리스크 제거가 목표다. 본 문서는 `docs/plan/02-architecture.md`를 구현 관점에서 압축한 문서다.

## Layers

- UI: `src/sourcetrail_remake/ui/`
- Application: `src/sourcetrail_remake/indexer/`, `search/`, `refactor/`, `core/event_bus.py`
- Domain: `src/sourcetrail_remake/core/project.py`, `core/types.py`
- Infrastructure: `src/sourcetrail_remake/db/`, `indexer/jedi_resolver.py`

허용 방향은 `UI -> Application -> Domain`, `Infrastructure -> Domain`이다. `cli/`는 headless entrypoint로 유지하며 `ui/`를 직접 import하지 않는다.

## Runtime Shell

- `python -m sourcetrail_remake`: 최소 `QMainWindow`를 띄우는 bootstrap shell
- `srm-gui`: 위와 동일한 GUI 엔트리포인트
- `srm-index`: 향후 인덱서 CLI 자리. Phase 0에서는 인자 검증과 경로 스캐폴드만 제공

## Database Strategy

- SQLite 기반 `.srctrldb`
- 스토리지 버전: `25`
- 원본 핵심 테이블은 C++ 구현과 동일하게 유지
- Python 특화 정보는 `edge_extension`, `node_extension`으로만 추가

## Phase 0 PoCs

- PoC 1: Jedi 정의 추출 결과를 SourcetrailDB 형태 SQLite에 기록
- PoC 2: PyQt6 + QScintilla editor bootstrap
- PoC 3: QGraphicsView 기반 고정 그래프 렌더링

