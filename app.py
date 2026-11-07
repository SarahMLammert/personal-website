"""The site's pages. The words, links and projects live in content.py."""
import re
from pathlib import Path

from flask import Flask, abort, render_template, url_for

from books import grouped, load_books, slugify
from content import BOOKCASE, DAY_EXTRAS, PHOTO_WALL, GITHUB, GLOBE, NIGHT_EXTRAS, PHOTO_CAPTIONS, PLATES, PROJECTS, SITE_URL

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


@app.route("/")
def home():
    plates = belt_plates()
    return render_template("index.html",
                           day=[p for p in plates if p.get("side", "day") == "day"],
                           night=[p for p in plates if p.get("side") == "night"],
                           day_extras=DAY_EXTRAS, night_extras=NIGHT_EXTRAS, globe=GLOBE,
                           bookcase=dict(BOOKCASE, href=url_for(BOOKCASE["endpoint"])),
                           photo_wall=dict(PHOTO_WALL, href=url_for(PHOTO_WALL["endpoint"]),
                                           images=[url_for("static", filename=f"images/photos/thumb/{n}")
                                                   for n in PHOTO_WALL["photos"]]))


@app.route("/photos")
def photos():
    names = sorted((p.name for p in (PHOTO_DIR / "web").glob("*.jpg")), key=natural_key)
    items = [{
        "thumb": url_for("static", filename=f"images/photos/thumb/{n}"),
        "full": url_for("static", filename=f"images/photos/web/{n}"),
        "caption": PHOTO_CAPTIONS.get(n, ""),
    } for n in names]
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
    return render_template("project.html", p=found)


@app.route("/books")
def books():
    return render_template("books.html", groups=grouped(load_books()))


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
