# personal-website

Sarah May Hui Yu Lammert's personal site: an illustrated squirrel sushi bar homepage, photos, projects and book notes.

It's a small Flask app that gets built into plain HTML files and published on GitHub Pages
every time `main` is pushed (`.github/workflows/deploy.yml`).

`.github/social-preview.png` is the image for the repo's link preview. GitHub doesn't pick it up
automatically: upload it under Settings → General → Social preview.

## Where things live

| To change | Edit |
|---|---|
| Plates and bowls on the belt, drink tubs on the bar, the globe / framed photo / bookcase / guest book / specials board, the About page, project write-ups, photo captions, the after-hours password | `content.py` |
| Book notes | Markdown files in `books/` (written in Obsidian) |
| Photos | `static/images/photos/originals/`, then run `python make_photos.py` |
| Page layouts | `templates/` |
| Look and feel | `static/css/style.css` |
| The homepage scene and belt | `templates/_scene.html`, `templates/_squirrels.html`, `templates/_sushi.html`, `static/js/belt.js` |
| The zoom into the globe, photos or bookcase | big copies in `templates/index.html`, `zoomInto()` in `static/js/belt.js`, "worlds inside worlds" in `style.css` |
| The photo viewer | `static/js/lightbox.js` |

## The homepage

An art print of a squirrel sushi bar, with the name and buttons for Projects, GitHub and LinkedIn
underneath. The name shows as "Sarah Lammert"; rest the pointer on it (or tap it) for two seconds and
"May Hui Yu" unfolds.

**By day** it's the sushi bar. Each link is part of the picture, labelled the way the room would label it:

- the chalkboard beside the chef says "Projects"
- the chef has an "About" sign hanging from his table
- the host stand by the door has a "LinkedIn" name plate
- the squirrel eating sushi wears a "hello, my name is GitHub" tag
- a little globe rides the belt on a yellow plate with an "Atlas" place card; click it to zoom into the
  Sports Pipeline Atlas

The other plates on the belt are snacks (sushi, or bowls of ramen, chirashi and edamame), each with a place
card. Point at a plate and it comes forward and grows so its card is easy to read. The counters are covered
in finished plates, and the shelves hold a teapot, a sake set, a waving lucky cat, a daruma, a jar of acorns,
a bonsai, a sake barrel and rice bowls.

**After hours** (click the sun; there's a password, and the moon brings you back) it becomes a bar with a DJ.
The links are big tubs of boba with name stickers on the glass, next to a bowl of boba pearls: Photos, Book
Notes and Music (coming soon). The framed photo on the wall (it slowly cycles through every photo) also opens
Photos, and the tall bookcase, with its "Book Notes" sign on top, opens Book Notes. The bartender has an
"About" sign for the night About page (not written yet). The shelves turn into liquor bottles, a shaker,
stacked glasses and a record player, with a lava lamp and a candle on the windowsill.

Hovering over anything clickable shows its name; on phones the first tap shows it and the second opens it.

Clicking the globe, the photo or the bookcase zooms into it before the page opens. To add another one:
draw it in `_scene.html` as a `.scene-link` with `data-zoom="name"` and a `.zoom-from` part, add a big
copy in `index.html` as `.zoom-world[data-for="name"]` (with the same `.zoom-from` part), and style its
stages in `style.css`.

A few things to keep in step when editing the scene:

- The counter and belt are drawn flattened (`SQUASH` at the top of `_scene.html`, `BELT_SQUASH` in
  `belt.js`): change both together. Anything placed on the counter by hand goes at
  `600 + (y - 600) × 0.82`.
- The counter top is a band around `COUNTER` (straights from x 390 to 1210) and the belt runs inside it
  along `BELT` (430 to 1170). If the belt changes, the inner island and the two clip paths move with it; if
  the counter changes, so do the counter front and everything at its ends.
- Food on the counter's plates is drawn the same size as the belt's food at that depth (`fs` in
  `plate_stack()`): about 0.55 at the back and 1.23 at the front (`0.55 + 0.68 × depth` in `belt.js`). A small plate at the front gets a single
  piece (`spicy-piece`).
- Nigiri come in pairs (`nigiri()` in `_sushi.html` draws one piece; `sushi()` puts two side by side) and
  maki as six small rolls.
- Draw order is depth: things behind the counter come before it, labels on the counter come before the
  front row so the diners' tails pass in front of them.

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
reread:                # read it again? one "- YYYY-MM-DD" line per later finish
edition: 5             # kept in the file, not shown
volume:                # adds ", Volume N" to the title
color: "#26344d"       # optional cover color
---
```

Books are shelved like a library: one shelf per Dewey class, then by number and the first author's last
name, each with a call-number sticker. A red ribbon bookmark marks what I'm reading now. The leather
journal on the first shelf opens the Reading Log: finished books by year, and once three books have
a `date_finished`, a month-by-month timeline at the top. The navy guide lying on top of the bookcase opens
a table of every Dewey class and division, with how many books are in each (`DEWEY_DIVISIONS` in `books.py`).

Write the notes as an Obsidian outline: `#` headings for parts and chapters, and `- ` points under
them (Tab to nest a point, Shift+Tab to bring it back). Numbered points like `1)` keep their numbers,
and *italics*, **bold** and ==highlights== show on the site.

## Working on it locally

```
python3 -m venv .venv                         # once: a private Python for this project
source .venv/bin/activate                     # each new Terminal window
python -m pip install -r requirements-dev.txt # once: Flask, Pillow and the checkers

python app.py          # preview at http://127.0.0.1:5000
python freeze.py       # build the static site into build/ and check every link
ruff check .           # check the Python
djlint templates --lint  # check the templates
```

The checkers' settings live in `pyproject.toml`.
