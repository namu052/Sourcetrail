# .claude/hooks/  (Sourcetrail_Remake / Python)

이 디렉터리는 **Claude Code 훅 초안 보관소**다. 실제 적용은 `~/.claude/settings.json`(글로벌) 또는 프로젝트 `.claude/settings.json`/`settings.local.json`에 등재해야 동작.

> **중요**: 적용은 사용자 승인 후. 글로벌 hook과 충돌할 수 있으니 `update-config` 스킬 권장.

## 권장 hook 초안

### PreToolUse — 위험 Bash 명령 차단 (G1, G3, G7, G13)

```jsonc
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "tool == \"Bash\"",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'cmd=\"$tool_input_command\"; for pat in \"rm -rf /\" \"git push --force\" \"git push -f\" \"git reset --hard\" \"git commit.*--no-verify\" \"git commit.*--amend\" \"sudo \" \"pip install\" \"pip3 install\" \"poetry \" \"pipenv \" \"conda \"; do if [[ \"$cmd\" =~ $pat ]]; then echo \"BLOCKED: $pat (see docs/golden-rules.md)\"; exit 1; fi; done'"
          }
        ]
      }
    ]
  }
}
```

### PreToolUse — 보호 경로 수정 차단 (`docs/sop/human-approval.md` §1)

```jsonc
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "tool == \"Edit\" || tool == \"Write\"",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'p=\"$tool_input_file_path\"; for pat in \"pyproject.toml\" \"uv.lock\" \".pre-commit-config.yaml\" \".github/CODEOWNERS\" \".github/workflows/\" \".claude/hooks/\" \".codex/config.\" \"docs/golden-rules.md\" \"docs/security.md\" \"docs/reliability.md\" \"docs/sop/human-approval.md\" \"docs/plan/\" \"CMakeLists.txt\" \"cmake/\" \"script/\" \".clang-format\" \".travis.yml\" \"appveyor.yml\" \"src/lib\" \"src/app/\" \"src/indexer/\" \"src/external/\" \"src/test/\" \"java_indexer/\" \"ide_plugins/\" \"bin/\" \"deployment/\" \"setup/\" \"testing/\" \"docs/documentation/\" \"docs/readme/\"; do if [[ \"$p\" == *\"$pat\"* ]]; then echo \"BLOCKED: protected path $pat (see docs/sop/human-approval.md)\"; exit 1; fi; done'"
          }
        ]
      }
    ]
  }
}
```

### PostToolUse — 편집 후 ruff format (G1)

```jsonc
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "(tool == \"Edit\" || tool == \"Write\") && tool_input_file_path =~ \"\\.py$\"",
        "hooks": [
          {
            "type": "command",
            "command": "bash -c 'if command -v uv >/dev/null 2>&1; then uv run ruff format \"$tool_input_file_path\" 2>/dev/null || true; fi'"
          }
        ]
      }
    ]
  }
}
```

### Stop — 세션 종료 시 미머지 plan 점검

```jsonc
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash scripts/docs-freshness.sh || true"
          }
        ]
      }
    ]
  }
}
```

## 적용 절차

1. 본 README의 초안을 검토.
2. `update-config` 스킬로 `~/.claude/settings.json` 또는 `.claude/settings.local.json`에 추가.
3. 글로벌 hook과 matcher 중복을 사용자가 검사.
4. 시범: 작은 변경으로 hook 동작 확인.
5. 본 README의 마지막 갱신일 변경.

## 주의

- hook 과잉은 작업을 방해 (`docs/failure-modes.md` 패턴 6).
- 위 hook은 **bash 가용** 가정. Windows에서 Git Bash 또는 WSL 필요.
- `uv run ruff format` PostToolUse hook은 Phase 0 D2에 `pyproject.toml`이 마련된 후 활성화 권장.
- 모든 hook 변경은 `docs/sop/human-approval.md` 절차.
