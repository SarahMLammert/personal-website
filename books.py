"""Read the Obsidian book notes in books/ and turn them into data for the site.

Each note is a Markdown file: the file name is the title, the header between
the --- lines holds fields like `author` and `status`, and the body is an
outline. Indented lines (tabs, or bullets like "- ") become nested points;
an unindented line with points under it becomes a section heading.
"""
import hashlib
import re
from pathlib import Path

BOOKS_DIR = Path(__file__).parent / "books"

# How statuses are grouped on the page, in order. Anything else goes last.
STATUS_GROUPS = [
    ("Reading", {"reading", "currently reading", "in progress"}),
    ("Finished", {"read", "finished", "done", "completed"}),
    ("To read", {"to read", "to-read", "want to read", "tbr"}),
]

COVER_COLORS = ["#2f4a3f", "#6b2a2a", "#26344d", "#8a6a35", "#4a2f45", "#3b4248", "#5a4632"]


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def clean_inline(text):
    """Strip Obsidian/Markdown syntax that shouldn't show up as raw characters."""
    text = re.sub(r"!\[\[[^\]]*\]\]", "", text)                    # embeds
    text = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", text)     # [[link|label]] -> label
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)            # [label](url) -> label
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text)                 # bold
    text = re.sub(r"(?<!\w)[*_](.+?)[*_](?!\w)", r"\1", text)       # italic
    text = re.sub(r"==(.+?)==", r"\1", text)                        # highlight
    return text.strip()


def parse_note(raw):
    meta, body = {}, raw
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", raw, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip().lower()] = value.strip().strip('"').strip("'")
        body = m.group(2)

    # Each non-empty line becomes (depth, text).
    items = []
    for line in body.splitlines():
        if not line.strip():
            continue
        lead = line[: len(line) - len(line.lstrip())]
        depth = lead.count("\t") + lead.replace("\t", "").count(" ") // 4
        text = line.strip()
        heading = re.match(r"(#{1,6})\s+(.*)", text)
        if heading:
            items.append((0, clean_inline(heading.group(2)), True))
            continue
        text = re.sub(r"^([-*+]|\d+[.)])\s+(\[[ xX]\]\s+)?", "", text)
        items.append((depth, clean_inline(text), False))

    # Build a tree from the indentation.
    root = {"children": []}
    stack = [(-1, root)]
    for depth, text, is_heading in items:
        node = {"text": text, "children": [], "heading": is_heading}
        while stack[-1][0] >= depth:
            stack.pop()
        stack[-1][1]["children"].append(node)
        stack.append((depth, node))

    # Top-level lines with points under them read as section headings.
    for node in root["children"]:
        if node["children"]:
            node["heading"] = True
    return meta, root["children"]


def spine_size(title, digest):
    """Height varies a little from book to book; width fits the title's lines."""
    height = 220 + (digest >> 8) % 45
    chars_per_line = (height - 74) // 8.4          # 14px serif, written down the spine (with room to spare)
    lines = max(1, min(4, -(-len(title) // int(chars_per_line))))
    return {"spine_height": height, "spine_width": 26 + lines * 19}


def status_group(status):
    s = (status or "").strip().lower()
    for label, names in STATUS_GROUPS:
        if s in names:
            return label
    return status or "Other"


def load_books():
    books = []
    if not BOOKS_DIR.exists():
        return books
    for path in sorted(BOOKS_DIR.glob("*.md")):
        meta, notes = parse_note(path.read_text(encoding="utf-8"))
        title = meta.get("title") or path.stem
        digest = int(hashlib.md5(title.encode()).hexdigest(), 16)
        color_index = digest % len(COVER_COLORS)
        books.append({
            "title": title,
            "slug": slugify(title),
            "author": meta.get("author", ""),
            "status": meta.get("status", ""),
            "group": status_group(meta.get("status")),
            "notes": notes,
            "has_notes": bool(notes),
            "color": meta.get("color") or COVER_COLORS[color_index],
            # spine size on the bookshelf: a little variety, wider for long titles
            **spine_size(title, digest),
        })
    return books


def grouped(books):
    order = [label for label, _ in STATUS_GROUPS]
    groups = {}
    for b in books:
        groups.setdefault(b["group"], []).append(b)
    keys = sorted(groups, key=lambda g: order.index(g) if g in order else len(order))
    # books with notes first within each group
    return [(k, sorted(groups[k], key=lambda b: (not b["has_notes"], b["title"]))) for k in keys]
