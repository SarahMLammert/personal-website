# personal-website

Sarah May Hui Yu Lammert's personal site: a sushi conveyor belt homepage, photos, projects and book notes.

It's a small Flask app that gets built into plain HTML files and published on GitHub Pages
every time `main` is pushed (`.github/workflows/deploy.yml`).

`.github/social-preview.png` is the image for the repo's link preview. GitHub doesn't pick it up
automatically: upload it under Settings → General → Social preview.

## Where things live

| To change | Edit |
|---|---|
| Plates on the homepage belt, project write-ups, photo captions | `content.py` |
| Book notes | Markdown files in `books/` (written in Obsidian) |
| Photos | `static/images/photos/originals/`, then run `python make_photos.py` |
| Page layouts | `templates/` |
| Look and feel | `static/css/style.css` |
| The belt and the photo viewer | `static/js/ring.js`, `static/js/lightbox.js` |

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
