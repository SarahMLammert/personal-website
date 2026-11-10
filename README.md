# personal-website

Sarah May Hui Yu Lammert's personal site: an illustrated squirrel sushi bar homepage, photos, projects and book notes.

It's a small Flask app that gets built into plain HTML files and published on GitHub Pages
every time `main` is pushed (`.github/workflows/deploy.yml`).

`.github/social-preview.png` is the image for the repo's link preview. GitHub doesn't pick it up
automatically: upload it under Settings → General → Social preview.

## Where things live

| To change | Edit |
|---|---|
| Plates on the belt, drinks on the bar, the globe / framed photos / bookcase, project write-ups, photo captions | `content.py` |
| Book notes | Markdown files in `books/` (written in Obsidian) |
| Photos | `static/images/photos/originals/`, then run `python make_photos.py` |
| Page layouts | `templates/` |
| Look and feel | `static/css/style.css` |
| The homepage scene and belt | `templates/_scene.html`, `templates/_squirrels.html`, `static/js/belt.js` |
| The zoom into the globe, photos or bookcase | big copies in `templates/index.html`, `zoomInto()` in `static/js/belt.js`, "worlds inside worlds" in `style.css` |
| The photo viewer | `static/js/lightbox.js` |

## The homepage

By day it's a sushi bar: plates ride the conveyor belt (Projects, GitHub, LinkedIn) and a globe on the
windowsill opens the College Sports Atlas. Click the sun and it turns into an after-hours bar: drinks on
the bar, a big framed photo on the wall (it slowly cycles through every photo) and a tall bookcase. Click the
moon to go back.

Clicking the globe, the photos or the bookcase zooms into it before the page opens. To add another one:
draw it in `_scene.html` as a `.scene-link` with `data-zoom="name"` and a `.zoom-from` part, add a big
copy in `index.html` as `.zoom-world[data-for="name"]` (with the same `.zoom-from` part), and style its stages in `style.css`.

## Book notes

Each note in `books/` becomes a book on the shelf. The header sets its details:

```
---
author: Robert B. Cialdini
status: Reading        # Reading, Read or To read
title: "Influence: The Psychology of Persuasion"   # optional, defaults to the file name
color: "#26344d"       # optional cover color
---
```

Unindented lines with indented points under them become section headings.

## Working on it locally

```
pip install -r requirements.txt
python app.py          # preview at http://127.0.0.1:5000
python freeze.py       # build the static site into build/ and check every link
```

`make_photos.py` also needs Pillow (`pip install pillow`).
