"""Everything the site says lives here. Edit this file to change the site's content.

Book notes come from the Markdown files in books/, and photos from
static/images/photos/ (see make_photos.py), so those aren't listed here.
"""

# The site's public address, used for link previews on social media.
SITE_URL = "https://www.sarahlammert.com"

# ---------------------------------------------------------------------------
# Plates on the homepage sushi belt, in order. For each one, give:
#   "endpoint": a page on this site (the name of its function in app.py), or
#   "url":      a link to another site (opens in a new tab), or
#   neither:    the plate shows "Coming soon".
# sushi: toro, salmon, tuna, ebi, unagi, spicy, maki, tempura, ikura
# plate: red, blue, yellow, green, black, pink
# ---------------------------------------------------------------------------
PLATES = [
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

# ---------------------------------------------------------------------------
# Captions for photos, by file name (optional).
# ---------------------------------------------------------------------------
PHOTO_CAPTIONS = {
    # "squirrel1.jpg": "Lunch break.",
}


# ---------------------------------------------------------------------------
# Projects page, in order. Each project's "story" is its flow of questions; a step with
# "next": True shows as "In progress".
# ---------------------------------------------------------------------------
GITHUB = "https://github.com/SarahMLammert"

PROJECTS = [
    {
        "title": "This Website",
        "kicker": "Design and front end",
        "summary": "A personal site run by squirrels at a sushi bar.",
        "story": [
            {"label": "Personal page and squirrel photos",
             "title": "Start with what I like",
             "text": "The site began as a place to show off my squirrel photos, because squirrels are "
                     "awesome! A simple page with a few links and a gallery was all it needed to be at first."},
            {"label": "Sushi theme",
             "title": "A spinning idea, served on a conveyor belt",
             "text": "I wanted the homepage to spin, and the first thing that came to mind was conveyor "
                     "belt sushi, like at Kura. Every section of the site became a plate riding around the "
                     "belt, so you pick what you want as it goes by."},
            {"label": "Bookshelf",
             "title": "A tiny bookshelf for my notes",
             "text": "I write my book notes in Obsidian and wanted them on the site. I thought of those "
                     "little make-it-yourself miniature bookshelves, so each book sits on the shelf as its "
                     "own spine, with room for a lot more."},
            {"label": "Squirrel sushi bar",
             "title": "Make it feel like the art on my wall",
             "text": "I have Pok\u00e9mon art prints of little scenes, like a barbecue and bath time in the "
                     "sink, and I wanted my homepage to feel like one of them. So the sushi bar became an "
                     "illustrated scene, with squirrels like the ones in my photos sitting around the belt."},
        ],
        "features": ["Squirrel sushi bar illustration", "Plates on a moving belt",
                     "Photo gallery and viewer", "Bookshelf of book notes", "Project story flows"],
        "tools": ["Python", "Flask", "Jinja", "JavaScript", "SVG", "CSS", "Obsidian", "GitHub Pages"],
        "image": "images/projects/website-home.jpg",
        "image_alt": "The homepage: an illustrated sushi bar where squirrels sit around a conveyor belt of plates",
        "url": "/",
        "cta": "Back to the counter",
        "code": "https://github.com/SarahMLammert/personal-website",
    },
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
]
