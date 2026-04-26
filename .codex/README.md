# .codex/ — Codex CLI Adapter (Sourcetrail_Remake / Python)

이 폴더는 **프로젝트 로컬 Codex 설정**이다. 글로벌 `~/.codex/config.toml`은 건드리지 않는다.

## 프로파일

| 파일 | 자율성 | 언제 |
|---|---|---|
| `config.toml` (기본) | L2 균형 | 일상 작업 — Python 개발/테스트/검증 |
| `config.balanced.toml` | L2 | `config.toml`의 명시 사본 (`check-adapter-sync.sh`가 동일성 검사) |
| `config.conservative.toml` | L1 | 탐색·리뷰·민감 영역 / C++ legacy 영역 작업 |
| `config.semi-autonomous.toml` | L3 | worktree 격리 + 자동 검증 + 자동 PR (잘 정의된 task) |

## 사용

```bash
codex                                                    # 기본 (균형)
codex --config .codex/config.conservative.toml           # 보수
codex --config .codex/config.semi-autonomous.toml        # 반자율
```

## 자율성 매핑

`docs/autonomy-levels.md` 참조.

| Profile | Level | 권한 요약 |
|---|---|---|
| `conservative` | L1 | 읽기 + ruff check / mypy 만 자동. 모든 쓰기/테스트 사람 승인. |
| `balanced` (기본) | L2 | uv 실행, 게이트 자동. 보호 경로 변경은 사람 승인. |
| `semi-autonomous` | L3 | worktree 강제. `feature/*` 푸시 + `gh pr create` 자동. master/protected 제외. |

## 핵심 원칙

- **uv가 의존성 매니저** — `pip`/`poetry`/`pipenv`/`conda`는 모든 프로파일에서 deny.
- **C++ legacy 보호** — `src/lib*`, `CMakeLists.txt` 등은 모든 프로파일에서 protected.
- **`docs/plan/`은 ADR 필요** — 대관 계획 변경은 사람 승인.

## 변경 절차

이 디렉터리의 어떤 변경도 [`docs/sop/human-approval.md`](../docs/sop/human-approval.md) 절차를 따라야 한다.
프로파일 추가는 사람 승인 후에만.
