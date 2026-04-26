---
title: Execution Plans Index
status: Active
last_updated: 2026-04-25
---

# Sourcetrail_Remake — 실행 계획 (Execution Plans)

> Sourcetrail 오픈소스를 기반으로 Source Insight 스타일 UX를 결합한 **Python 전용 코드 분석 데스크톱 도구**의 구현 계획입니다.

## 확정 파라미터

| 항목 | 결정 |
|------|------|
| 라이선스 | **GPL v3** (Sourcetrail 상속) |
| UI 프레임워크 | **PyQt6** (GPL 라이선스 일관성) |
| 에디터 위젯 | **QScintilla** (PyQt6 바인딩) |
| 파싱/분석 | Jedi 0.19+, Parso, Rope, Tree-sitter |
| DB | SQLite — **SourcetrailDB 스키마 100% 호환** |
| 타겟 플랫폼 | **Windows 전용** |
| 개발 체계 | **1인 풀타임** |
| MVP 범위 | Phase 0 ~ Phase 2 (16주) |
| 전체 일정 | **31주 (약 8개월)** |
| 프로젝트명 | **Sourcetrail_Remake** |
| 테스트 커버리지 | 80% 이상 유지 |

## Phase 개요

| Phase | 기간 | 누적 | 문서 | 핵심 결과물 |
|-------|------|------|------|-------------|
| [Phase 0](phase-0-setup-and-poc.md) | 2주 | 2주 | 셋업 & PoC | 레포/CI/PoC 3종 |
| [Phase 1](phase-1-mvp-core.md) | 6주 | 8주 | MVP Core | 인덱서 + 그래프 뷰 |
| [Phase 2](../completed/phase-2-source-insight-panels.md) | 8주 | **16주 (MVP)** | SI 핵심 패널 | Context / Symbol / Relation / Editor |
| [Phase 3](phase-3-editor-productivity.md) | 6주 | 22주 | 에디터 강화 | Rename / Search / Layouts |
| [Phase 4](phase-4-python-specialization.md) | 6주 | 28주 | Python 특화 | TypeHint / Django / Jupyter |
| [Phase 5](phase-5-polish-and-packaging.md) | 3주 | 31주 | 완성도 & 패키징 | 테마 / Export / 인스톨러 |
| [Phase 6](phase-6-testing-and-docs.md) | 지속 | — | 테스트 & 문서 | 80%+ 커버리지 |

## 타임라인

```
주차 │ 1 2 │ 3 4 5 6 7 8 │ 9 ······ 16 │ 17 ···· 22 │ 23 ···· 28 │ 29 30 31 │
─────┼─────┼─────────────┼─────────────┼────────────┼────────────┼──────────┤
0단계│ ███ │             │             │            │            │          │
1단계│     │ ███████████ │             │            │            │          │
2단계│     │             │ █████████   │            │            │          │ ← MVP
3단계│     │             │             │ ██████     │            │          │
4단계│     │             │             │            │ ██████     │          │
5단계│     │             │             │            │            │ ███      │
6단계│ ═══════════════════════ 전 기간 지속 ══════════════════════════════  │
```

## 마일스톤

| 마일스톤 | 주차 | 기준 |
|----------|------|------|
| **M0 — Foundation** | 2 | PoC 3종 성공, CI 통과 |
| **M1 — Image Parity** | 8 | 첨부 이미지와 동일 UX 재현 |
| **M2 — MVP (Alpha→Beta)** | 16 | SI 핵심 4종 패널, 자가 분석 가능 |
| **M3 — Productivity** | 22 | Rename/Search/Layouts 실용 수준 |
| **M4 — Differentiation** | 28 | Django/Jupyter 경쟁 우위 확보 |
| **M5 — v1.0.0 Release** | 31 | 인스톨러 배포, 매뉴얼 완비 |

## 기능 우선순위 (27개)

- **P0 (이미지 기반, 필수)**: 멀티 탭 / 히스토리 / FQN 검색 / 그래프 뷰 / Unsolved 노드 / 엣지 타입 / 심도·줌·북마크
- **P1 (SI DNA)**: F1 Context Window · F2 Symbol Window · F3 Relation Tree · F4 Syntax Formatting
- **P2 (생산성)**: F5 Smart Rename · F6 Fuzzy Lookup · F7 Lookup References · F8 Layouts · F9 Bookmarks+ · F10 Clips
- **P3 (완성도)**: F11 Search Project · F12 Overview Scroller · F13 Folding · F14 Revision · F15 MFL
- **P4 (옵션)**: F16 Custom Language · F17 Export · F18 Dir Compare
- **P5 (Python 차별화)**: F19 Type Hint · F20 Duck Typing · F21 Framework · F22 venv · F23 Jupyter · F24 Import Graph · F25 Decorator · F26 Dynamic · F27 Shallow/Deep

## 문서 관리 규칙

- `active/` — 현재 진행 중인 Phase 계획
- `completed/` — 완료된 Phase 아카이브 (각 Phase 종료 시 이동)
- `archived/` — 폐기/대체된 계획

각 Phase 문서는 **착수 시 WIP → 진행 중 업데이트 → 종료 시 회고 추가 → completed/ 로 이동** 흐름으로 관리합니다.

## 리스크 게이트

| 주차 | 점검 | 실패 시 대응 |
|------|------|-------------|
| 2 | PoC 1 (Jedi → SourcetrailDB) 성공? | Parso 단독 fallback 검토 |
| 8 | 10만 LoC 그래프 60fps? | LoD 도입, 뷰포트 컬링 |
| 16 | 자가 호스팅(dogfooding) 가능? | Phase 3로 부족 기능 이월 |
| 22 | Smart Rename 회귀율 < 1%? | LibCST 기반 재작성 검토 |
| 28 | 타입 힌트로 unsolved 50% 감소? | mypy/pyright 통합 강도 조절 |
