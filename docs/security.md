# Security Policy (Sourcetrail_Remake / Python / Windows)

| 정책 | 필요성 | 규칙 | 자동화 | 위반 시 조치 | Codex 추가사항 | Claude 추가사항 |
|---|---|---|---|---|---|---|
| **시크릿 금지 커밋** | 토큰/키 유출 즉시 사고. | API 키/토큰/비밀번호/코드 서명 키는 환경 변수 또는 `%APPDATA%`로만. 리포에는 `.env.example`만. | `scripts/structure-check.sh` + (권장) pre-commit `gitleaks`. | 차단 + 키 회전 + 사고 보고서. | `.codex/config.toml` `network_access = false` 기본. | PreToolUse hook으로 `Edit`/`Write`에 토큰 패턴 차단. |
| **샌드박스 기본 보수** | 임의 파일/네트워크 접근 폭발 반경. | 새 작업 시작 샌드박스는 read-only 또는 workspace-write. 전체 시스템 접근은 사람 승인. | Codex sandbox / Claude permissions. | 작업 중단 + 사람 권한 요청. | `.codex/config.conservative.toml` read-only 기본. | Claude permission `default` 유지, `acceptEdits` 자동 사용 금지. |
| **위험 명령 통제** | `rm -rf`, `git push --force`, `git reset --hard`, `pip install`, `sudo`는 사고 직결. | 항상 사람 승인 후. 자동 승인 금지. | shell allowlist (Codex), Bash deny (Claude hook). | 즉시 중단 + 로그. | `.codex/` deny 리스트에 위 명령 + `pip/poetry/pipenv/conda`. | hook으로 동일 차단. |
| **Windows 코드 서명** (Phase 5) | PyInstaller 바이너리 SmartScreen 오탐. | 가능하면 EV 코드 서명 인증서 사용. 인증서 키는 `%LOCALAPPDATA%`에만. | 빌드 스크립트 외부화. | 서명 실패 시 release 보류. | release 트리거 자동 금지. | 동일. |
| **Microsoft Defender 오탐 대응** | 서명 없는 바이너리 격리 위험. | Inno Setup 사용 (낮은 오탐), `--exclude` 최적화. 오탐 발생 시 Microsoft Submit-a-File. | release 후 모니터링 (이슈 수집). | hotfix release. | — | — |
| **사용자 데이터 접근 통제** | 사용자 코드는 민감 자산 (사내 IP). | 인덱싱 데이터는 사용자 지정 경로 또는 `%APPDATA%/Sourcetrail_Remake/projects/`. 외부 전송 0. | 코드 리뷰 + `scripts/structure-check.sh`의 `requests`/`httpx`/`urllib` import 검사 (있으면 warn — F22 venv 검사 외엔 외부 요청 금지). | PR 차단. | network_access=false 강제. | 동일. |
| **SQL 안전성** | SourcetrailDB 쿼리에서 SQL 인젝션. | 모든 쿼리 파라미터화. 문자열 연결 금지. | code review + `scripts/structure-check.sh` 휴리스틱 (f-string + execute). | PR 차단. | — | — |
| **경로 입력 검증** | 사용자 프로젝트 경로 탈출 공격. | `..` 정규화, `Path.resolve()`. relative 입력 금지. | `core/project.py`에서 검증 함수 강제 (Phase 0+). | 입력 거부. | — | — |
| **롤백 정책** | 머지 후 회귀 시 빠른 복구. | 모든 PR은 `git revert <sha>` 가능. 단일 squash commit + 작은 PR. | squash merge 권장. | 회귀 발견 즉시 revert PR + `docs/exec-plans/active/`에 회고. | — | — |
| **에스컬레이션** | 보안 의심 즉시 사람에게. | S1 부채(시크릿/빌드/보안)는 발견 즉시 maintainer 알림. | `docs/sop/human-approval.md` 절차. | — | Codex `--ask-for-approval` 강제. | Claude 작업 중단 + 사용자 텍스트 보고. |
| **문서 신선도** | 오래된 정책은 위험. | 분기 1회 검토. 사고 후 즉시 갱신. | `scripts/docs-freshness.sh` 90일 미갱신 경고. | 백로그 등재. | — | — |
| **감사 로그** | 누가 무엇을 언제. | commit 메시지 `<scope>: <title>` + Co-Authored-By. CI 결과 `docs/generated/`에 보존. | git history + CI 산출물. | — | Codex stderr 이력. | Claude transcript 사용자 책임. |
| **인간 승인 게이트** | 자동화의 마지막 안전망. | 다음은 항상 사람 승인: golden rule 변경, `pyproject.toml`/`uv.lock` 변경, 새 외부 의존성 (`uv add`), 새 hook, 1000+ LOC, C++ legacy 변경, `docs/plan/` 변경. | `.github/CODEOWNERS` + `harness-gate.yml`. | 머지 차단. | — | — |

## 시크릿 패턴 차단 (`scripts/structure-check.sh`)

```bash
PATTERNS='(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----)'
```

## Windows 특화

- `%APPDATA%/Sourcetrail_Remake/`에 사용자 데이터/로그 격리 (`docs/observability.md` §2).
- 인스톨러는 사용자 권한 설치 우선 (관리자 권한 요구 최소화).
- 파일 연관 `.srctrldb`는 사용자 동의 후만 등록.
