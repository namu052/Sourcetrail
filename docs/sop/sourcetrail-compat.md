# SOP — SourcetrailDB 100% 호환 (G14)

Sourcetrail_Remake가 생성하는 `.srctrldb`는 **원본 Sourcetrail Windows GUI에서 에러 없이 열림**이 핵심 약속이다. 본 SOP는 이를 매 phase, 매 release에서 검증한다.

> 기술 배경은 [`docs/plan/02-architecture.md` §5](../plan/02-architecture.md), 위험 R-02는 [`docs/plan/03-risks.md`](../plan/03-risks.md).

## 1. 원칙

| # | 원칙 |
|---|---|
| 1 | **원본 스키마 미훼손**. `node`, `edge`, `symbol`, `file`, `source_location`, `occurrence`, `local_symbol`, `component_access`, `error`, `node_file`, `meta` 테이블의 컬럼/제약 변경 금지. |
| 2 | **enum 1:1 매핑**. `node_type`, `edge_type`, `symbol_definition_kind`, `source_location_type`, `access_kind`는 원본 C++ 헤더와 1:1. 추가/제거 금지. |
| 3 | **Python 특화는 확장 테이블**. `edge_extension`, `node_extension`만 사용. |
| 4 | **자동 검증**. 매 PR (DB/스키마 영향 시) + 매 phase 종료 + 매 release. |
| 5 | **사고 발생 시 즉시 release 보류**. G14는 점수와 무관하게 머지 차단. |

## 2. 확장 테이블

```sql
CREATE TABLE IF NOT EXISTS edge_extension (
    edge_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY (edge_id) REFERENCES edge(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_edge_extension_edge_id ON edge_extension(edge_id);

CREATE TABLE IF NOT EXISTS node_extension (
    node_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    confidence REAL,
    metadata TEXT,
    FOREIGN KEY (node_id) REFERENCES node(id) ON DELETE CASCADE
);
```

`kind` 값 카탈로그 (확장 시 본 문서 갱신):

| kind | 의미 | 원본 매핑 |
|---|---|---|
| `django_fk` | Django ForeignKey | `edge_type = USAGE` |
| `django_m2m` | Django ManyToManyField | `edge_type = USAGE` |
| `flask_route` | `@app.route` | `edge_type = CALL` |
| `fastapi_route` | `@app.get/post` | `edge_type = CALL` |
| `sqlalchemy_relationship` | `relationship()` | `edge_type = USAGE` |
| `dynamic_import` | `importlib.import_module` 정적 탐지 | `edge_type = IMPORT` |
| `duck_candidate` | duck typing 후보 | `edge_type = USAGE` |
| `unsolved` | 해결 못한 참조 | `edge_type = USAGE` 또는 미생성 |
| `jupyter_cell` | `.ipynb` 셀 노드 | `node_type = MODULE` 변형 |

## 3. 검증 절차

### 3.1 자동 (CI)

```bash
bash scripts/compat-check.sh tests/fixtures/<sample>/
```

내부적으로 (`scripts/compat_check_impl.py`, Phase 0 D8 PoC 1에 첫 구현):

1. fixture 인덱싱 → `.srctrldb` 생성.
2. SQLite 스키마를 원본 v25와 비교 (테이블/컬럼/제약).
3. (가능하면) 원본 Sourcetrail CLI 또는 GUI headless로 DB 로드 시도.
4. 노드/엣지 카운트 무결성.
5. 리포트: pass/fail + diff.

### 3.2 매 phase 종료 (수동)

- 5종 fixture 모두에 `compat-check.sh` 실행:
  - `tests/fixtures/sample-minimal/` (100줄)
  - `tests/fixtures/sample-django/` (Phase 4)
  - `tests/fixtures/sample-flask/` (Phase 4)
  - `tests/fixtures/sample-fastapi/` (Phase 4)
  - `tests/fixtures/sample-jupyter/` (Phase 4)
- 결과를 `docs/exec-plans/completed/phase-N-retro.md`에 첨부.

### 3.3 매 release (수동)

- 위 §3.2 + **실제 Windows VM**에서 원본 Sourcetrail GUI로 열기.
- 그래프 렌더링 정상, 노드 클릭 정상.

## 4. 위반 시 (사고)

1. release 즉시 보류.
2. `tech-debt-tracker.md`에 S1으로 등재.
3. `docs/exec-plans/active/`에 `compat-fix-<date>.md` 즉시 작성.
4. 원인이 본 SOP의 어느 원칙 위반인지 명시.
5. RULE_OVERRIDE는 G14에 한해 maintainer 2명 + 사용자 영향 분석 + (가능하면) 외부 자문.

## 5. 책임

- 인덱서 변경 PR 작성자: PR 본문에 compat 영향 명시.
- maintainer: §3.3 매 release 수행.
- (TBD) 자동화 담당: 일간 nightly compat 회귀 잡 (Phase 1+).
