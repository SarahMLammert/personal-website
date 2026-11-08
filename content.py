"""Everything the site says lives here. Edit this file to change the site's content.

Book notes come from the Markdown files in books/, and photos from
static/images/photos/ (see make_photos.py), so those aren't listed here.
"""

# The site's public address, used for link previews on social media.
SITE_URL = "https://www.sarahlammert.com"

# ---------------------------------------------------------------------------
# The homepage has two modes. Click the sun or moon in the window to switch.
#   Day ("side": "day"):     the sushi bar. Professional sections ride the belt as plates.
#   Night ("side": "night"): after hours. Personal sections are drinks on the bar.
# For each one, give:
#   "endpoint": a page on this site (the name of its function in app.py), or
#   "url":      a link to another site (opens in a new tab), or
#   neither:    it shows "Coming soon".
# sushi: toro, salmon, tuna, ebi, unagi, spicy, maki, tempura, ikura, acorn
# plate: red, blue, yellow, green, black, pink
# drink: taro, matcha, mango, brownsugar, strawberry
# ---------------------------------------------------------------------------
PLATES = [
    # day
    {"side": "day", "title": "Projects", "description": "Data and analytics work.", "endpoint": "projects",
     "sushi": "spicy", "plate": "blue"},
    {"side": "day", "title": "GitHub", "description": "Code and repositories.",
     "url": "https://github.com/SarahMLammert", "sushi": "salmon", "plate": "black"},
    {"side": "day", "title": "LinkedIn", "description": "Professional profile.",
     "url": "https://www.linkedin.com/in/sarahmlammert/", "sushi": "ebi", "plate": "pink"},
    # night
    # Photos is also the framed photos on the wall (PHOTO_WALL). This drink is temporary:
    # take it off the bar once more drinks are added.
    {"side": "night", "title": "Photos", "description": "Squirrels, mainly.", "endpoint": "photos",
     "drink": "taro"},
    # Book Notes is also the bookcase on the windowsill (BOOKCASE). This drink is temporary:
    # take it off the bar once more drinks are added.
    {"side": "night", "title": "Book Notes", "description": "Notes from what I\u2019m reading.", "endpoint": "books",
     "drink": "matcha"},
    {"side": "night", "title": "Writing", "description": "Notes and posts.",
     "drink": "mango"},
]

# Plates and drinks that are just for fun (no link).
DAY_EXTRAS = [
    {"title": "An acorn", "description": "Not on the menu", "sushi": "acorn", "plate": "yellow"},
    {"title": "Toro", "description": "Just a snack", "sushi": "toro", "plate": "red"},
    {"title": "Unagi", "description": "Just a snack", "sushi": "unagi", "plate": "green"},
]
NIGHT_EXTRAS = [
    {"title": "Acorn sour", "description": "House special", "drink": "brownsugar"},
]

# Things in the scene that open a page. Clicking one zooms the room into it ("worlds inside worlds").
# Day: the little globe on the windowsill. It spins to the Americas, then opens the atlas.
GLOBE = {"title": "College Sports Atlas", "description": "Where college athletes come from",
         "url": "https://sarahmlammert.github.io/college-sports-atlas/index.html"}

# After hours: the tall bookcase on the right. The Book Notes book slides off the shelf, then Book Notes opens.
BOOKCASE = {"title": "Book Notes", "description": "Notes from what I\u2019m reading.", "endpoint": "books"}

# After hours: framed photos on the wall, where the sushi menu hangs by day. The middle one comes forward,
# then Photos opens. Every few seconds one frame fades to the next photo, cycling through all of them.
# "photos" = the three to start with (left, middle, right), by file name in static/images/photos/web/.
PHOTO_WALL = {"title": "Photos", "description": "Squirrels, mainly.", "endpoint": "photos",
              "photos": ["squirrel2.jpg", "squirrel1.jpg", "squirrel3.jpg"]}

# ---------------------------------------------------------------------------
# About page: the chef in the middle of the belt opens it.
# DRAFT, written from what's already on the site. Rewrite it in your own words!
# ---------------------------------------------------------------------------
ABOUT = {
    "title": "About",
    "sub": "Nice to meet you",
    "hello": "Hi, I\u2019m Sarah.",
    "paragraphs": [
        "I work with data: maps, analysis, and building things people enjoy exploring. My favorite so far is "
        "the College Sports Atlas, which started as a project at work mapping where Ivy League football "
        "players come from and grew into a map of every Division I college.",
        "Outside of work you\u2019ll find me taking far too many photos of squirrels, ordering boba, eating "
        "conveyor belt sushi, and writing book notes in Obsidian. This site is a little of all of that.",
    ],
    "links": [
        {"title": "Projects", "endpoint": "projects"},
        {"title": "GitHub", "url": "https://github.com/SarahMLammert"},
        {"title": "LinkedIn", "url": "https://www.linkedin.com/in/sarahmlammert/"},
    ],
}


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
            {"label": "After hours",
             "title": "Separate the professional from the personal",
             "text": "I added a night scene so the site could have two sides: by day, the sushi bar shows "
                     "my professional work, and after hours, the personal side opens up. It was also a chance "
                     "to put in something else I love, boba, and the dream of owning a boba shop that turns "
                     "into a night club."},
        ],
        "features": ["Squirrel sushi bar illustration", "Plates on a moving belt", "After-hours boba bar",
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
             "title": "Start small, with the Ivies",
             "text": "For a project at work, we mapped where Ivy League football players are recruited "
                     "from. The dot map and the heatmaps both came out of that project, and they became the "
                     "starting point for everything else."},
            {"label": "All of Division I",
             "title": "Scale it up to every D1 college",
             "text": "Once it worked for the Ivies, I wanted to see the same thing for every Division I "
                     "college. A lot of my coworkers, and the sports professionals I met through the IMPACT "
                     "Learning Institute, love college football, so I thought it would be fun to build "
                     "something they'd enjoy exploring."},
            {"label": "Recruiting footprints",
             "title": "Let people pick the colleges",
             "text": "The Ivy League version showed all eight heatmaps on one page. Seeing colleges side by "
                     "side was the part that mattered, so I made the heatmap page modular: you pick which "
                     "colleges to compare, up to four at a time."},
            {"label": "Transfer map",
             "title": "Follow the players who move",
             "text": "With NIL changing college sports, and transfers being something we look at in my work "
                     "too, I realized I could map transfers in and out of D1, college to college."},
            {"label": "More divisions",
             "title": "Go beyond D1 to see the whole picture",
             "text": "To follow transfers, I needed rosters from the colleges players were coming from and "
                     "going to, so I added Division II, Division III, NAIA and junior colleges."},
            {"label": "Coaching moves & staff directory",
             "title": "Map the people behind the teams",
             "text": "Working in an athletic department, I wondered where coaches and staff come from, and I "
                     "thought it was an interesting thing to visualize. So I added a map of coaching moves "
                     "and a directory of every college's staff over time."},
            {"label": "School influence map",
             "title": "Make it for the fans",
             "text": "My boss is a super fan of her college\u2019s teams, so I made a way to pick one college "
                     "and see where everyone who went there ended up: players, coaches and staff."},
            {"label": "All-sports college map", "next": True,
             "title": "Put every sport for one college on one map",
             "text": "A massive map for a single college, with every one of its sports together in one place."},
            {"label": "High school map", "next": True,
             "title": "Flip it around to the high schools",
             "text": "A map of just the high schools, to see which ones are sending the most players to "
                     "college teams."},
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
