"""Convert Wayback-archived Meta WhatsApp Flows reference HTML to clean Markdown.

The pages have a consistent layout: an <h1> followed by article content
inside a series of nested divs, ending before a feedback section.
We grab everything from <h1> onward (excluding feedback / footer) and
convert to Markdown via html2text after stripping Wayback rewrites and
non-content sidebars.
"""
from __future__ import annotations

import sys
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
import html2text


REF_DIR = Path(__file__).resolve().parent.parent / "docs" / "reference"


# Map raw-html filename -> (output md filename, page title, source url)
PAGES = {
    "_index_wayback.html": (
        "index.md",
        "WhatsApp Flows Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference",
    ),
    "_components_wayback.html": (
        "components.md",
        "WhatsApp Flows Components Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/components",
    ),
    "_error_codes_wayback.html": (
        "error-codes.md",
        "WhatsApp Flows Error Codes Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/error-codes",
    ),
    "_flowjson_wayback.html": (
        "flow-json.md",
        "WhatsApp Flows Flow JSON Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/flowjson",
    ),
    "_flowsapi_wayback.html": (
        "flows-api.md",
        "WhatsApp Flows API Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/flowsapi",
    ),
    "_lifecycle_wayback.html": (
        "lifecycle.md",
        "WhatsApp Flows Lifecycle Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/lifecycle",
    ),
    "_media_upload_wayback.html": (
        "media-upload.md",
        "WhatsApp Flows Media Upload Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/media_upload",
    ),
    "_metrics_wayback.html": (
        "metrics-api.md",
        "WhatsApp Flows Metrics API Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/metrics_api",
    ),
    "_versioning_wayback.html": (
        "versioning.md",
        "WhatsApp Flows Versioning Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/versioning",
    ),
    "_webhooks_wayback.html": (
        "webhooks.md",
        "WhatsApp Flows Webhooks Reference",
        "https://developers.facebook.com/docs/whatsapp/flows/reference/flowswebhooks",
    ),
}


def clean_wayback_urls(soup: BeautifulSoup) -> None:
    """Strip Wayback's /web/<timestamp>/ rewrites from anchors and remove Wayback toolbar."""
    # Remove Wayback's toolbar and analytics
    for sel in [
        "#wm-ipp-base",
        "#wm-ipp",
        "#wm-ipp-print",
        "script",
        "noscript",
        "style",
        "link",
        "iframe",
    ]:
        for el in soup.select(sel):
            el.decompose()

    # Rewrite hrefs
    wb_re = re.compile(r"^https?://web\.archive\.org/web/\d+(?:im_)?/")
    for a in soup.find_all("a", href=True):
        a["href"] = wb_re.sub("", a["href"])
    for img in soup.find_all("img", src=True):
        img["src"] = wb_re.sub("", img["src"])


def find_article(soup: BeautifulSoup) -> Tag | None:
    """Find the main article container.

    Meta's docs put content into #documentation_body_pagelet which holds
    a series of <h1>, <h2>, <h3>, <p>, <ul>, <table>, <pre> elements
    interleaved with chrome divs. We pick that pagelet as the root, then
    drop unwanted sibling chunks (feedback widget, secondary nav).
    """
    pagelet = soup.find(id="documentation_body_pagelet")
    if pagelet is None:
        # fall back to first <h1>'s parent chain
        h1 = soup.find("h1")
        return h1.parent if h1 else None
    return pagelet


def strip_chrome(article: Tag) -> None:
    """Remove feedback widgets, breadcrumbs, next/prev nav, side rails."""
    kill_selectors = [
        "#documentation_breadcrumbs_pagelet",
        "#documentation_primary_nav_pagelet",
        "#documentation_secondary_nav_pagelet",
        "#documentation_footer_pagelet",
        "#documentation_feedback_pagelet",
        "[data-referrer='documentation_feedback_pagelet']",
        "[data-referrer='documentation_secondary_nav_pagelet']",
        ".devsite-feedback",
        ".feedback",
    ]
    for sel in kill_selectors:
        for el in article.select(sel):
            el.decompose()

    # Remove "Was this page helpful?" blocks and rating widgets
    for el in article.find_all(string=re.compile(r"Was this page helpful|page useful", re.I)):
        # walk up to nearest div and remove
        parent = el.find_parent("div")
        if parent:
            parent.decompose()

    # Remove "On this page" right rail
    for el in article.find_all(string=re.compile(r"^On this page", re.I)):
        parent = el.find_parent("div")
        if parent:
            parent.decompose()


def convert(html_path: Path) -> str:
    raw = html_path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "lxml")
    clean_wayback_urls(soup)
    article = find_article(soup)
    if article is None:
        return ""
    strip_chrome(article)

    # html2text configuration
    h = html2text.HTML2Text()
    h.body_width = 0  # no line wrapping
    h.ignore_links = False
    h.ignore_images = True
    h.bypass_tables = False  # render tables as markdown
    h.mark_code = True
    h.unicode_snob = True
    h.escape_snob = True
    h.single_line_break = False

    md = h.handle(str(article))

    # Post-process: collapse 3+ blank lines, strip leading site chrome lines
    md = re.sub(r"\n{3,}", "\n\n", md)
    md = md.strip()
    return md


def main() -> int:
    if not REF_DIR.exists():
        print(f"Reference dir not found: {REF_DIR}", file=sys.stderr)
        return 1

    for raw_name, (md_name, title, source_url) in PAGES.items():
        raw_path = REF_DIR / raw_name
        if not raw_path.exists():
            print(f"SKIP {raw_name}: missing")
            continue
        body = convert(raw_path)
        if not body:
            print(f"EMPTY {raw_name}: no article body extracted")
            continue
        out_path = REF_DIR / md_name
        # If body already starts with a top-level heading rendered from <h1>,
        # we still prepend our own canonical title + Source line.
        content = f"# {title}\n\nSource: {source_url}\n\n{body}\n"
        out_path.write_text(content, encoding="utf-8")
        size = out_path.stat().st_size
        print(f"OK {md_name}: {size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
