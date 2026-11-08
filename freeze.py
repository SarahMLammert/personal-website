"""Build the whole site as plain HTML files in build/, ready for GitHub Pages.

    python freeze.py

Every page is rendered once with Flask, saved as a file, and the static
folder is copied alongside. Then every link and image in the result is
checked, so a broken link fails the build instead of going live.
"""
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

from flask import render_template

from app import app, project_list
from books import load_books

ROOT = Path(__file__).parent
BUILD = ROOT / "build"


def pages():
    yield "/"
    yield "/about"
    yield "/photos"
    yield "/projects"
    for p in project_list():
        yield f"/projects/{p['slug']}"
    yield "/books"
    yield "/books/reading-log"
    for b in load_books():
        yield f"/books/{b['slug']}"


def out_path(url):
    """/ -> index.html, /books -> books/index.html (so /books and /books/ both work)."""
    url = url.strip("/")
    return BUILD / url / "index.html" if url else BUILD / "index.html"


def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir()

    client = app.test_client()
    for url in pages():
        resp = client.get(url)
        if resp.status_code != 200:
            sys.exit(f"{url} returned {resp.status_code}")
        target = out_path(url)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(resp.data)
        print("page ", url)

    # the "not found" page GitHub Pages shows for unknown addresses
    with app.test_request_context("/404"):
        (BUILD / "404.html").write_text(render_template("404.html"), encoding="utf-8")

    # static files: skip full-size photo originals, the site only uses the resized copies
    shutil.copytree(ROOT / "static", BUILD / "static",
                    ignore=shutil.ignore_patterns("originals", ".DS_Store"))
    shutil.copy(ROOT / "static" / "favicon.ico", BUILD / "favicon.ico")
    (BUILD / ".nojekyll").touch()   # tell GitHub Pages to serve files as they are

    check_links()
    size = sum(f.stat().st_size for f in BUILD.rglob("*") if f.is_file())
    print(f"built {BUILD.name}/ ({size / 1e6:.1f} MB)")


def check_links():
    """Every local href/src in the built pages must point at a real file."""
    broken = []
    for page in BUILD.rglob("*.html"):
        for ref in re.findall(r'(?:href|src)="([^"]+)"', page.read_text(encoding="utf-8")):
            u = urlparse(ref)
            if u.scheme or u.netloc or ref.startswith(("#", "mailto:")):
                continue
            path = u.path
            target = BUILD / path.lstrip("/")
            if not (target.is_file() or (target / "index.html").is_file()):
                broken.append(f"{page.relative_to(BUILD)} -> {ref}")
    if broken:
        sys.exit("broken links:\n  " + "\n  ".join(broken))


if __name__ == "__main__":
    main()
