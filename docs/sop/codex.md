# SOP — Codex CLI (Sourcetrail_Remake / Python)

Codex CLI로 본 리포에서 작업할 때의 표준 절차. **공용 진입은 `AGENTS.md` → 이 SOP → `docs/README.md` → `docs/plan/00-overview.md`** 순.

## 1. 시작

```bash
codex                                                    # 균형 (L2, 기본)
codex --config .codex/config.conservative.toml           # 보수 (L1)
codex --config .codex/config.semi-autonomous.toml        # 반자율 (L3)
```

## 2. 표준 작업 루프

| 단계 | 행위 | Codex 실행 포인트 |
|---|---|---|
| 1. 컨텍스트 | `docs/README.md` + `docs/plan/00-overview.md` + 해당 phase 파일 | Codex 자동 read |
| 2. 계획 | 1000+ LOC면 `docs/exec-plans/active/` 새 plan | Codex |
| 3. 재현 | 버그면 실패 케이스 먼저 (`tests/<area>/test_*.py`) | Codex |
| 4. 수정 | 작은 단위 patch | Codex |
| 5. 검증 | `bash scripts/verify-all.sh` + `bash scripts/run-tests.sh -m <marker>` | Codex (allowlist) |
| 6. 자기 리뷰 | `docs/quality-score.md` 체크 | Codex |
| 7. (해당 시) compat | `bash scripts/compat-check.sh tests/fixtures/...` | Codex (allowlist) |
| 8. PR | `.github/PULL_REQUEST_TEMPLATE.md` | 사람 승인 후 Codex |

## 3. 권한 / 샌드박스

기본은 `.codex/config.toml` (L2 균형). 다음은 **반드시 사람 승인**:

- `pyproject.toml`, `uv.lock`, `.pre-commit-config.yaml` 수정.
- 새 외부 의존성 (`uv add <pkg>`).
- 새 hook, golden rule, security/reliability 정책 변경.
- `docs/plan/` 변경 (대관 계획).
- 1000 LOC 이상 변경.
- C++ legacy 영역 변경 (G7).
- network access (CI 외부 호출, 패키지 설치 등).

승인 요청 템플릿:

```
[Codex 권한 요청]
- 무엇을: <명령 또는 변경 범위>
- 왜: <연결된 exec-plan 경로 + phase>
- 영향: <파일 N개, LOC ±M>
- 롤백: <git revert 가능 여부, 추가 정리 필요 여부>
- (해당 시) compat 영향: <DB/스키마 변경 여부>
```

## 4. 위험 명령 통제

`.codex/config.toml`의 deny 리스트:

- `rm -rf /` 또는 절대경로 대량 삭제
- `git push --force` (특히 master)
- `git reset --hard`, `git commit --amend`, `git commit --no-verify`
- `sudo` 모든 명령
- `pip install`, `pip3 install`, `poetry`, `pipenv`, `conda` (G13 위반)

## 5. worktree 운영

병렬 작업 충돌 방지. [`worktree.md`](worktree.md) 참조. L3에선 `require_worktree = true`.

## 6. 종료 시

- 머지된 plan은 `docs/exec-plans/completed/`로 이동 (회고 작성).
- worktree 제거.
- 임시 인덱스 DB (`.tmp-srctrldb/`) 정리.

## 7. Codex 전용 주의

- **subagents**: 같은 task 반복 작업 외엔 자제.
- **memory**: Codex 자체 메모리 사용 금지 — SoT는 `docs/`.
- **auto-confirm**: `--yes`는 §3 승인 항목엔 절대 금지.
- **stdout/stderr**: 백그라운드 프로세스 (uv run pytest --log-file) 출력은 `docs/generated/`로 리디렉션 권장.
