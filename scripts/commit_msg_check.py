#!/usr/bin/env python3
"""Simple commit-msg hook enforcing Conventional Commit style.

Matches: <type>(<scope>)?: <short description>
Type allowed: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert, const, tests
Subject is limited to 72 characters for readability.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERN = re.compile(
    r"^(?:feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert|const|tests)"
    r"(?:\([a-z0-9_\-]+\))?: .{1,72}$"
)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("[commit-msg-check] No commit message file provided", file=sys.stderr)
        return 1

    msg_file = Path(argv[1])
    try:
        content = msg_file.read_text(encoding="utf-8")
    except Exception as exc:
        print(f"[commit-msg-check] Failed to read commit message file: {exc}", file=sys.stderr)
        return 1

    # Use the first non-empty line as the subject
    for line in content.splitlines():
        subject = line.strip()
        if subject:
            break
    else:
        print("[commit-msg-check] Empty commit message", file=sys.stderr)
        return 1

    if not PATTERN.match(subject):
        print("\n[commit-msg-check] Invalid commit message subject:\n", file=sys.stderr)
        print(f"  {subject}\n", file=sys.stderr)
        print(
            "Expected format: <type>(<scope>)?: <short description>\n"
            "Allowed types: feat, fix, docs, style, refactor, perf, test, chore, ci, build, revert, const, tests\n"
            "Subject length: up to 72 characters",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
