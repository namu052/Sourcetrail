# 00 · Sourcetrail_Remake 구현 계획 — 전체 요약

> Python 코드베이스를 **빠르고 관대하게** 탐색·분석하는 Windows 데스크톱 도구.
> Sourcetrail 오픈소스를 기반으로 **Source Insight 스타일 UX**를 결합한다.

---

## 1. 프로젝트 정체성

| 항목 | 내용 |
|------|------|
| 프로젝트명 | **Sourcetrail_Remake** |
| 한 줄 설명 | Sourcetrail 그래프 엔진 + Source Insight 에디터 UX의 Python 전용 재해석 |
| 타겟 사용자 | 대규모 Python 코드베이스 탐색자 (Django/ML/레거시 마이그레이션) |
| 차별화 포인트 | **Unsolved symbol을 1급 시민으로 인정** — Python 동적 특성을 숨기지 않고 시각화 |

---

## 2. 8가지 확정 사항

| # | 항목 | 결정 |
|---|------|------|
| 1 | 라이선스 | **GPL v3** (Sourcetrail/QScintilla와 일관성) |
| 2 | 에디터 위젯 | **QScintilla** (PyQt6 바인딩, 성숙도 최고) |
| 3 | MVP 범위 | **Phase 0-2 (16주)** — Context Window까지 포함 |
| 4 | 타겟 플랫폼 | **Windows 전용** (macOS/Linux 제외) |
| 5 | 개발 체계 | **1인 풀타임** |
| 6 | DB 호환성 | **SourcetrailDB 100% 호환** — 원본 Sourcetrail GUI에서도 열람 가능 |
| 7 | 레포명 | **Sourcetrail_Remake** 유지 |
| 8 | 기능 범위 | **27개 기능 전체 포함** (F1-F27) |

### 추가 결정 (파생)
- **UI 프레임워크**: QScintilla 바인딩 제약으로 **PyQt6** 확정 (PySide6 아님)
- **Python 버전**: 3.12 (최신 안정, Jedi 호환성 검증됨)
- **의존성 관리**: uv (빠른 설치, 프로젝트 락파일)
- **인덱스 포맷**: SQLite (SourcetrailDB `.srctrldb` 확장자 호환)

---

## 3. 일정 한눈에 보기

```
주차 │ 1 2 │ 3 4 5 6 7 8 │ 9 ······ 16 │ 17 ···· 22 │ 23 ···· 28 │ 29 30 31 │
─────┼─────┼─────────────┼─────────────┼────────────┼────────────┼──────────┤
P0   │ ███ │             │             │            │            │          │ 셋업 & PoC
P1   │     │ ███████████ │             │            │            │          │ MVP 인덱서+그래프
P2   │     │             │ █████████   │            │            │          │ ← MVP 완성
P3   │     │             │             │ ██████     │            │          │ 에디터 강화
P4   │     │             │             │            │ ██████     │          │ Python 특화
P5   │     │             │             │            │            │ ███      │ ← v1.0.0
P6   │ ═════════════════════ 전 기간 지속 (테스트 & 문서) ═══════════════════ │
```

### Phase별 요약

| Phase | 기간 | 누적 | 핵심 | 문서 |
|-------|------|------|------|------|
| **Phase 0** | 2주 | 2주 | 레포/CI/역공학/PoC 3종 | [phase-0-setup.md](phase-0-setup.md) |
| **Phase 1** | 6주 | 8주 | P0 기능 (이미지 재현) | [phase-1-mvp-indexer-graph.md](phase-1-mvp-indexer-graph.md) |
| **Phase 2** | 8주 | **16주 (MVP)** | F1-F4 (Context/Symbol/Relation/Editor) | [phase-2-context-panels.md](phase-2-context-panels.md) |
| **Phase 3** | 6주 | 22주 | F5-F10 (Rename/Search/Layouts) | [phase-3-editor-features.md](phase-3-editor-features.md) |
| **Phase 4** | 6주 | 28주 | F19-F27 (Python 특화) | [phase-4-python-specific.md](phase-4-python-specific.md) |
| **Phase 5** | 3주 | **31주 (v1.0)** | F11-F17 + 패키징 | [phase-5-packaging.md](phase-5-packaging.md) |
| **Phase 6** | 지속 | — | 80%+ 커버리지, 문서 | [phase-6-testing-docs.md](phase-6-testing-docs.md) |

**전체 기간**: **31주 (약 8개월)**, 1인 풀타임 기준.

---

## 4. 마일스톤

| 마일스톤 | 주차 | 기준 |
|---------|------|------|
| **M0 — Foundation** | 2 | PoC 3종 성공, CI 통과, SourcetrailDB 스키마 문서 완성 |
| **M1 — Image Parity** | 8 | 첨부 이미지와 동일한 그래프 UX 재현 완료 (Alpha 릴리스) |
| **M2 — MVP** | **16** | SI 핵심 4종 패널 완비, 자가 분석 가능 (**Beta 릴리스**) |
| **M3 — Productivity** | 22 | Rename/Search/Layouts 실용 수준 |
| **M4 — Differentiation** | 28 | Django/Jupyter 등 경쟁 도구 대비 우위 확보 (RC 릴리스) |
| **M5 — v1.0.0** | 31 | 인스톨러 배포, 사용자 매뉴얼 완비 |

---

## 5. 관련 문서

### 계획 단계 문서
- [01-requirements.md](01-requirements.md) — 27개 기능 상세 + P0-P5 우선순위
- [02-architecture.md](02-architecture.md) — 기술 스택, 모듈 구조, SourcetrailDB 호환 전략
- [03-risks.md](03-risks.md) — 전체 리스크 평가 및 완화 방안

### Phase별 실행 문서
- [phase-0-setup.md](phase-0-setup.md)
- [phase-1-mvp-indexer-graph.md](phase-1-mvp-indexer-graph.md)
- [phase-2-context-panels.md](phase-2-context-panels.md)
- [phase-3-editor-features.md](phase-3-editor-features.md)
- [phase-4-python-specific.md](phase-4-python-specific.md)
- [phase-5-packaging.md](phase-5-packaging.md)
- [phase-6-testing-docs.md](phase-6-testing-docs.md)

---

## 6. 문서 읽기 순서

| 독자 | 권장 순서 |
|------|----------|
| **Skim (5분)** | `00-overview.md` → 각 Phase 제목만 |
| **기술 검토 (30분)** | `00` → `02-architecture` → `03-risks` |
| **기능 이해 (20분)** | `00` → `01-requirements` |
| **전체 이해 (2시간)** | `00` → `01` → `02` → `03` → Phase 0-6 |
| **Phase 착수자** | `00` → 해당 Phase 파일 → `02-architecture` |

---

## 7. 성공 기준 (v1.0.0 기준)

### 기능
- [ ] F1-F27 모든 기능 구현 완료
- [ ] 첨부 이미지의 UX 100% 재현
- [ ] SourcetrailDB 생성한 DB를 원본 Sourcetrail GUI에서 열람 성공

### 품질
- [ ] 테스트 커버리지 80% 이상
- [ ] Windows 10/11에서 설치 → 실행 → 인덱싱 전 과정 성공
- [ ] CI 항상 green

### 성능
- [ ] 1만 LoC 인덱싱 < 1분 (Shallow)
- [ ] 그래프 첫 표시 < 500ms
- [ ] Fuzzy Lookup < 50ms (10만 심볼)
- [ ] 메모리 사용 < 2GB (대형 프로젝트)

### 사용성
- [ ] 자가 호스팅(dogfooding) 가능 — 이 프로젝트를 이 도구로 분석
- [ ] 사용자 매뉴얼 10개 챕터 완성
- [ ] 키보드 단축키 체계 정립

---

## 8. 릴리스 타임라인

| 릴리스 | 주차 | 대상 | 비고 |
|--------|------|------|------|
| Alpha | 8 | 내부 | 이미지 재현 검증 |
| **Beta** | 16 | 공개 | **MVP, 얼리어답터 피드백** |
| RC 1 | 24 | 공개 | Django/Jupyter 테스트 |
| RC 2 | 28 | 공개 | 기능 동결 |
| **v1.0.0** | **31** | 공개 정식 | 인스톨러 배포 |
