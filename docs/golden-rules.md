# Golden Rules

이 규칙들은 **자동 검사 + 사람 게이트**로 강제된다. 위반 우회는 `docs/sop/human-approval.md`의 `RULE_OVERRIDE` 절차로만.

> 본 룰은 **Sourcetrail_Remake (Python 프로젝트)** 대상이다. C++ legacy 영역(`docs/references/architecture-rules.md` §7)은 G7만 적용된다.

| # | 규칙 | 강제 방법 |
|---|---|---|
| G1 | **린트/타입을 끄지 않는다.** `ruff check` 0건, `mypy --strict` 0건. `# noqa`/`# type: ignore`는 한 줄만, 사유 주석 필수 (`# type: ignore[<code>]  # reason: ...`). | `scripts/lint.sh`, `scripts/type-check.sh`. ruff `--fix`는 OK, `--unsafe-fixes`는 사람 승인. |
| G2 | **레이어 의존 방향을 위반하지 않는다.** (`docs/references/architecture-rules.md` §1) | `scripts/structure-check.sh`. |
| G3 | **테스트는 `bash scripts/run-tests.sh` (= `uv run pytest`)로만.** 직접 `pytest`/`python -m pytest` 호출 시 가상환경 외부 위험. | code review + `.codex/`/`.claude/` 어댑터의 allowlist. |
| G4 | **공용 유틸을 우선 사용한다.** ad-hoc 헬퍼 금지. 비슷한 기능이 `core/` / 기존 모듈에 있으면 그것을 쓴다. | code review + `scripts/structure-check.sh`의 `# LOCAL HELPER:` 주석 검색. |
| G5 | **AGENTS.md / CLAUDE.md에 정책을 복붙하지 않는다.** 모두 `docs/`로 링크. | `scripts/check-adapter-sync.sh`. |
| G6 | **PR은 작게.** 한 PR = 한 목적. 1000 LOC 이상 변경은 사람 승인 필수. | CI(`harness-gate.yml`)가 size 측정 → 1000 LOC 초과 시 `needs-human-review` 라벨 자동. |
| G7 | **C++ legacy 영역(`docs/references/architecture-rules.md` §7)을 임의로 수정하지 않는다.** 보존 결정. 새 자산은 `src/sourcetrail_remake/`, `tests/`, `docs/`, `scripts/`, `.codex/`, `.claude/`, `.github/`에만. | `scripts/structure-check.sh` + `.github/CODEOWNERS`. |
| G8 | **CI green 없이는 머지 금지.** Windows runner의 `harness-gate` + `ci`(Phase 0+) 둘 다 green. 환경 사정으로 로컬 미실행이면 PR에 명시 + CI green 필수. | branch protection. |
| G9 | **시크릿/토큰을 리포에 커밋하지 않는다.** `.env`, API 키, 코드 서명 키 등. | `scripts/structure-check.sh`의 패턴 검사. |
| G10 | **`docs/exec-plans/active/` plan 없이 1000 LOC 이상 작업하지 않는다.** | code review + `scripts/docs-freshness.sh`가 큰 PR과 plan 부재를 교차 검사. |
| G11 | **불변성 우선.** 가능하면 `@dataclass(frozen=True)`, 인자 변경은 명시적 반환. (글로벌 코딩 규칙과 호환) | code review. |
| G12 | **함수 50줄 / 파일 800줄 / 중첩 4단 상한**. 초과는 분할. | code review + `scripts/structure-check.sh` soft warn. |
| G13 | **`uv` 외 의존성 매니저 금지.** `pip install`, `poetry`, `pipenv`, `conda` 직접 사용 금지. 새 의존성은 `uv add <pkg>` → `uv.lock` 같이 커밋. | `scripts/structure-check.sh` + 어댑터 allowlist. |
| G14 | **SourcetrailDB 스키마 호환을 깨지 않는다.** 원본 `node`/`edge`/`symbol`/... 테이블의 컬럼/enum 변경 금지. Python 특화는 `edge_extension`/`node_extension`만. | `scripts/compat-check.sh` (Phase 0 PoC 1 이후 강화) + 매 phase 종료 시 `docs/sop/sourcetrail-compat.md` 절차. |
| G15 | **Windows 전용.** macOS/Linux 분기 코드 금지. `sys.platform != 'win32'` 가드 등 추가는 사람 승인. | code review. |

## 변경 절차

이 문서는 사람 승인 필수. PR 라벨 `golden-rule-change` + 최소 1명 maintainer 승인 + `docs/sop/human-approval.md` 따름.
