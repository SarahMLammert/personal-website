"""Read the Obsidian book notes in books/ and turn them into data for the site.

Each note is a Markdown file: the file name is the title, the header between
the --- lines holds fields like `author`, `status` and an optional full `title`
(use it for punctuation a file name can't hold, like a colon). The site shows the
short title: the part before the first ": " (or `short_title`, if given), plus
", Volume 2" when there's a `volume`. `edition` is kept in the file but not shown.
`date_finished` (YYYY-MM-DD) is the day you finished the book, for a reading timeline.
`dewey` is the book's Dewey Decimal number ("796", or "796.357"; keep the quotes so "005"
keeps its zeros). Like a library, books are shelved by Dewey class and, within a shelf,
by number and then the first author's last name; each spine gets a call-number sticker. The body is an
outline. Indented lines (tabs, or bullets like "- ") become nested points;
an unindented line with points under it becomes a section heading.
"""
import datetime
import hashlib
import re
import unicodedata
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
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", raw, re.DOTALL)
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
    height = 238 + (digest >> 8) % 45
    chars_per_line = (height - 112) // 8.4         # 14px serif down the spine; leaves room for author + call-number sticker
    lines = max(1, min(5, -(-len(title) // int(chars_per_line))))
    return {"spine_height": height, "spine_width": 26 + lines * 19}


def finished_date(meta):
    """`date_finished: 2026-11-08` (Obsidian's date property) -> a date, or None if blank or unreadable."""
    raw = meta.get("date_finished") or meta.get("date finished") or ""
    try:
        return datetime.date.fromisoformat(raw[:10])
    except ValueError:
        return None


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
        full_title = meta.get("title") or path.stem
        title = meta.get("short_title") or full_title.split(": ", 1)[0]
        if meta.get("volume"):
            title += ", Volume " + meta["volume"]
        digest = int(hashlib.md5(title.encode()).hexdigest(), 16)
        color_index = digest % len(COVER_COLORS)
        books.append({
            "title": title,
            "full_title": full_title,
            "edition": meta.get("edition", ""),
            "volume": meta.get("volume", ""),
            "dewey": meta.get("dewey", ""),
            "call_number": " ".join(x for x in (meta.get("dewey", ""), cutter(meta.get("author", ""))) if x),
            "finished": finished_date(meta),  # for a reading timeline
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


# The shelves, like a library: Dewey Decimal classes, by the hundreds.
DEWEY_CLASSES = {
    "000": "Computers & Information",
    "100": "Philosophy & Psychology",
    "200": "Religion",
    "300": "Social Sciences",
    "400": "Language",
    "500": "Science & Math",
    "600": "Technology & Business",
    "700": "Arts & Recreation",
    "800": "Literature",
    "900": "History & Geography",
}


def author_last(author):
    """Last name of the first author: "Gayle Laakmann McDowell" -> "McDowell"."""
    first = (author or "").split(",")[0].strip()
    words = [w for w in first.split() if w.rstrip(".").lower() not in {"jr", "sr", "ii", "iii"}]
    return words[-1] if words else ""


def cutter(author):
    """The letters on a library spine label: first three of the author's last name, "LEW"."""
    plain = unicodedata.normalize("NFKD", author_last(author)).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z]", "", plain)[:3].upper()


def dewey_number(b):
    try:
        return float(b["dewey"])
    except (TypeError, ValueError):
        return 1000.0          # no number yet: shelved last


def call_order(b):
    """Library order: call number, then author's last name, then title."""
    return (dewey_number(b), author_last(b["author"]).lower(), b["title"].lower())


def grouped(books):
    """Shelves for the Book Notes page: one per Dewey class. Books I'm reading stay in
    their section and get a ribbon bookmark instead."""
    shelves = []
    sections = {}
    for b in books:
        n = dewey_number(b)
        key = f"{int(n // 100) * 100:03d}" if n < 1000 else ""
        sections.setdefault(key, []).append(b)
    for key in sorted(sections, key=lambda k: k or "999"):
        name = DEWEY_CLASSES.get(key, "Not yet shelved")
        shelves.append((name, key, sorted(sections[key], key=call_order)))
    return shelves


def reading_log(books):
    """Finished books with a `date_finished`, newest first, grouped by year: [(2026, [book, ...]), ...]."""
    done = sorted((b for b in books if b["finished"]), key=lambda b: (b["finished"], b["title"]), reverse=True)
    years = {}
    for b in done:
        years.setdefault(b["finished"].year, []).append(b)
    return list(years.items())
