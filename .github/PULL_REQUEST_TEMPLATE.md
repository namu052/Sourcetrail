<!--
공용 하네스 PR 템플릿. 모든 절은 비워두지 않는다.
참조: docs/quality-score.md, docs/sop/human-approval.md, docs/sop/sourcetrail-compat.md
-->

## Summary

<!-- 1~3 문장. "무엇이 달라졌는지" 결과 중심. -->

## Why

<!-- 연결된 exec-plan + phase 링크. 1000+ LOC면 필수. -->
- exec-plan: `docs/exec-plans/active/<file>.md`
- phase: `docs/plan/phase-N-*.md`
- 관련 spec / design (있으면):

## Test plan

<!-- 어떤 마커로 어떻게 검증했는가. -->
- [ ] `bash scripts/verify-all.sh` 통과
- [ ] `bash scripts/run-tests.sh -m unit` 통과
- [ ] `bash scripts/run-tests.sh -m integration` (해당 시)
- [ ] `bash scripts/run-tests.sh -m ui` (UI 변경 시)
- [ ] `bash scripts/compat-check.sh tests/fixtures/<sample>/` (DB/스키마 영향 시)
- [ ] (UI/시각 회귀 가능성) `docs/observability.md` §5 시나리오 # 수동 확인

## Risk & rollback

<!-- 회귀 시 어떻게 되돌리는가. revert만으로 충분한지. -->
- 영향 범위:
- 롤백 방법: `git revert <SHA>` / 추가 정리 필요 사항:
- (해당 시) DB 마이그레이션 영향:

## Quality score

<!-- docs/quality-score.md §1 표 자체 산출. CI가 코멘트로 재계산. -->
- Build & test green (25):
- Lint & format (8):
- Type check (7):
- Structure rules (10):
- Test coverage delta (12):
- SourcetrailDB compat (15):
- PR size (8):
- Exec-plan linkage (8):
- Self-review checklist (7):
- **Total**: __/100

## Self-review checklist

- [ ] Golden Rules (`docs/golden-rules.md`) G1~G15 모두 준수
- [ ] G7: C++ legacy 변경 시 `legacy-cpp-touch` 라벨 + 사유 명시
- [ ] G13: 새 의존성은 `uv add`로만, `uv.lock` 동시 커밋
- [ ] G14: DB/스키마 영향 시 compat-check 결과 첨부
- [ ] 보호 경로 (`docs/sop/human-approval.md` §1) 변경 시 사람 승인 받음
- [ ] AGENTS.md / CLAUDE.md 본문에 정책 복붙 없음 (모두 docs/ 링크)
- [ ] 새 외부 의존성/시크릿 없음
- [ ] AUTHORS.txt에 본인 등재

## RULE_OVERRIDE (해당 시)

<!-- Golden Rule 우회가 필요했다면 docs/sop/human-approval.md §2 절차에 따라 명시. -->
