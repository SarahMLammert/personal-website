# personal-website

Sarah May Hui Yu Lammert's personal site: an illustrated squirrel sushi bar homepage, photos, projects and book notes.

It's a small Flask app that gets built into plain HTML files and published on GitHub Pages
every time `main` is pushed (`.github/workflows/deploy.yml`).

`.github/social-preview.png` is the image for the repo's link preview. GitHub doesn't pick it up
automatically: upload it under Settings → General → Social preview.

## Where things live

| To change | Edit |
|---|---|
| Plates on the belt, drinks on the bar, the globe / framed photo / bookcase, the About page, project write-ups, photo captions | `content.py` |
| Book notes | Markdown files in `books/` (written in Obsidian) |
| Photos | `static/images/photos/originals/`, then run `python make_photos.py` |
| Page layouts | `templates/` |
| Look and feel | `static/css/style.css` |
| The homepage scene and belt | `templates/_scene.html`, `templates/_squirrels.html`, `static/js/belt.js` |
| The zoom into the globe, photos or bookcase | big copies in `templates/index.html`, `zoomInto()` in `static/js/belt.js`, "worlds inside worlds" in `style.css` |
| The photo viewer | `static/js/lightbox.js` |

## The homepage

An art print of a squirrel sushi bar, with the name and buttons for Projects, GitHub and LinkedIn
underneath. The name shows as "Sarah Lammert"; rest the pointer on it (or tap it) for two seconds and
"May Hui Yu" unfolds.

By day, plates ride the conveyor belt (Projects, GitHub, LinkedIn), the chef opens the About page and a
globe on the windowsill opens the College Sports Atlas. Click the sun and it turns into an after-hours bar:
drinks on the bar, a big framed photo on the wall (it slowly cycles through every photo) and a tall
bookcase. Click the moon to go back. Hovering over anything clickable shows its name.

Clicking the globe, the photo or the bookcase zooms into it before the page opens. To add another one:
draw it in `_scene.html` as a `.scene-link` with `data-zoom="name"` and a `.zoom-from` part, add a big
copy in `index.html` as `.zoom-world[data-for="name"]` (with the same `.zoom-from` part), and style its
stages in `style.css`.

## Book notes

Each note in `books/` becomes a book on the shelf; copy `books/_templates/Template.md` to start one.
The file name is the book's full title (no colons). The header sets its details:

```
---
title: "Influence: The Psychology of Persuasion"   # full title, quoted (for punctuation a file name can't hold)
short_title: ""        # optional: what the spine shows (default: the part before the first ": ")
author: Robert B. Cialdini                          # several authors: "A, B"
dewey: "153"           # Dewey Decimal number, quoted; decides the shelf
status: Reading        # Reading, Read or To Read
date_finished:         # YYYY-MM-DD once finished; feeds the Reading Log
edition: 5             # kept in the file, not shown
volume:                # adds ", Volume N" to the title
color: "#26344d"       # optional cover color
---
```

Books are shelved like a library: one shelf per Dewey class, then by number and the first author's last
name, each with a call-number sticker. A red ribbon bookmark marks what I'm reading now. The leather
journal on the first shelf opens the Reading Log (finished books by year).

Unindented lines with indented points under them become section headings.

## Working on it locally

```
pip install -r requirements.txt
python app.py          # preview at http://127.0.0.1:5000
python freeze.py       # build the static site into build/ and check every link
```

`make_photos.py` also needs Pillow (`pip install pillow`).
