# Reliability Policy

Sourcetrail_Remake는 **Windows 데스크톱 앱**이라 SaaS의 "프로덕션 장애"와 의미가 다르다. 본 정책은 사용자 머신에서의 신뢰성 + 개발 신뢰성을 모두 다룬다.

## 1. 빌드 / 테스트 신뢰성

- **마스터는 항상 green**. `harness-gate` + `ci` (Phase 0 D2+) 빨간 채로 머지 금지.
- 깨진 빌드 자동 복구: 에이전트 PR이 CI 실패 → `build-error-resolver` 에이전트가 즉시 수정 PR 시도 → 3회 실패 시 사람 에스컬레이션.

## 2. 테스트 신뢰성

- **Flaky 테스트는 격리**. 발견 즉시 `@pytest.mark.flaky` 또는 `@pytest.mark.skip` + `tech-debt-tracker.md`에 S2로 등재. 1주 내 root cause.
- pytest-qt fixture는 `qtbot.addWidget(w)` 강제 — 누락 시 다음 테스트 오염.
- 환경 의존(JDK, Maven 등 — 본 프로젝트엔 없지만 향후 mypy/pyright 외부 통합) 테스트는 `@pytest.mark.skipif(...)` 명시.

## 3. 런타임 신뢰성 (사용자 머신)

| 항목 | 정책 |
|---|---|
| 크래시 복구 | 세션 상태 자동 저장 (레이아웃, 열린 탭, 북마크 → `%APPDATA%/Sourcetrail_Remake/sessions/`). 크래시 후 재시작 시 복원 옵션 제공. |
| 인덱싱 중단 | "Cancel" 시 깨끗한 중단. 부분 DB는 무결성 유지 또는 자동 폐기. |
| 큰 프로젝트 메모리 | 10만+ LoC < 2GB. 초과 시 사용자에게 Shallow 모드 권장. |
| 백그라운드 스레드 예외 | EventBus로 UI에 전달 → 사용자에게 다이얼로그 + 로그 위치 안내. |
| OOM 방지 | 그래프 노드 1만 초과 시 LoD 자동, 슬라이더 제한 안내. |

## 4. 릴리스 신뢰성

- 릴리스 태그는 maintainer만 (branch protection).
- 릴리스 전 체크리스트:
  - [ ] CHANGELOG 갱신 (Phase 5 D? 자동화 검토).
  - [ ] `bin/app/data` 자산 변경 영향 — 본 프로젝트엔 없음, 사용자 데이터는 `%APPDATA%`.
  - [ ] Windows 10 + Windows 11 클린 머신 인스톨러 테스트 (`docs/observability.md` §5 시나리오 #10).
  - [ ] 알려진 회귀 없음.
  - [ ] `compat-check.sh`가 fixture 5종 모두 통과 (G14).
  - [ ] PyInstaller 바이너리 < 200MB.

## 5. 31주 리스크 게이트 (`docs/plan/03-risks.md`)

| Gate | 주차 | 체크 | 실패 시 |
|---|---|---|---|
| G1 | 2 | PoC 1 (Jedi → SourcetrailDB → 원본 GUI 열람) 성공? | Parso 단독 접근 재설계. |
| G2 | 8 | 10만 LoC 그래프 60fps? | LoD + 뷰포트 컬링 강화. |
| G3 | 16 | 자가 호스팅(dogfooding) 가능? | Phase 3로 보강 이월, MVP 배포 연기. |
| G4 | 22 | Smart Rename 회귀율 < 1%? | LibCST 기반 재작성 검토. |
| G5 | 28 | 타입 힌트 통합으로 unsolved 50% 감소? | mypy/pyright 강도 조정, UX 기대치 조정. |
| G6 | 31 | Windows VM에서 설치→실행→인덱싱 성공? | 릴리스 연기, 핫픽스. |

## 6. 에스컬레이션

```
issue 발견 ──▶ tech-debt-tracker.md 등재 ──▶ severity?
   ├─ S1 ──▶ maintainer 즉시 알림 + 다음 PR
   ├─ S2 ──▶ 분기 내 처리
   └─ S3 ──▶ 백로그
```

## 7. 자동화 가능성

| 항목 | 자동화 |
|---|---|
| 빌드 회귀 감지 | CI |
| Flaky 테스트 감지 | (TBD) `scripts/`에 nightly job |
| 릴리스 자산 무결성 | GitHub Actions release |
| 회귀 PR 자동 생성 | `build-error-resolver` (Claude) / Codex `--ask-for-approval=on-failure` |
| Bench 회귀 | `docs/generated/bench/` 시계열 + Phase 1+ 자동 |

## 8. 1인 풀타임 번아웃 (R-03 — Critical)

이 프로젝트의 #1 리스크는 기술이 아닌 **사람**.

- 주 40시간 상한 엄수. 주말 commit 금지 (drift-control이 commit 시간 분포 추적).
- 매 phase 종료 시 1~2일 버퍼.
- MVP(W16)까지 범위 축소 금지. 그 후는 유연 (Phase 3 이후 기능 이월 가능).
- 매주 금요일 30분 자기 회고 (drift control §1 일간 작업과 별개).
- Beta(W16) 공개 후 사용자 피드백으로 동기 부여.

## 9. 위반 시 조치

- 마스터 깨진 채 24h+ → maintainer 책임. 모든 비핵심 PR 동결.
- Flaky 테스트 1주 내 미처리 → S1 승격.
- compat-check 실패 release 시도 → 즉시 중단 + 회고.
