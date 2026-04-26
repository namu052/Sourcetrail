# Failure Modes

Sourcetrail_Remake (Python) 운영에서 흔한 15가지 실패 패턴 카탈로그. 새 사고 발생 시 항목 추가.

| # | 패턴 | 징후 | 원인 | 조기 탐지 | 교정 |
|---|---|---|---|---|---|
| 1 | **AGENTS.md / CLAUDE.md 중복 비대화** | 두 파일이 각각 500줄+. 같은 정책이 두 곳에 살짝 다르게. | 어댑터에 정책 본문 직접 작성. | `scripts/check-adapter-sync.sh` (첫 링크 + 30줄 임계). | docs/로 이전, 어댑터엔 링크만. |
| 2 | **문서 드리프트** | `references/build-and-test.md` ↔ `pyproject.toml` 버전 불일치. | 코드 변경 시 docs 갱신 누락. | `scripts/docs-freshness.sh` 정합성 검사. | 변경 PR에 docs 갱신 포함을 PR_TEMPLATE이 강제. |
| 3 | **Source of truth 혼란** | 같은 정책이 여러 파일에. | 같은 사실 산재. | grep으로 중복 정의 검색. | `docs/`에 단일 파일로 통합. |
| 4 | **Codex config 난립** | `.codex/`에 6+ 파일. | 작업마다 새 프로파일. | `.codex/README.md` 표가 4개 초과면 경고. | 3개로 통합. |
| 5 | **Claude skills 난립** | `.claude/skills/`에 10+ 폴더. | 한 번 쓸 절차도 SKILL로. | 분기 정기 스윕. | 6개월 미사용 SKILL 삭제. |
| 6 | **Hook 과잉** | 단순 명령에 다중 hook 끼어 작업 지연. | 모든 룰을 hook으로. | hook 응답시간 임계. | 핵심 차단 hook만 유지. |
| 7 | **Jedi unresolved 폭증** | 그래프가 회색 해치 노드로 도배. 사용자 "쓸모없다" 판단. | 동적 import / 메타클래스 / duck typing. | Phase 4 game G5: typed/untyped 비교로 50% 감소 측정. | F19 Type Hint, F20 Duck candidate, mypy/pyright 통합. |
| 8 | **SourcetrailDB 호환 깨짐** | 원본 Sourcetrail GUI에서 DB 로드 실패. | Python 특화 데이터를 원본 enum/테이블에 끼워넣음. | `scripts/compat-check.sh` 매 phase. | 원본 스키마 미훼손 + `edge_extension`/`node_extension`만 사용 (G14). |
| 9 | **PyQt event-loop 데드락** | UI 멈춤. 백그라운드 인덱서 응답 안함. | QThread에서 mainThread의 객체 직접 호출. | `tests/ui/`에 deadlock 시나리오 + `qtbot.waitUntil` timeout. | EventBus signal로만 cross-thread 통신 (`02-architecture.md` §6). |
| 10 | **mypy strict drift** | `# type: ignore`가 여기저기. 결국 strict 의미 없음. | edge case에 `# type: ignore` 남발. | grep으로 `# type: ignore` 카운트, 사유 주석 누락 검사. | 한 줄당 사유 필수, PR 본문에 누적 카운트 표시. |
| 11 | **pytest-qt fixture 누설** | UI 테스트가 다음 테스트의 위젯에 영향. | `qtbot.addWidget` 누락 또는 명시적 close 안함. | flaky test 발생 시 격리 우선. | `qtbot.addWidget(w)` 강제 + `pytest-qt` `qapp_args` 사용. |
| 12 | **PyInstaller 바이너리 비대화** | 인스톨러 200MB+ → Defender 의심. | 불필요 패키지 번들. | 매 RC 빌드 시 사이즈 추적 (`docs/generated/build-size.md`). | `--exclude` + UPX. 200MB 임계. |
| 13 | **uv.lock 미커밋** | CI 재현 실패. "내 머신에선 됨". | `uv add` 후 `uv.lock` 잊음. | `scripts/structure-check.sh`가 `pyproject.toml` 변경 시 `uv.lock` 동시 변경 검사. | PR_TEMPLATE 체크리스트 + git hook. |
| 14 | **C++ legacy 영역 무단 변경** | `src/lib*/`에 갑자기 새 .cpp 또는 수정. | 에이전트가 G7 모르고 작업. | `scripts/structure-check.sh` warn + `.github/CODEOWNERS`. | 라벨 `legacy-cpp-touch` + 사유 명시 강제. 우발적이면 revert. |
| 15 | **번아웃** (1인 풀타임 R-03) | 주말 commit, 새벽 commit, plan 정체. | 주 40h 상한 무시. | 주간 회고에서 commit 시간 분포 + plan `last_updated` 추이. | 사람 결정 — 휴식, 범위 축소. Phase 3+에 기능 이월 가능. |

## 운영

- 새 사고 → 7일 내 표에 추가 + 가능하면 검출 자동화도 추가.
- 분기마다 패턴별 발생 빈도 집계 → `docs/quality-score.md`의 부채 점수 입력.
- 신규 패턴 추가는 `docs/exec-plans/completed/`의 phase-N-retro.md에 자주 등장하는 항목에서 발굴.
