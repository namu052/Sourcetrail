# SourcetrailDB Schema Notes

Phase 0에서 확인한 SourcetrailDB v25 스키마 요약이다. 기준 소스는:

- `src/lib/data/storage/sqlite/SqliteStorage.cpp`
- `src/lib/data/storage/sqlite/SqliteIndexStorage.cpp`
- `src/lib/data/NodeKind.h`
- `src/lib/data/graph/Edge.h`
- `src/lib/data/DefinitionKind.h`
- `src/lib/data/location/LocationType.h`
- `src/lib/data/parser/AccessKind.h`

## Storage Version

- `storage_version = 25`

## Core Tables

| Table | Columns |
|---|---|
| `meta` | `id`, `key`, `value` |
| `element` | `id` |
| `element_component` | `id`, `element_id`, `type`, `data` |
| `edge` | `id`, `type`, `source_node_id`, `target_node_id` |
| `node` | `id`, `type`, `serialized_name` |
| `symbol` | `id`, `definition_kind` |
| `file` | `id`, `path`, `language`, `modification_time`, `indexed`, `complete`, `line_count` |
| `filecontent` | `id`, `content` |
| `local_symbol` | `id`, `name` |
| `source_location` | `id`, `file_node_id`, `start_line`, `start_column`, `end_line`, `end_column`, `type` |
| `occurrence` | `element_id`, `source_location_id` |
| `component_access` | `node_id`, `type` |
| `error` | `id`, `message`, `fatal`, `indexed`, `translation_unit` |

## Notes

- 계획 문서의 초기 초안에는 `node_file`가 언급되지만, 현재 C++ 저장소 구현에서 확인한 v25 schema 생성 코드는 `node_file` 대신 `file`, `filecontent`, `source_location.file_node_id`, `element_component`를 사용한다.
- `edge`, `node`, `symbol`, `file`, `local_symbol`, `error` 등은 모두 `element`/`node`에 foreign key를 건다.

## Enum Values

### `node.type` (`NodeKind`)

| Name | Value |
|---|---:|
| `NODE_SYMBOL` | 1 |
| `NODE_TYPE` | 2 |
| `NODE_BUILTIN_TYPE` | 4 |
| `NODE_MODULE` | 8 |
| `NODE_NAMESPACE` | 16 |
| `NODE_PACKAGE` | 32 |
| `NODE_STRUCT` | 64 |
| `NODE_CLASS` | 128 |
| `NODE_INTERFACE` | 256 |
| `NODE_ANNOTATION` | 512 |
| `NODE_GLOBAL_VARIABLE` | 1024 |
| `NODE_FIELD` | 2048 |
| `NODE_FUNCTION` | 4096 |
| `NODE_METHOD` | 8192 |
| `NODE_ENUM` | 16384 |
| `NODE_ENUM_CONSTANT` | 32768 |
| `NODE_TYPEDEF` | 65536 |
| `NODE_TYPE_PARAMETER` | 131072 |
| `NODE_FILE` | 262144 |
| `NODE_MACRO` | 524288 |
| `NODE_UNION` | 1048576 |

### `edge.type` (`EdgeType`)

| Name | Value |
|---|---:|
| `EDGE_UNDEFINED` | 0 |
| `EDGE_MEMBER` | 1 |
| `EDGE_TYPE_USAGE` | 2 |
| `EDGE_USAGE` | 4 |
| `EDGE_CALL` | 8 |
| `EDGE_INHERITANCE` | 16 |
| `EDGE_OVERRIDE` | 32 |
| `EDGE_TYPE_ARGUMENT` | 64 |
| `EDGE_TEMPLATE_SPECIALIZATION` | 128 |
| `EDGE_INCLUDE` | 256 |
| `EDGE_IMPORT` | 512 |
| `EDGE_BUNDLED_EDGES` | 1024 |
| `EDGE_MACRO_USAGE` | 2048 |
| `EDGE_ANNOTATION_USAGE` | 4096 |

### `symbol.definition_kind` (`DefinitionKind`)

| Name | Value |
|---|---:|
| `DEFINITION_NONE` | 0 |
| `DEFINITION_IMPLICIT` | 1 |
| `DEFINITION_EXPLICIT` | 2 |

### `source_location.type` (`LocationType`)

| Name | Value |
|---|---:|
| `LOCATION_TOKEN` | 0 |
| `LOCATION_SCOPE` | 1 |
| `LOCATION_QUALIFIER` | 2 |
| `LOCATION_LOCAL_SYMBOL` | 3 |
| `LOCATION_SIGNATURE` | 4 |
| `LOCATION_COMMENT` | 5 |
| `LOCATION_ERROR` | 6 |
| `LOCATION_FULLTEXT_SEARCH` | 7 |
| `LOCATION_SCREEN_SEARCH` | 8 |
| `LOCATION_UNSOLVED` | 9 |

### `component_access.type` (`AccessKind`)

| Name | Value |
|---|---:|
| `ACCESS_NONE` | 0 |
| `ACCESS_PUBLIC` | 1 |
| `ACCESS_PROTECTED` | 2 |
| `ACCESS_PRIVATE` | 3 |
| `ACCESS_DEFAULT` | 4 |
| `ACCESS_TEMPLATE_PARAMETER` | 5 |
| `ACCESS_TYPE_PARAMETER` | 6 |

## Python Extension Tables

원본 스키마를 훼손하지 않고 추가해야 하는 Phase 4용 확장 테이블:

```sql
CREATE TABLE IF NOT EXISTS edge_extension(
    edge_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    metadata TEXT,
    FOREIGN KEY(edge_id) REFERENCES edge(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS node_extension(
    node_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    confidence REAL,
    metadata TEXT,
    FOREIGN KEY(node_id) REFERENCES node(id) ON DELETE CASCADE
);
```

## Phase 0 Status

- 원본 C++ 생성 SQL 기준으로 core table/enum은 문서화했다.
- 원본 GUI 열람 검증은 별도 Windows Sourcetrail binary가 필요하다.

