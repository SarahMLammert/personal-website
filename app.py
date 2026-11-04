import re
from pathlib import Path

from flask import Flask, abort, render_template, url_for

from books import grouped, load_books

app = Flask(__name__)

# Everything that rides the sushi belt on the hub (home page).
# To add something, add an entry here:
#   "endpoint": a page on this site (the function name of its route), or
#   "url":      a link to another site (opens in a new tab), or
#   neither:    shows as "Coming soon".
HUB_ITEMS = [
    {"title": "Photos", "description": "Squirrels, mainly.", "endpoint": "photos",
     "sushi": "toro", "plate": "red"},
    {"title": "Projects", "description": "Data and analytics work.", "endpoint": "projects",
     "sushi": "spicy", "plate": "blue"},
    {"title": "Book Notes", "description": "Notes from what I\u2019m reading.", "endpoint": "books",
     "sushi": "tempura", "plate": "yellow"},
    {"title": "Writing", "description": "Notes and posts.",
     "sushi": "unagi", "plate": "green"},
    {"title": "GitHub", "description": "Code and repositories.",
     "url": "https://github.com/SarahMLammert", "sushi": "salmon", "plate": "black"},
    {"title": "LinkedIn", "description": "Professional profile.",
     "url": "https://www.linkedin.com/in/sarahmlammert/", "sushi": "ebi", "plate": "pink"},
]
# sushi options: toro, salmon, tuna, ebi, unagi, spicy, maki, tempura, ikura
# plate options: red, blue, yellow, green, black, pink


def hub_cards():
    cards = []
    for item in HUB_ITEMS:
        card = dict(item)
        card["external"] = "url" in item
        if "endpoint" in item:
            card["href"] = url_for(item["endpoint"])
        else:
            card["href"] = item.get("url")
        cards.append(card)
    return cards


# some browsers ask for /favicon.ico directly
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/')
def home():
    return render_template('index.html', cards=hub_cards())


# Photos page. Every image in static/images/photos/web shows up automatically
# (run make_photos.py after adding new originals). Captions are optional.
PHOTO_DIR = Path(app.static_folder) / "images" / "photos"
CAPTIONS = {
    # "squirrel1.jpg": "Lunch break.",
}


def natural_key(name):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


@app.route('/photos')
def photos():
    names = sorted((p.name for p in (PHOTO_DIR / "web").glob("*.jpg")), key=natural_key)
    items = [{
        "thumb": url_for('static', filename=f"images/photos/thumb/{n}"),
        "full": url_for('static', filename=f"images/photos/web/{n}"),
        "caption": CAPTIONS.get(n, ""),
    } for n in names]
    return render_template('photos.html', photos=items)


# Projects page. Add a project by adding an entry here; the first one is featured.
GITHUB = "https://github.com/SarahMLammert"
PROJECTS = [
    {
        "title": "College Sports Atlas",
        "kicker": "Interactive data maps",
        "summary": "Where college athletes come from, and where coaches go.",
        # How the project grew, step by step (shown as a flow on the page).
        "story": [
            {"label": "Dot map",
             "title": "Where do Ivy League football players come from?",
             "text": "For a project at work, we mapped where Ivy League football players are "
                     "recruited from. The dot map was part of that project."},
            {"label": "All of Division I",
             "title": "Can we do this for all of D1?",
             "text": "Once it worked for the Ivies, I wanted to see the same thing for every "
                     "Division I college."},
            {"label": "Recruiting footprints",
             "title": "What if you could choose the colleges?",
             "text": "I modified the heatmap page to be more modular, so you can pick which "
                     "colleges to compare."},
            {"label": "Transfer map",
             "title": "Where do transfers go?",
             "text": "After thinking about transfers, I realized I could map the transfers in "
                     "and out of D1."},
            {"label": "More divisions",
             "title": "What about players outside D1?",
             "text": "To follow transfers, I needed more rosters, so I added more divisions."},
            {"label": "Coaching moves & staff directory",
             "title": "Where does the staff come from?",
             "text": "Working in an athletic department, I thought this was an interesting thing "
                     "to visualize."},
            {"label": "School influence map",
             "title": "Where did everyone from one college end up?",
             "text": "My boss is a super fan of her college\u2019s teams, so I made a way to pick "
                     "one college and see where everyone who went there ended up."},
            {"label": "All-sports college map", "next": True,
             "title": "What does one college look like across every sport?",
             "text": "A massive map for a single college, with every one of its sports together "
                     "in one place."},
            {"label": "High school map", "next": True,
             "title": "Which high schools are getting the most looks?",
             "text": "A map of just high schools, to see which ones are sending the most players "
                     "to college teams."},
        ],
        "stats": [("12", "sports"), ("1.5M+", "player records"), ("2016\u20132027", "seasons")],
        "features": ["Recruiting map", "Recruiting footprints", "Transfer map",
                     "Coaching moves", "Staff directory", "School influence map"],
        "tools": ["Python", "Requests", "Beautiful Soup", "Playwright", "D3", "GitHub Pages"],
        "image": "images/projects/atlas-map.jpg",
        "image_alt": "Map of the United States covered in colored dots, one for each college football player's hometown",
        "url": "https://sarahmlammert.github.io/college-sports-atlas/index.html",
        "cta": "Explore the atlas",
        "code": "https://github.com/SarahMLammert/college-sports-atlas",
    },
    {
        "title": "This Website",
        "kicker": "Design and front end",
        "summary": "A personal site served like a sushi bar.",
        "story": [
            {"label": "Personal page and squirrel photos",
             "title": "Where do I start?",
             "text": "First, I made a simple personal page and displayed my squirrel photos."},
            {"label": "Sushi theme",
             "title": "How do I make it fun?",
             "text": "The sushi theme was a personal choice. I just wanted the site to be fun."},
            {"label": "Bookshelf",
             "title": "Where do my book notes go?",
             "text": "I put the book notes I write in Obsidian on a bookshelf with room for a lot of books."},
        ],
        "features": ["Rotating sushi belt", "Spotlight on the front plate",
                     "Photo gallery and viewer", "Bookshelf of book notes", "Project story flows"],
        "tools": ["Python", "Flask", "Jinja", "JavaScript", "SVG", "CSS", "Obsidian", "Render"],
        "image": "images/projects/website-home.jpg",
        "image_alt": "The homepage: a round sushi conveyor belt on a dark counter, with the front plate in a spotlight",
        "url": "/",
        "cta": "Back to the counter",
        "code": "https://github.com/SarahMLammert/personal-website",
    },
]


@app.route('/projects')
def projects():
    return render_template('projects.html', projects=PROJECTS, github=GITHUB)


# Book notes: every Markdown file in books/ (written in Obsidian) gets a page.
@app.route('/books')
def books():
    return render_template('books.html', groups=grouped(load_books()))


@app.route('/books/<slug>')
def book(slug):
    found = next((b for b in load_books() if b["slug"] == slug), None)
    if not found:
        abort(404)
    return render_template('book.html', book=found)


if __name__ == "__main__":
    app.run(debug=True)
