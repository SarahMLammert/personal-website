"""The site's pages. The words, links and projects live in content.py."""
import re
from pathlib import Path

from flask import Flask, abort, render_template, url_for

from books import grouped, load_books
from content import GITHUB, PHOTO_CAPTIONS, PLATES, PROJECTS

app = Flask(__name__)
PHOTO_DIR = Path(app.static_folder) / "images" / "photos"


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
    return render_template("index.html", plates=belt_plates())


@app.route("/photos")
def photos():
    names = sorted((p.name for p in (PHOTO_DIR / "web").glob("*.jpg")), key=natural_key)
    items = [{
        "thumb": url_for("static", filename=f"images/photos/thumb/{n}"),
        "full": url_for("static", filename=f"images/photos/web/{n}"),
        "caption": PHOTO_CAPTIONS.get(n, ""),
    } for n in names]
    return render_template("photos.html", photos=items)


@app.route("/projects")
def projects():
    return render_template("projects.html", projects=PROJECTS, github=GITHUB)


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
