"""
Extract Meta Developer docs (DMC = Developer Meta Components) page content
to Markdown.

The article content is embedded inside the page HTML as a JSON-encoded React
tree. This script:

  1. Locates the encoded tree in the HTML.
  2. Decodes it (it's a JSON string containing JSON).
  3. Walks the tree recursively, emitting Markdown for each node type.

Run:
    python extract_dmc.py <input.html> <output.md> [--url <source-url>]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# --- Step 1: pull the inner content tree out of the page HTML --------------


# The page contains many script blobs. The article content sits inside one
# whose payload has the shape:
#
#     ...,"content":"<JSON-encoded-React-tree>","js_dependencies":[...
#
# The React tree, once decoded, is a JSON document whose top-level type is
# usually "Fragment" and whose children are DMCCommonH1 / DocumentHeading /
# DMCCommonP / etc. We search for "content":"<...>" pairs and decode each
# candidate; the right one is the one that decodes to a JSON object/array
# whose serialized form contains "DMCCommonP" or "DocumentHeading" or
# "DMCCommonH1".


CONTENT_KEYS = ('"json_cms_content":"', '"content":"')


def find_content_blobs(html: str) -> list[str]:
    """Return every JSON string assigned to a content-bearing key.

    Walks the HTML character by character so escaped quotes (``\\"``)
    inside the JSON string don't terminate it early.
    """
    out: list[str] = []
    n = len(html)
    for needle in CONTENT_KEYS:
        i = 0
        while True:
            j = html.find(needle, i)
            if j < 0:
                break
            start = j + len(needle)
            # Walk forward looking for an unescaped closing quote.
            k = start
            found_close = False
            while k < n:
                c = html[k]
                if c == "\\":
                    k += 2  # skip the escaped char
                    continue
                if c == '"':
                    out.append(html[start:k])
                    i = k + 1
                    found_close = True
                    break
                k += 1
            if not found_close:
                break
    return out


def find_article_tree(html: str) -> Any:
    """Return the decoded React tree that holds the article body."""
    candidates = find_content_blobs(html)
    best: Any = None
    best_score = -1
    for raw in candidates:
        # raw is the *inner* JSON string. To decode it, wrap it back in
        # quotes and let json.loads handle the escapes.
        try:
            decoded = json.loads('"' + raw + '"')
        except json.JSONDecodeError:
            continue
        # decoded is now itself a JSON document — parse again.
        try:
            tree = json.loads(decoded)
        except json.JSONDecodeError:
            continue
        # Score: more DMC/Developer node mentions = more likely the real one.
        ser = json.dumps(tree)
        score = (
            ser.count("DMCCommonP")
            + ser.count("DMCCommonH1")
            + ser.count("DocumentHeading")
            + ser.count("DeveloperPre")
            + ser.count("DeveloperDMCDocsH")
        )
        if score > best_score:
            best_score = score
            best = tree
    if best is None or best_score == 0:
        raise RuntimeError("No DMC article tree found in HTML")
    return best


# --- Step 2: walk the tree and emit Markdown ------------------------------


# Each node is either:
#   - a plain string (leaf text), or
#   - a dict with keys: "type", "props", "children" (and others we ignore).
#
# `children` can be missing, a single value, or a list. We normalize that.


_UNKNOWN_TYPES: set[str] = set()


INLINE_TYPES = {
    "DMCCommonStrong": ("**", "**"),
    "DeveloperStrong": ("**", "**"),
    "DMCCommonB": ("**", "**"),
    "DMCCommonEm": ("*", "*"),
    "DMCCommonI": ("*", "*"),
    "DMCCommonU": ("", ""),  # underline -> no Markdown equivalent, keep text
    "DMCCommonSup": ("<sup>", "</sup>"),
    "DMCCommonSub": ("<sub>", "</sub>"),
    "DMCCommonDel": ("~~", "~~"),
    "DMCCommonS": ("~~", "~~"),
    "DMCCommonSmall": ("", ""),
    "DMCCommonBr": ("", ""),  # handled specially as a newline
}


def _children(node: dict) -> list:
    c = node.get("children")
    if c is None:
        return []
    if isinstance(c, list):
        return c
    return [c]


def _props(node: dict) -> dict:
    p = node.get("props") or {}
    return p if isinstance(p, dict) else {}


def render_inline(node: Any) -> str:
    """Render an inline node (string or inline element) to Markdown text."""
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""
    t = node.get("type", "")
    props = _props(node)
    kids = _children(node)

    if t == "DMCCommonBr":
        return "  \n"

    if t in ("DMCCommonA", "DeveloperA"):
        text = "".join(render_inline(c) for c in kids).strip()
        href = props.get("href", "")
        if not text:
            text = href
        return f"[{text}]({href})" if href else text

    if t == "DeveloperCode":
        # Inline `code` *or* code-block content (when nested inside DeveloperPre,
        # the block handler intercepts before we get here).
        text = "".join(_flatten_text(c) for c in kids)
        return f"`{text}`"

    if t == "DMCCommonImg" or t == "DeveloperImg":
        src = props.get("src", "")
        alt = props.get("alt", "")
        return f"![{alt}]({src})"

    if t in INLINE_TYPES:
        open_, close = INLINE_TYPES[t]
        return open_ + "".join(render_inline(c) for c in kids) + close

    if t == "Fragment" or t == "":
        return "".join(render_inline(c) for c in kids)

    # Unknown inline-ish type: fall back to its text content.
    return "".join(render_inline(c) for c in kids)


def _flatten_text(node: Any) -> str:
    """Concatenate every string leaf under `node` with no markup."""
    if isinstance(node, str):
        return node
    if not isinstance(node, dict):
        return ""
    return "".join(_flatten_text(c) for c in _children(node))


def render_block(node: Any, depth: int = 0) -> str:
    """Render a block-level node to Markdown."""
    if isinstance(node, str):
        s = node.strip()
        return s + "\n\n" if s else ""
    if not isinstance(node, dict):
        return ""
    t = node.get("type", "")
    props = _props(node)
    kids = _children(node)

    # --- Headings ---
    if t == "DMCCommonH1":
        return "# " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t == "DocumentHeading":
        # `props.level` (1..6) controls the heading level.
        level = int(props.get("level", 2))
        level = max(1, min(level, 6))
        return "#" * level + " " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t == "DeveloperDMCDocsH2":
        return "## " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t == "DeveloperDMCDocsH3":
        return "### " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t == "DeveloperDMCDocsH4":
        return "#### " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t in ("DMCCommonH2",):
        return "## " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t in ("DMCCommonH3",):
        return "### " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t in ("DMCCommonH4",):
        return "#### " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t in ("DMCCommonH5",):
        return "##### " + "".join(render_inline(c) for c in kids).strip() + "\n\n"
    if t in ("DMCCommonH6",):
        return "###### " + "".join(render_inline(c) for c in kids).strip() + "\n\n"

    # --- Paragraph ---
    if t == "DMCCommonP":
        text = "".join(render_inline(c) for c in kids).strip()
        return text + "\n\n" if text else ""

    # --- Lists ---
    if t in ("DMCCommonUl", "DMCCommonOl"):
        return _render_list(node, ordered=(t == "DMCCommonOl"), depth=depth)
    if t == "DMCCommonLi":
        # Standalone Li (shouldn't usually happen; lists handle their own Li).
        return _render_list_item(node, "- ", depth)

    # --- Code blocks ---
    if t == "DeveloperPre":
        return _render_code_block(node)

    # --- Tables ---
    if t in ("DMCCommonTable", "DeveloperTable"):
        return _render_table(node) + "\n\n"

    # --- Blockquote / callout-ish containers we just unwrap ---
    if t == "DMCCommonBlockquote":
        inner = "".join(render_block(c, depth) for c in kids).strip()
        return "\n".join("> " + ln for ln in inner.splitlines()) + "\n\n"

    # --- Images standing alone ---
    if t in ("DMCCommonImg", "DeveloperImg"):
        return render_inline(node) + "\n\n"

    # --- Horizontal rule ---
    if t == "DMCCommonHr":
        return "\n---\n\n"

    # --- Generic container: render children as blocks ---
    if t in (
        "Fragment",
        "",
        "DeveloperDocsBody",
        "DMCCommonDiv",
        "DeveloperDiv",
        "DeveloperSection",
        "DMCCommonSection",
        "DeveloperContent",
        "DocumentBody",
        "DMCCommonArticle",
        "DeveloperArticle",
        # Card/grid containers used on index/listing pages: just unwrap so
        # whatever heading/text/link they contain still appears.
        "DMCCardGrid",
        "DMCCard",
        "DeveloperCard",
        "DeveloperDocsCard",
        "DeveloperDocsCardGrid",
        "DocsCard",
        "DocsCardGrid",
        "DMCCardLink",
        "DeveloperCardLink",
        "DocsCardLink",
        "DocsLinkCard",
        "DMCDocsCardLink",
        "DMCDocsLinkCard",
        "DocsLinkCardGroup",
        "DocsLinkCardGrid",
    ):
        return "".join(render_block(c, depth) for c in kids)

    # --- "Last updated" widget and similar metadata: skip silently ---
    if t in (
        "DMCUiDocsLastUpdated",
        "DeveloperDocsLastUpdated",
        "DMCUiDocsFeedback",
        "DeveloperDocsBreadcrumb",
        "DMCSideNav",
        "DeveloperSideNav",
        "DMCSidebarNav",
    ):
        return ""

    # --- Video / iframe embeds: emit a link with the src URL ---
    if t in ("DMCCommonIframe", "DeveloperIframe", "DMCCommonVideo", "DeveloperVideo"):
        src = props.get("src") or props.get("data-src") or ""
        if src:
            return f"[Embedded video/iframe: {src}]({src})\n\n"
        return ""

    # --- Note/callout component used inline in docs ---
    if t in ("DMCuiNote", "DeveloperNote", "DMCNote", "DeveloperDocsNote"):
        kind = props.get("kind") or props.get("type") or "Note"
        inner = "".join(render_block(c, depth) for c in kids).strip()
        if not inner:
            inner = "".join(render_inline(c) for c in kids).strip()
        prefixed = "\n".join("> " + ln if ln else ">" for ln in inner.splitlines())
        return f"> **{kind}**\n{prefixed}\n\n"

    # --- Bare table cell encountered outside a table walker: render its
    # children (this happens because _render_table calls render_block on cell
    # nodes and the recursion hits the cell type itself first).
    if t in ("DMCCommonTd", "DMCCommonTh", "DeveloperTd", "DeveloperTh"):
        return "".join(render_block(c, depth) for c in kids)

    # --- Callout / note / warning boxes ---
    if t in (
        "DeveloperCallout",
        "DMCCallout",
        "DeveloperNote",
        "DMCNote",
        "DeveloperWarning",
        "DeveloperTip",
    ):
        kind = props.get("kind") or props.get("variant") or t.replace("Developer", "").replace("DMC", "")
        inner = "".join(render_block(c, depth) for c in kids).strip()
        prefixed = "\n".join("> " + ln if ln else ">" for ln in inner.splitlines())
        return f"> **{kind}**\n{prefixed}\n\n"

    # --- Unknown block: try inline fallback, otherwise recurse into children ---
    _UNKNOWN_TYPES.add(t)
    if kids:
        return "".join(render_block(c, depth) for c in kids)
    text = render_inline(node).strip()
    return text + "\n\n" if text else ""


def _render_list(node: dict, ordered: bool, depth: int) -> str:
    out_lines: list[str] = []
    counter = 1
    for child in _children(node):
        if isinstance(child, dict) and child.get("type") == "DMCCommonLi":
            marker = f"{counter}. " if ordered else "- "
            out_lines.append(_render_list_item(child, marker, depth))
            counter += 1
        else:
            # Unexpected non-Li child: render it indented inline.
            text = render_inline(child).strip()
            if text:
                out_lines.append("  " * depth + text)
    return "".join(out_lines) + "\n"


def _render_list_item(li_node: dict, marker: str, depth: int) -> str:
    """Render an Li, handling nested block content (paragraphs, nested lists).

    The first chunk of textual content -- whether it comes from inline children
    or from an initial nested ``DMCCommonP`` block -- is placed on the same
    line as the bullet marker so the list stays numbered/bulleted correctly.
    Subsequent blocks (nested lists, code blocks, additional paragraphs) are
    indented under the marker as continuation content.
    """
    indent = "  " * depth
    parts: list[str] = []
    inline_buf: list[str] = []
    marker_used = False  # has the bullet marker been emitted yet?

    def flush_inline() -> None:
        nonlocal marker_used
        text = "".join(inline_buf).strip()
        inline_buf.clear()
        if not text:
            return
        if not marker_used:
            parts.append(f"{indent}{marker}{text}\n")
            marker_used = True
        else:
            parts.append(f"{indent}  {text}\n")

    BLOCK_CHILD_TYPES = (
        "DMCCommonUl",
        "DMCCommonOl",
        "DMCCommonP",
        "DeveloperPre",
        "DMCCommonTable",
        "DocumentHeading",
        "DMCCommonH1",
        "DMCCommonH2",
        "DMCCommonH3",
        "DMCCommonH4",
        "DeveloperDMCDocsH2",
        "DeveloperDMCDocsH3",
    )

    children = _children(li_node)
    for c in children:
        if isinstance(c, dict) and c.get("type") in BLOCK_CHILD_TYPES:
            flush_inline()
            t = c.get("type")
            if not marker_used and t == "DMCCommonP":
                # The very first block in this Li is a paragraph: hoist its
                # text onto the marker line instead of indenting it below.
                text = "".join(render_inline(k) for k in _children(c)).strip()
                if text:
                    parts.append(f"{indent}{marker}{text}\n")
                    marker_used = True
                continue
            block_md = render_block(c, depth + 1)
            indented_lines = []
            for ln in block_md.splitlines():
                if ln.strip():
                    indented_lines.append(indent + "  " + ln)
                else:
                    indented_lines.append("")
            if not marker_used:
                # Hoist the first non-empty line up onto the marker line.
                while indented_lines and not indented_lines[0].strip():
                    indented_lines.pop(0)
                if indented_lines:
                    first = indented_lines.pop(0).lstrip()
                    parts.append(f"{indent}{marker}{first}\n")
                    marker_used = True
            parts.append("\n".join(indented_lines).rstrip() + "\n")
        else:
            inline_buf.append(render_inline(c))
    flush_inline()
    if not marker_used:
        parts.append(f"{indent}{marker}\n")
    return "".join(parts)


def _render_code_block(pre_node: dict) -> str:
    """Render a <pre><code> block. Detect the language from the inner code node."""
    lang = ""
    text = ""
    for c in _children(pre_node):
        if isinstance(c, dict) and c.get("type") == "DeveloperCode":
            cprops = _props(c)
            cls = cprops.get("class") or cprops.get("className") or ""
            m = re.search(r"language-([\w-]+)", cls)
            if m:
                lang = m.group(1)
            text = "".join(_flatten_text(k) for k in _children(c))
            break
    if not text:
        text = "".join(_flatten_text(c) for c in _children(pre_node))
    text = text.rstrip("\n")
    return f"```{lang}\n{text}\n```\n\n"


def _render_table(table_node: dict) -> str:
    """Render a DMC/Developer table to a GFM Markdown table."""
    rows: list[list[str]] = []
    header_row_count = 0

    def walk(n: Any, in_head: bool = False) -> None:
        nonlocal header_row_count
        if not isinstance(n, dict):
            return
        t = n.get("type", "")
        if t in ("DMCCommonThead", "DeveloperThead"):
            for c in _children(n):
                walk(c, in_head=True)
            return
        if t in ("DMCCommonTbody", "DeveloperTbody"):
            for c in _children(n):
                walk(c, in_head=False)
            return
        if t in ("DMCCommonTr", "DeveloperTr"):
            cells: list[str] = []
            row_is_head = in_head
            for c in _children(n):
                if isinstance(c, dict) and c.get("type") in (
                    "DMCCommonTh",
                    "DeveloperTh",
                ):
                    row_is_head = True
                    cell = render_block(c).strip() or "".join(
                        render_inline(k) for k in _children(c)
                    ).strip()
                    cells.append(_md_cell(cell))
                elif isinstance(c, dict) and c.get("type") in (
                    "DMCCommonTd",
                    "DeveloperTd",
                ):
                    cell = render_block(c).strip() or "".join(
                        render_inline(k) for k in _children(c)
                    ).strip()
                    cells.append(_md_cell(cell))
            if cells:
                rows.append(cells)
                if row_is_head:
                    header_row_count += 1
            return
        for c in _children(n):
            walk(c, in_head=in_head)

    walk(table_node)
    if not rows:
        return ""

    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]

    if header_row_count == 0:
        # Synthesize an empty header row so the table is valid GFM.
        header = [""] * width
        body = rows
    else:
        header = rows[0]
        body = rows[header_row_count:]

    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join(["---"] * width) + "|"]
    for r in body:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def _md_cell(text: str) -> str:
    """Sanitize a string for use as a single Markdown table cell."""
    return text.replace("\n", " ").replace("|", "\\|").strip()


# --- Step 3: glue --------------------------------------------------------


def extract_title(tree: Any) -> str:
    """Best-effort: find the first DMCCommonH1 in the tree."""
    if isinstance(tree, dict):
        if tree.get("type") == "DMCCommonH1":
            return "".join(render_inline(c) for c in _children(tree)).strip()
        for c in _children(tree):
            t = extract_title(c)
            if t:
                return t
    elif isinstance(tree, list):
        for c in tree:
            t = extract_title(c)
            if t:
                return t
    return ""


def cleanup_md(md: str) -> str:
    """Collapse runs of blank lines and trim trailing whitespace per line."""
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--url", default="")
    ap.add_argument("--title", default="")
    args = ap.parse_args()

    html = args.input.read_text(encoding="utf-8", errors="replace")
    tree = find_article_tree(html)
    body_md = render_block(tree)
    body_md = cleanup_md(body_md)

    title = args.title or extract_title(tree) or args.input.stem.replace("-", " ").title()

    header = f"# {title}\n\nSource: {args.url}\n\n" if args.url else f"# {title}\n\n"

    # Strip a leading duplicated H1 from the body if it matches the title.
    body_lines = body_md.splitlines()
    if body_lines and body_lines[0].startswith("# ") and body_lines[0][2:].strip() == title.strip():
        body_md = "\n".join(body_lines[1:]).lstrip()

    args.output.write_text(header + body_md, encoding="utf-8")
    print(f"WROTE {args.output} (size={args.output.stat().st_size} bytes, title={title!r})")
    if _UNKNOWN_TYPES:
        unhandled = sorted(t for t in _UNKNOWN_TYPES if t)
        if unhandled:
            print(f"  unhandled component types (fell through to default): {', '.join(unhandled)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
