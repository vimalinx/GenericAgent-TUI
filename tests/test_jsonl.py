"""Tests for JSONL read/append helpers (ga_tui.app).

The append helper now holds a process-internal lock per path plus an advisory
fcntl.flock for cross-process safety. These tests cover correctness, not
concurrency (a dedicated stress test covers that).
"""
from __future__ import annotations

import json
from pathlib import Path


from ga_tui.app import append_jsonl, read_jsonl


class TestAppendJsonl:
    def test_creates_parent_dirs(self, tmp_path: Path) -> None:
        path = tmp_path / "nested" / "deep" / "tasks.jsonl"
        append_jsonl(str(path), {"task_id": "t1"})
        assert path.exists()

    def test_appends_records(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.jsonl"
        append_jsonl(str(path), {"task_id": "t1"})
        append_jsonl(str(path), {"task_id": "t2"})
        rows = read_jsonl(str(path))
        assert [r["task_id"] for r in rows] == ["t1", "t2"]

    def test_unicode_payload(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.jsonl"
        append_jsonl(str(path), {"name": "枢衡", "emoji": "\N{ROCKET}"})
        rows = read_jsonl(str(path))
        assert rows[0]["name"] == "枢衡"

    def test_writes_valid_json_lines(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.jsonl"
        append_jsonl(str(path), {"a": 1})
        append_jsonl(str(path), {"b": 2})
        with open(path, encoding="utf-8") as fh:
            lines = [ln for ln in fh.read().splitlines() if ln.strip()]
        assert len(lines) == 2
        for line in lines:
            assert json.loads(line)  # no exception

    def test_overwrites_partial_not_possible(self, tmp_path: Path) -> None:
        # Append mode never truncates; an existing file keeps prior content.
        path = tmp_path / "tasks.jsonl"
        path.write_text('{"existing": true}\n', encoding="utf-8")
        append_jsonl(str(path), {"new": True})
        rows = read_jsonl(str(path))
        assert len(rows) == 2


class TestReadJsonl:
    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        assert read_jsonl(str(tmp_path / "nope.jsonl")) == []

    def test_skips_blank_lines(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.jsonl"
        path.write_text('{"a": 1}\n\n  \n{"b": 2}\n', encoding="utf-8")
        assert len(read_jsonl(str(path))) == 2

    def test_skips_corrupt_lines(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.jsonl"
        path.write_text('{"a": 1}\nBROKEN\n{"b": 2}\n', encoding="utf-8")
        rows = read_jsonl(str(path))
        assert len(rows) == 2
        assert rows[0]["a"] == 1

    def test_limit_returns_tail(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.jsonl"
        for i in range(10):
            append_jsonl(str(path), {"i": i})
        rows = read_jsonl(str(path), limit=3)
        assert [r["i"] for r in rows] == [7, 8, 9]

    def test_limit_zero_means_all(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.jsonl"
        for i in range(5):
            append_jsonl(str(path), {"i": i})
        assert len(read_jsonl(str(path), limit=0)) == 5

    def test_skips_non_dict_lines(self, tmp_path: Path) -> None:
        path = tmp_path / "tasks.jsonl"
        path.write_text('[1,2,3]\n"string"\n42\n{"ok": true}\n', encoding="utf-8")
        rows = read_jsonl(str(path))
        assert len(rows) == 1
        assert rows[0]["ok"] is True
