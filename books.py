"""Read the Obsidian book notes in books/ and turn them into data for the site.

Each note is a Markdown file: the file name is the title, the header between
the --- lines holds fields like `author`, `status`, an optional `title` (use it for
punctuation a file name can't hold) and an optional `subtitle`. The spines show the
title (or `short_title`, if given; an old-style "Title: Subtitle" still shows only the
part before the ": "), plus ", Volume 2" when there's a `volume`; the full title is
"Title: Subtitle". `edition` is kept in the file but not shown.
`date_finished` (YYYY-MM-DD) is the day you finished the book; if you read it again, list the later
days under `reread` (one "- YYYY-MM-DD" per line). Both feed the Reading Log.
`dewey` is the book's Dewey Decimal number ("796", or "796.357"; keep the quotes so "005"
keeps its zeros). Like a library, books are shelved by Dewey class and, within a shelf,
by number and then the first author's last name; each spine gets a call-number sticker. The body is an
outline. Indented lines (tabs, or bullets like "- ") become nested points;
an unindented line with points under it becomes a section heading, and so does a
"# heading" line (points under it start at the left edge, as Obsidian lists do).
"""
import contextlib
import datetime
import hashlib
import re
import unicodedata
from pathlib import Path

from markupsafe import Markup, escape

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


def inline_html(text):
    """A line of Obsidian/Markdown as safe HTML: **bold**, *italic*, ==highlight== and links show as
    formatting; anything else that would look like raw syntax ([[links]], embeds) is tidied away."""
    # Markdown backslash escapes (Obsidian writes [y] as \[y\]): keep the character itself, and set it aside so
    # an escaped * or [ isn't read as formatting below
    kept = []

    def keep(m):
        kept.append(m.group(1))
        return f"\x00{len(kept) - 1}\x00"

    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|~=<>])", keep, text.strip())
    text = str(escape(text))
    text = re.sub(r"!\[\[[^\]]*\]\]", "", text)                                   # embeds
    text = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", text)                    # [[link|label]] -> label
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",                            # [label](https://...)
                  r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)                           # other links -> label
    text = re.sub(r"(\*\*|__)(?=\S)(.+?)(?<=\S)\1", r"<strong>\2</strong>", text)  # bold
    text = re.sub(r"(?<![\w*])\*(?=\S)(.+?)(?<=\S)\*(?![\w*])", r"<em>\1</em>", text)  # *italic*
    text = re.sub(r"(?<![\w_])_(?=\S)(.+?)(?<=\S)_(?![\w_])", r"<em>\1</em>", text)    # _italic_
    text = re.sub(r"==(.+?)==", r"<mark>\1</mark>", text)                          # highlight
    text = re.sub(r"\x00(\d+)\x00", lambda m: str(escape(kept[int(m.group(1))])), text)
    return Markup(text.strip())


def parse_note(raw):
    meta, body = {}, raw
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", raw, re.DOTALL)
    if m:
        key = None
        for line in m.group(1).splitlines():
            item = re.match(r"\s*-\s+(.*)", line)
            if item and key:                       # a list property, one "- value" per line (like `reread`)
                if not isinstance(meta[key], list):
                    meta[key] = [meta[key]] if meta[key] else []
                meta[key].append(item.group(1).strip().strip('"').strip("'"))
            elif ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                meta[key] = value.strip().strip('"').strip("'")
        body = m.group(2)

    # Each non-empty line becomes (depth, text).
    items = []
    under_heading = 0      # after a "# heading", left-edge points belong to it (one level in)
    for line in body.splitlines():
        if not line.strip():
            continue
        lead = line[: len(line) - len(line.lstrip())]
        depth = lead.count("\t") + lead.replace("\t", "").count(" ") // 4
        text = line.strip()
        heading = re.match(r"(#{1,6})\s+(.*)", text)
        if heading:
            items.append((0, inline_html(heading.group(2)), True))
            under_heading = 1
            continue
        depth += under_heading
        text = re.sub(r"^[-*+]\s+(\[[ xX]\]\s+)?", "", text)   # bullets go (the outline draws its own); numbers like "1)" stay
        items.append((depth, inline_html(text), False))

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
        return datetime.date.fromisoformat(str(raw)[:10])
    except ValueError:
        return None


def reread_dates(meta):
    """Later finishes from the `reread` list (one YYYY-MM-DD per item; commas work too)."""
    raw = meta.get("reread") or ""
    raw = " ".join(raw) if isinstance(raw, list) else raw
    dates = []
    for d in re.findall(r"\d{4}-\d{2}-\d{2}", raw):
        with contextlib.suppress(ValueError):      # skip impossible dates like 2027-02-30
            dates.append(datetime.date.fromisoformat(d))
    return dates


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
        main_title = meta.get("title") or path.stem
        subtitle = meta.get("subtitle", "")
        full_title = f"{main_title}: {subtitle}" if subtitle else main_title
        title = meta.get("short_title") or main_title.split(": ", 1)[0]
        if meta.get("volume"):
            title += ", Volume " + meta["volume"]
        digest = int(hashlib.md5(title.encode()).hexdigest(), 16)
        color_index = digest % len(COVER_COLORS)
        books.append({
            "title": title,
            "full_title": full_title,
            "subtitle": subtitle,
            "edition": meta.get("edition", ""),
            "volume": meta.get("volume", ""),
            "dewey": meta.get("dewey", ""),
            "call_number": " ".join(x for x in (meta.get("dewey", ""), cutter(meta.get("author", ""))) if x),
            "finished": finished_date(meta),  # the first time you finished it
            "reads": sorted({d for d in [finished_date(meta), *reread_dates(meta)] if d}),  # every finish, oldest first
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


# The second level of Dewey: ten divisions in each class, for the guide on top of the bookcase.
DEWEY_DIVISIONS = {
    "000": "Computer science, knowledge & systems", "010": "Bibliographies",
    "020": "Library & information sciences", "030": "Encyclopedias & books of facts",
    "040": "(unassigned)", "050": "Magazines, journals & serials",
    "060": "Associations, organizations & museums", "070": "News media, journalism & publishing",
    "080": "Quotations", "090": "Manuscripts & rare books",
    "100": "Philosophy", "110": "Metaphysics", "120": "Epistemology", "130": "Parapsychology & occultism",
    "140": "Philosophical schools of thought", "150": "Psychology", "160": "Logic", "170": "Ethics",
    "180": "Ancient, medieval & eastern philosophy", "190": "Modern western philosophy",
    "200": "Religion", "210": "Philosophy & theory of religion", "220": "The Bible", "230": "Christianity",
    "240": "Christian practice & observance", "250": "Christian pastoral practice & religious orders",
    "260": "Christian organization, social work & worship", "270": "History of Christianity",
    "280": "Christian denominations", "290": "Other religions (and mythology)",
    "300": "Social sciences, sociology & anthropology", "310": "Statistics", "320": "Political science",
    "330": "Economics", "340": "Law", "350": "Public administration & military science",
    "360": "Social problems & social services", "370": "Education",
    "380": "Commerce, communications & transportation", "390": "Customs, etiquette & folklore",
    "400": "Language", "410": "Linguistics", "420": "English", "430": "German & related languages",
    "440": "French & related languages", "450": "Italian, Romanian & related languages",
    "460": "Spanish, Portuguese & Galician", "470": "Latin & Italic languages",
    "480": "Classical & modern Greek", "490": "Other languages",
    "500": "Science", "510": "Mathematics", "520": "Astronomy", "530": "Physics", "540": "Chemistry",
    "550": "Earth sciences & geology", "560": "Fossils & prehistoric life", "570": "Biology",
    "580": "Plants", "590": "Animals",
    "600": "Technology", "610": "Medicine & health", "620": "Engineering", "630": "Agriculture",
    "640": "Home & family management (cooking)", "650": "Management & business",
    "660": "Chemical engineering", "670": "Manufacturing", "680": "Manufacture for specific uses",
    "690": "Construction of buildings",
    "700": "Arts", "710": "Area planning & landscape architecture", "720": "Architecture",
    "730": "Sculpture, ceramics & metalwork", "740": "Drawing & decorative arts", "750": "Painting",
    "760": "Graphic arts", "770": "Photography & computer art", "780": "Music",
    "790": "Sports, games & entertainment",
    "800": "Literature, rhetoric & criticism", "810": "American literature in English",
    "820": "English & Old English literatures", "830": "German & related literatures",
    "840": "French & related literatures", "850": "Italian, Romanian & related literatures",
    "860": "Spanish, Portuguese & Galician literatures", "870": "Latin & Italic literatures",
    "880": "Classical & modern Greek literatures", "890": "Other literatures",
    "900": "History", "910": "Geography & travel", "920": "Biography & genealogy",
    "930": "The ancient world (to about 499)", "940": "Europe", "950": "Asia", "960": "Africa",
    "970": "North America", "980": "South America", "990": "Other areas",
}


def dewey_guide(books):
    """The guide on top of the bookcase: every class with its ten divisions and how many of my books
    are in each. [(class, name, [(division, name, count), ...], count), ...]"""
    counts = {}
    for b in books:
        n = dewey_number(b)
        if n < 1000:
            counts[f"{int(n // 10) * 10:03d}"] = counts.get(f"{int(n // 10) * 10:03d}", 0) + 1
    guide = []
    for key, name in DEWEY_CLASSES.items():
        divisions = [(f"{d:03d}", DEWEY_DIVISIONS[f"{d:03d}"], counts.get(f"{d:03d}", 0))
                     for d in range(int(key), int(key) + 100, 10)]
        guide.append((key, name, divisions, sum(c for _, _, c in divisions)))
    return guide


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


def finishes(books):
    """One entry per time a book was finished (a re-read counts again): the book with `finished` set to
    that day and `again` = "", "2nd time", "3rd time", ..."""
    out = []
    for b in books:
        for n, day in enumerate(b["reads"], 1):
            again = "" if n == 1 else f"{n}{'nd' if n == 2 else 'rd' if n == 3 else 'th'} time"
            out.append(dict(b, finished=day, again=again))
    return out


def reading_log(books):
    """Every finish, newest first, grouped by year: [(2026, [book, ...]), ...]."""
    done = sorted(finishes(books), key=lambda b: (b["finished"], b["title"]), reverse=True)
    years = {}
    for b in done:
        years.setdefault(b["finished"].year, []).append(b)
    return list(years.items())


def reading_timeline(books, at_least=3):
    """Finished books month by month, oldest first, for the timeline at the top of the Reading Log.

    Every month from the first finished book to the latest is included (empty ones too, so the
    gaps show). Returns None until books have been finished at least `at_least` times.
    """
    done = sorted(finishes(books), key=lambda b: (b["finished"], b["title"]))
    if len(done) < at_least:
        return None
    month = done[0]["finished"].replace(day=1)
    last = done[-1]["finished"].replace(day=1)
    months = []
    while month <= last:
        months.append({"date": month,
                       "books": [b for b in done if b["finished"].replace(day=1) == month]})
        month = month.replace(year=month.year + month.month // 12, month=month.month % 12 + 1)
    return {"months": months, "count": len(done), "since": done[0]["finished"]}

