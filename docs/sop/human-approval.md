# SOP — Human Approval

자동화의 마지막 안전망. 다음은 **에이전트 단독 실행 금지** — 사람 승인 후만.

## 1. 항상 사람 승인 필요한 변경

| 영역 | 이유 |
|---|---|
| `pyproject.toml`, `uv.lock` | 의존성 / 빌드 메타 변경. CI 깨짐/공급망 위험. |
| `.pre-commit-config.yaml` | hook 정책 |
| `.github/CODEOWNERS`, `.github/workflows/` | 게이트 자체 |
| `.claude/hooks/`, `.claude/settings.json` | 자동화 권한 |
| `.codex/config.*.toml` | 권한 / 샌드박스 |
| `docs/golden-rules.md` | 제일 강한 룰 |
| `docs/security.md`, `docs/reliability.md` | 정책 |
| `docs/sop/human-approval.md` | 본 문서 자체 |
| `docs/plan/**` | 대관 계획 — 변경은 ADR 필수 |
| 새 외부 의존성 (`uv add <pkg>`) | 라이선스/보안 |
| 1000+ LOC PR | 검토 가능성 / 롤백 비용 |
| **C++ legacy 영역** (`docs/references/architecture-rules.md` §7) | G7 — 보존 결정 |
| 릴리스 태그 / `git push --tags` | 사용자 영향 직결 |
| `compat-check.sh` 결과 무시한 머지 시도 | G14 위반 — 어떤 경우에도 차단 |

## 2. RULE_OVERRIDE 절차

Golden Rule을 일시 우회해야 할 때:

1. PR 본문에 `RULE_OVERRIDE: G<n> — <한 문장 사유>` 명시.
2. 영향 분석 + 롤백 계획 첨부.
3. maintainer 1명 이상 명시적 승인.
4. 24시간 내 회고 plan을 `docs/exec-plans/active/`에 작성.
5. (G14의 경우) **항상 maintainer 2명 + 명시적 사용자 영향 분석** — DB 호환은 약속.

## 3. 에스컬레이션

| 상황 | 누구에게 | 어떻게 |
|---|---|---|
| 시크릿 노출 의심 | maintainer 즉시 | PR 코멘트 + 별도 채널 |
| 마스터 빌드 깨짐 24h+ | maintainer | issue + 라벨 `master-broken` |
| 보안 취약점 (외부 보고) | security 담당 | 비공개 채널 (private fork / email) |
| 위험 명령 자동 실행됨 | maintainer | 즉시 + 로그 첨부 |
| C++ legacy 무단 변경 발견 | maintainer | revert PR + 회고 |
| compat-check 실패 release 시도 | maintainer | 즉시 중단 |

## 4. 승인 체크리스트 (사람용)

PR 머지 전:

- [ ] CI green (`harness-gate`, `ci`)
- [ ] `docs/quality-score.md` ≥ 임계
- [ ] golden rule 위반 없음
- [ ] 매칭되는 `docs/exec-plans/active/` plan 존재 (1000+ LOC면 필수)
- [ ] revert 가능한 단일 단위 (squash로 정리)
- [ ] 새 외부 의존성/시크릿 없음
- [ ] DB/스키마 영향 변경이면 `compat-check.sh` 결과 첨부
- [ ] C++ legacy 변경이면 `legacy-cpp-touch` 라벨 + 사유 OK
- [ ] (해당 시) `docs/plan/` 변경에 ADR (`docs/design-docs/`) 첨부

## 5. 자동화 가능성

| 항목 | 자동화 |
|---|---|
| 사람 승인 필요 경로 변경 감지 | `.github/CODEOWNERS` + `scripts/structure-check.sh` warn |
| Golden rule 위반 라벨 | CI |
| 1000+ LOC 라벨 | CI (`harness-gate.yml`) |
| 마스터 깨짐 알림 | (TBD, GitHub status check) |
| compat-check 실패 PR 차단 | CI gate |
