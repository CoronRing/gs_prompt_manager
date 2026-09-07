"""Render ``docs/assets/demo.svg``: an animated terminal cast of a real
``gs_prompt_manager`` session.

The output is a self-contained SVG whose lines fade in on a CSS timeline, so it
animates inside a plain ``<img>`` tag on GitHub and Read the Docs without a GIF
encoder or a JavaScript player. The transcript below is copied verbatim from a
live run against ``.agent_temp/demo``; re-run this script after changing the
public API so the recording keeps matching reality.

Usage::

    python src/human_tools/make_demo_svg.py
"""

from __future__ import annotations

import os
from typing import List, Sequence, Tuple

Segment = Tuple[str, str]
"""A run of terminal text and the fill colour it is drawn in."""

Line = Tuple[float, Sequence[Segment]]
"""A transcript line: the beat (seconds) it holds for, and its segments."""

# Terminal geometry. CHAR_W is the advance width the ``textLength`` hints are
# computed against, so glyph positions stay exact in any monospace fallback.
CHAR_W = 9.0
FONT_SIZE = 15
LINE_H = 26.0
PAD_X = 26.0
FIRST_BASELINE = 84.0
CHROME_H = 40.0
WIDTH = 760.0
TAIL_HOLD = 3.0
FADE = 0.30

# Palette: warm neutrals on dark brown, matching the logo and banner.
BG = "#160f0a"
CHROME = "#231710"
BORDER = "#3d2a1c"
TITLE = "#a08b7a"
PROMPT = "#f0883e"
CODE = "#f7f1ea"
OUT = "#cdbfb3"
VALUE = "#ffb86b"

TRANSCRIPT: List[Line] = [
    (1.20, [("$ ", PROMPT), ("pip install gs-prompt-manager", CODE)]),
    (0.20, []),
    (0.90, [("$ ", PROMPT), ("python", CODE)]),
    (1.00, [(">>> ", PROMPT), ("from gs_prompt_manager import PromptManager", CODE)]),
    (1.00, [(">>> ", PROMPT), ('m = PromptManager("./prompts")', CODE)]),
    (0.20, []),
    (0.90, [(">>> ", PROMPT), ("m.get_prompt_group_names()", CODE)]),
    (0.60, [("['Reviewer']", VALUE)]),
    (0.90, [(">>> ", PROMPT), ("m.Reviewer.get_prompt_names()", CODE)]),
    (0.90, [("['chat', 'verdict', 'system']", VALUE)]),
    (0.20, []),
    (1.10, [(">>> ", PROMPT), ('print(m.Reviewer.system({"language": "Rust"}))', CODE)]),
    (0.35, [("You are a senior Rust reviewer.", OUT)]),
    (0.35, [("Focus on correctness first, style last.", OUT)]),
    (1.00, [("Session started 2026-09-07 01:13:24.", OUT)]),
    (0.20, []),
    (1.00, [(">>> ", PROMPT), ("print(m.Reviewer.verdict())", CODE)]),
    (0.60, [("Answer with exactly one word: approve or reject.", OUT)]),
]

_ESCAPES = (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"))


def escape(text: str) -> str:
    """Escape the three characters that matter inside SVG text content."""
    for raw, encoded in _ESCAPES:
        text = text.replace(raw, encoded)
    return text


def render_line(segments: Sequence[Segment], index: int, baseline: float) -> str:
    """Render one transcript line as an SVG ``<text>`` element."""
    if not segments:
        return f'  <text class="m l{index}" y="{baseline}" xml:space="preserve"></text>'

    spans: List[str] = []
    x = PAD_X
    for text, colour in segments:
        length = len(text) * CHAR_W
        spans.append(
            f'<tspan x="{x}" fill="{colour}" textLength="{length}" '
            f'lengthAdjust="spacingAndGlyphs">{escape(text)}</tspan>'
        )
        x += length
    return (
        f'  <text class="m l{index}" y="{baseline}" xml:space="preserve">'
        + "".join(spans)
        + "</text>"
    )


def build() -> str:
    """Build the complete SVG document as a string."""
    total = sum(beat for beat, _ in TRANSCRIPT) + TAIL_HOLD
    cursor_baseline = FIRST_BASELINE + len(TRANSCRIPT) * LINE_H
    height = cursor_baseline + 40.0

    keyframes: List[str] = []
    lines: List[str] = []
    elapsed = 0.0

    for index, (beat, segments) in enumerate(TRANSCRIPT):
        start = elapsed / total * 100.0
        end = min((elapsed + FADE) / total * 100.0, 100.0)
        head = "0%" if index == 0 else f"0%,{start:.2f}%"
        keyframes.append(
            f"    @keyframes k{index}{{{head}{{opacity:0}}{end:.2f}%,100%{{opacity:1}}}}"
            f".l{index}{{opacity:0;animation:k{index} {total:.1f}s linear infinite}}"
        )
        lines.append(render_line(segments, index, FIRST_BASELINE + index * LINE_H))
        elapsed += beat

    cursor_start = elapsed / total * 100.0
    keyframes.append(
        f"    @keyframes blink{{0%,{cursor_start:.2f}%{{opacity:0}}"
        f"{min(cursor_start + 0.1, 100.0):.2f}%,100%{{opacity:1}}}}"
        f".cursor{{opacity:0;animation:blink {total:.1f}s steps(1) infinite}}"
    )

    label = (
        "Terminal recording: installing gs-prompt-manager, then a Python session "
        "where PromptManager discovers the Reviewer group and renders its system "
        "and verdict prompts"
    )

    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH:.0f} {height:.0f}" '
            f'width="{WIDTH:.0f}" height="{height:.0f}" role="img" aria-label="{label}">',
            "  <title>gs_prompt_manager in a Python session</title>",
            "  <defs><style>",
            '    .m { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, '
            'Consolas, "Liberation Mono", monospace; font-size: %dpx; }' % FONT_SIZE,
            '    .chrome { font-family: ui-sans-serif, -apple-system, "Segoe UI", '
            "Roboto, Helvetica, Arial, sans-serif; font-size: 13px; }",
            *keyframes,
            "  </style></defs>",
            "",
            f'  <rect width="{WIDTH:.0f}" height="{height:.0f}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
            f'  <path d="M0 {CHROME_H:.0f} V10 a10 10 0 0 1 10 -10 H{WIDTH - 10:.0f} '
            f'a10 10 0 0 1 10 10 V{CHROME_H:.0f} Z" fill="{CHROME}"/>',
            f'  <line x1="0" y1="{CHROME_H:.0f}" x2="{WIDTH:.0f}" y2="{CHROME_H:.0f}" stroke="{BORDER}"/>',
            '  <circle cx="22" cy="20" r="6" fill="#ff5f57"/>',
            '  <circle cx="42" cy="20" r="6" fill="#febc2e"/>',
            '  <circle cx="62" cy="20" r="6" fill="#28c840"/>',
            f'  <text class="chrome" x="{WIDTH / 2:.0f}" y="25" fill="{TITLE}" '
            'text-anchor="middle">python — ./prompts</text>',
            "",
            *lines,
            "",
            f'  <text class="m cursor" x="{PAD_X}" y="{cursor_baseline}" fill="{PROMPT}" '
            'xml:space="preserve">&gt;&gt;&gt; <tspan fill="%s">&#9608;</tspan></text>' % CODE,
            "</svg>",
            "",
        ]
    )


def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target = os.path.join(root, "docs", "assets", "demo.svg")
    with open(target, "w", encoding="utf-8") as handle:
        handle.write(build())
    print(f"wrote {target}")


if __name__ == "__main__":
    main()
