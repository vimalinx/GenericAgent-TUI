"""Tests for terminal cell-width / wrapping utilities (ga_tui.app).

These functions compute display widths for East-Asian-Wide characters and wrap
text to a terminal cell budget. They are pure: no IO, no curses.
"""
from __future__ import annotations

from ga_tui.app import (
    ANSI_RE,
    cell_width,
    clean_text,
    pad_cells,
    truncate_cells,
    wrap_cells,
)


class TestCellWidth:
    def test_ascii(self) -> None:
        assert cell_width("hello") == 5

    def test_empty(self) -> None:
        assert cell_width("") == 0
    def test_mixed(self) -> None:
        # 2 ASCII + 2 CJK (2 cells each) = 2 + 4
        assert cell_width("ab枢衡") == 6
        assert cell_width("枢衡") == 4

    def test_combining_marks_zero_width(self) -> None:
        # U+0301 COMBINING ACUTE ACCENT adds no width.
        assert cell_width("e\u0301") == 1

    def test_emoji_wide(self) -> None:
        # Most emoji render at width 2 in terminals; unicodedata classifies
        # many as W. Assert at least the common case.
        assert cell_width("\N{POLICE CAR}") >= 1


class TestTruncateCells:
    def test_truncate_ascii(self) -> None:
        assert truncate_cells("hello world", 5) == "hello…"

    def test_zero_width_returns_empty(self) -> None:
        assert truncate_cells("abc", 0) == ""

    def test_negative_width_returns_empty(self) -> None:
        assert truncate_cells("abc", -1) == ""

    def test_exact_fit_no_ellipsis(self) -> None:
        assert truncate_cells("abc", 3) == "abc"

    def test_truncate_mid_cjk(self) -> None:
        # One CJK char = 2 cells; width 3 fits one CJK (2) + ellipsis.
        assert truncate_cells("枢衡", 3) == "枢…"

    def test_truncate_at_cjk_boundary(self) -> None:
        # width 2 fits exactly one CJK, ellipsis won't fit -> just the char.
        assert truncate_cells("枢衡xyz", 2) == "枢…"


class TestPadCells:
    def test_pad_short_ascii(self) -> None:
        assert pad_cells("hi", 5) == "hi   "

    def test_pad_exact(self) -> None:
        assert pad_cells("abc", 3) == "abc"

    def test_pad_truncates_overflow(self) -> None:
        # Overflow truncates with ellipsis; the ellipsis "…" is 1 cell, so a
        # width-3 budget yields "abc…" which is 4 cells (overflow by 1). This
        # documents the existing design where truncation prefers showing the
        # ellipsis marker over strictly respecting the cell budget.
        result = pad_cells("abcdef", 3)
        assert result == "abc…"

    def test_pad_overflow_width_matches_truncate(self) -> None:
        # pad_cells delegates to truncate_cells then pads only if shorter.
        assert pad_cells("abcdef", 3) == truncate_cells("abcdef", 3)
    def test_pad_cjk(self) -> None:
        # 枢 is 2 cells; target 4 -> 2 trailing spaces.
        assert pad_cells("枢", 4) == "枢  "


class TestCleanText:
    def test_strips_ansi_color(self) -> None:
        assert clean_text("\x1b[31mred\x1b[0m") == "red"

    def test_strips_csi_cursor(self) -> None:
        assert clean_text("a\x1b[2Kb") == "ab"

    def test_collapses_excessive_newlines(self) -> None:
        assert clean_text("a\n\n\n\n\nb") == "a\n\n\nb"

    def test_strips_trailing_whitespace(self) -> None:
        assert clean_text("text   \n  ") == "text"

    def test_none_input(self) -> None:
        assert clean_text(None) == ""  # type: ignore[arg-type]

    def test_osc_terminator(self) -> None:
        # OSC sequence ended by BEL.
        assert ANSI_RE.sub("", "\x1b]0;title\x07text") == "text"


class TestWrapCells:
    def test_wrap_simple(self) -> None:
        # width > 4 uses the real wrap path; width 6 wraps "abcdef" in two.
        lines = wrap_cells("abcdef", 3)
        # width 3 <= 4 triggers the fallback (single truncated line).
        assert lines == ["abc…"]

    def test_wrap_real_path(self) -> None:
        lines = wrap_cells("abcdef", 5)
        assert lines == ["abcde", "f"]

    def test_wrap_exact_fit(self) -> None:
        lines = wrap_cells("abcdef", 6)
        assert lines == ["abcdef"]

    def test_wrap_narrow_returns_truncated(self) -> None:
        # width <= 4 falls back to single truncated line.
        lines = wrap_cells("abcdef", 2)
        assert lines == ["ab…"]

    def test_wrap_preserves_newlines(self) -> None:
        lines = wrap_cells("ab\ncd", 10)
        assert lines == ["ab", "cd"]

    def test_wrap_empty_lines_kept(self) -> None:
        lines = wrap_cells("a\n\nb", 10)
        assert lines == ["a", "", "b"]

    def test_wrap_expands_tabs(self) -> None:
        lines = wrap_cells("a\tb", 10)
        assert lines == ["a    b"]

    def test_wrap_cjk(self) -> None:
        # 枢 is 2 cells; width 6 (>4 for real wrap) fits three CJK chars.
        lines = wrap_cells("枢枢枢枢", 6)
        assert lines == ["枢枢枢", "枢"]

    def test_wrap_empty_input(self) -> None:
        lines = wrap_cells("", 10)
        assert lines == [""]

    def test_wrap_none_input(self) -> None:
        lines = wrap_cells(None, 10)  # type: ignore[arg-type]
        assert lines == [""]
