# Phase 1 WBS Detail

Week 3-8 범위를 일 단위로 분해한 Phase 1 초안 WBS다. 상세 구현 순서는 `docs/plan/phase-1-mvp-indexer-graph.md`를 따른다.

## Week 3

- D11: `db/schema.py` / `db/writer.py` 정식화
- D12: `indexer/jedi_resolver.py` 확장
- D13: `indexer/parso_walker.py` 초안
- D14: `indexer/service.py` 기본 파이프라인
- D15: Jedi type -> `NodeKind` 매핑

## Week 4

- D16: `db/reader.py` 초안
- D17: 파일/소스 로케이션 적재
- D18: occurrence 적재
- D19: 오류 기록(`error`) 적재
- D20: fixture 기반 integration test

## Week 5

- D21: `ui/graph/scene.py`에서 DB 로드
- D22: `ui/graph/view.py` zoom/pan polish
- D23: 노드 렌더러
- D24: 엣지 렌더러
- D25: sample project end-to-end smoke

## Week 6

- D26: `ui/panels/context.py`
- D27: `ui/panels/symbol.py`
- D28: EventBus 연결
- D29: `ui/main_window.py` 도킹 레이아웃
- D30: UI smoke test

## Week 7

- D31: shallow index 모드
- D32: refresh/reindex 경로
- D33: unresolved 표시 규칙
- D34: basic search service
- D35: compatibility fixture 확장

## Week 8

- D36: image parity polish
- D37: graph interaction polish
- D38: phase regression pass
- D39: docs refresh
- D40: M1 / G2 gate review

