"""The site's pages. The words, links and projects live in content.py."""
import re
from pathlib import Path

from flask import Flask, abort, render_template, url_for

from books import dewey_guide, grouped, inline_html, load_books, reading_log, reading_timeline, slugify
from content import (
    ABOUT,
    AFTER_HOURS_PASSWORD,
    BOOKCASE,
    DAY_EXTRAS,
    GITHUB,
    GLOBE,
    GUESTBOOK,
    MUNCHER,
    NIGHT_EXTRAS,
    NOTES_VISION,
    PHOTO_CAPTIONS,
    PHOTO_WALL,
    PLATES,
    PRINT_LINKS,
    PROJECTS,
    SITE_URL,
    SPECIALS,
)

app = Flask(__name__)
PHOTO_DIR = Path(app.static_folder) / "images" / "photos"


@app.context_processor
def site_info():
    """Every page knows the site's address (for link previews)."""
    return {"site_url": SITE_URL}


def belt_plates():
    """PLATES from content.py, with the link each plate opens."""
    plates = []
    for item in PLATES:
        plate = dict(item)
        plate["external"] = "url" in item
        plate["href"] = url_for(item["endpoint"]) if "endpoint" in item else item.get("url")
        plates.append(plate)
    return plates


def natural_key(name):
    """Sort squirrel2 before squirrel10."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def photo_names():
    """Every photo, in order (the files make_photos.py wrote)."""
    return sorted((p.name for p in (PHOTO_DIR / "web").glob("*.jpg")), key=natural_key)


def photo_url(name, size="thumb"):
    return url_for("static", filename=f"images/photos/{size}/{name}")


def photo_wall():
    """PHOTO_WALL with its link, the photo it starts with, and every photo it rotates through."""
    return dict(PHOTO_WALL, href=url_for(PHOTO_WALL["endpoint"]),
                image=photo_url(PHOTO_WALL["photo"]),
                all=[photo_url(n) for n in photo_names()])


def with_hrefs(links):
    """Links from content.py, each with the address it opens and whether it leaves the site."""
    return [dict(link, href=url_for(link["endpoint"]) if "endpoint" in link else link["url"],
                 external="url" in link)
            for link in links]


@app.route("/")
def home():
    plates = belt_plates()
    return render_template("index.html",
                           day=[p for p in plates if p.get("side", "day") == "day"],
                           night=[p for p in plates if p.get("side") == "night"],
                           day_extras=DAY_EXTRAS, night_extras=NIGHT_EXTRAS, globe=GLOBE,
                           bookcase=dict(BOOKCASE, href=url_for(BOOKCASE["endpoint"])),
                           photo_wall=photo_wall(), muncher=MUNCHER, guestbook=GUESTBOOK,
                           specials=dict(SPECIALS, href=url_for(SPECIALS["endpoint"])), print_links=with_hrefs(PRINT_LINKS),
                           after_hours_password=AFTER_HOURS_PASSWORD)


@app.route("/about")
def about():
    return render_template("about.html", about=ABOUT, links=with_hrefs(ABOUT["links"]), projects=project_list()[:3])


@app.route("/photos")
def photos():
    items = [{
        "thumb": photo_url(n),
        "full": photo_url(n, "web"),
        "caption": PHOTO_CAPTIONS.get(n, ""),
    } for n in photo_names()]
    return render_template("photos.html", photos=items)


def project_list():
    """PROJECTS from content.py, each with its own page address."""
    return [dict(p, slug=slugify(p["title"]), external=p["url"].startswith("http")) for p in PROJECTS]


@app.route("/projects")
def projects():
    return render_template("projects.html", projects=project_list(), github=GITHUB)


@app.route("/projects/<slug>")
def project(slug):
    found = next((p for p in project_list() if p["slug"] == slug), None)
    if not found:
        abort(404)
    return render_template("project.html", p=found, after_hours_password=AFTER_HOURS_PASSWORD)


@app.route("/books")
def books():
    return render_template("books.html", groups=grouped(load_books()))


@app.route("/books/about-these-notes")
def notes_vision_page():
    """The small book on top of the Dewey guide: why I keep these notes."""
    paragraphs = [inline_html(p) for p in NOTES_VISION["paragraphs"]]
    return render_template("about_notes.html", vision=NOTES_VISION, paragraphs=paragraphs)


@app.route("/books/dewey")
def dewey_guide_page():
    """The guide lying on top of the bookcase: how the Dewey Decimal shelves work."""
    return render_template("dewey.html", guide=dewey_guide(load_books()))


@app.route("/books/reading-log")
def reading_log_page():
    """The reading log: the journal on the Book Notes shelf opens this timeline of finished books."""
    all_books = load_books()
    reading = [b for b in all_books if b["group"] == "Reading"]
    return render_template("reading_log.html", years=reading_log(all_books), reading=reading,
                           timeline=reading_timeline(all_books))


@app.route("/books/<slug>")
def book(slug):
    found = next((b for b in load_books() if b["slug"] == slug), None)
    if not found:
        abort(404)
    return render_template("book.html", book=found)


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
