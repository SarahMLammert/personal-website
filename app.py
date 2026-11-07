"""The site's pages. The words, links and projects live in content.py."""
import re
from pathlib import Path

from flask import Flask, abort, render_template, url_for

from books import grouped, load_books, slugify
from content import (ABOUT, BOOKCASE, DAY_EXTRAS, GITHUB, GLOBE, NIGHT_EXTRAS, PHOTO_CAPTIONS, PHOTO_WALL, PLATES,
                     PROJECTS, SITE_URL)

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
    """PHOTO_WALL with its link, the three photos it starts with, and every photo it rotates through."""
    return dict(PHOTO_WALL, href=url_for(PHOTO_WALL["endpoint"]),
                images=[photo_url(n) for n in PHOTO_WALL["photos"]],
                all=[photo_url(n) for n in photo_names()])


@app.route("/")
def home():
    plates = belt_plates()
    return render_template("index.html",
                           day=[p for p in plates if p.get("side", "day") == "day"],
                           night=[p for p in plates if p.get("side") == "night"],
                           day_extras=DAY_EXTRAS, night_extras=NIGHT_EXTRAS, globe=GLOBE,
                           bookcase=dict(BOOKCASE, href=url_for(BOOKCASE["endpoint"])),
                           photo_wall=photo_wall())


@app.route("/about")
def about():
    links = [dict(l, href=url_for(l["endpoint"]) if "endpoint" in l else l["url"], external="url" in l)
             for l in ABOUT["links"]]
    return render_template("about.html", about=ABOUT, links=links)


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
