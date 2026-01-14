#!/usr/bin/env python3
"""Renumber numeric (defconst ...) IDs in a .per file sequentially.

By default prints the updated file to stdout. Use --in-place to rewrite.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path


DEFCONST_NUMERIC_RE = re.compile(
    r"^(?P<prefix>\s*\(defconst\s+)"
    r"(?P<name>[^\s()]+)"
    r"(?P<ws>\s+)"
    r"(?P<value>-?\d+)"
    r"(?P<suffix>\s*\)\s*(?:;.*)?\n?)$"
)


def renumber(text: str, start: int) -> tuple[str, list[tuple[str, int, int]]]:
    next_id = start
    out_lines: list[str] = []
    mapping: list[tuple[str, int, int]] = []

    for line in text.splitlines(keepends=True):
        match = DEFCONST_NUMERIC_RE.match(line)
        if not match:
            out_lines.append(line)
            continue

        name = match.group("name")
        old_value = int(match.group("value"))
        new_value = next_id
        next_id += 1

        out_lines.append(
            f"{match.group('prefix')}{name}{match.group('ws')}{new_value}{match.group('suffix')}"
        )
        mapping.append((name, old_value, new_value))

    return "".join(out_lines), mapping


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Renumber numeric defconst IDs sequentially (1,2,3,...)"
    )
    parser.add_argument("path", nargs="?", default="goal.per", help="File to update")
    parser.add_argument("--start", type=int, default=1, help="First ID to assign")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Rewrite the file in place (creates a .bak by default)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Do not create a .bak when using --in-place",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print a unified diff instead of the full rewritten file",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 0 if no changes needed; 1 if changes would be made",
    )
    parser.add_argument(
        "--print-map",
        action="store_true",
        help="Print name: old->new mapping to stderr",
    )

    args = parser.parse_args(argv)

    path = Path(args.path)
    original = path.read_text(encoding="utf-8")
    updated, mapping = renumber(original, start=args.start)

    if args.print_map:
        for name, old, new in mapping:
            print(f"{name}: {old} -> {new}", file=sys.stderr)

    changed = updated != original

    if args.check:
        return 1 if changed else 0

    if args.diff:
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=str(path),
            tofile=str(path),
        )
        sys.stdout.writelines(diff)
        return 0

    if args.in_place:
        if changed:
            if not args.no_backup:
                backup_path = path.with_suffix(path.suffix + ".bak")
                backup_path.write_text(original, encoding="utf-8")
            path.write_text(updated, encoding="utf-8")
        return 0

    sys.stdout.write(updated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
