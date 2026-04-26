#!/usr/bin/env bash
# scripts/changed-files.sh — 변경 파일 목록 헬퍼
# 다른 게이트 스크립트가 source 또는 호출.
#
# 사용:
#   bash scripts/changed-files.sh              # origin/master...HEAD
#   bash scripts/changed-files.sh --staged     # 인덱스에 staged된 파일
#   bash scripts/changed-files.sh --since=ref  # ref 이후

set -euo pipefail

mode="${1:-}"

case "$mode" in
  --staged)
    git diff --cached --name-only --diff-filter=ACMRT
    ;;
  --since=*)
    ref="${mode#--since=}"
    git diff --name-only --diff-filter=ACMRT "$ref"...HEAD
    ;;
  ""|--default)
    base="origin/master"
    if ! git rev-parse --verify "$base" >/dev/null 2>&1; then
      base="HEAD~1"
    fi
    git diff --name-only --diff-filter=ACMRT "$base"...HEAD
    ;;
  *)
    echo "usage: $0 [--staged|--since=<ref>]" >&2
    exit 2
    ;;
esac
