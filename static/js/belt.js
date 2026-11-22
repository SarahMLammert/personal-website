// The homepage scene. By day, plates ride the conveyor belt; after hours, drinks sit on the bar.
// Hover or focus a plate or drink to see where it goes; click to open it.
// On phones the first tap shows a title-only label, and tapping the label (or the item again) opens it.
// Click the sun or moon in the window to switch between day and night (there's no other hint: it's for explorers).
(function () {
    const root = document.querySelector('[data-belt]');
    if (!root) return;

    const SPEED = 55;                 // canvas units per second
    const html = document.documentElement;
    const svg = root.querySelector('svg');
    const line = svg.querySelector('#belt-line');
    const slats = svg.querySelectorAll('.belt-slats');   // the belt's back and front runs
    const back = svg.querySelector('#plates-back');
    const front = svg.querySelector('#plates-front');
    const plates = Array.from(svg.querySelectorAll('.belt-plate'));
    const picks = Array.from(svg.querySelectorAll('.belt-plate, .bar-drink, .scene-link'));
    const tag = root.querySelector('.plate-tag');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const touch = window.matchMedia('(hover: none)');

    const length = line.getTotalLength();
    const gap = length / plates.length;
    const TOP = 520, BOTTOM = 680;    // the belt's back and front straights (before flattening)
    const BELT_SQUASH = 0.82;         // the belt is drawn flattened around y = 600 (SQUASH in _scene.html)
    let offset = 0, held = null, last = null, zooming = false;

    const isNight = () => html.classList.contains('is-night');

    // ---- the belt -------------------------------------------------------
    function place() {
        plates.forEach((p, i) => {
            const pt = line.getPointAtLength((offset + i * gap) % length);
            const depth = (pt.y - TOP) / (BOTTOM - TOP);           // 0 at the back, 1 at the front
            const scale = 0.82 + 0.56 * depth;                     // smaller at the back, bigger at the front (depth)
            const y = 600 + (pt.y - 600) * BELT_SQUASH;
            p.setAttribute('transform', `translate(${pt.x.toFixed(1)} ${y.toFixed(1)}) scale(${scale.toFixed(3)})`);
            const group = pt.y < 600 ? back : front;                // pass behind or in front of the chef
            if (p.parentNode !== group && p !== held) group.appendChild(p);
        });
        slats.forEach(sl => sl.setAttribute('stroke-dashoffset', (-offset).toFixed(1)));
    }

    function tick(t) {
        if (last !== null && !held && !isNight() && !reduceMotion.matches) {
            offset = (offset + SPEED * Math.min((t - last) / 1000, 0.1)) % length;
            place();
        }
        last = t;
        requestAnimationFrame(tick);
    }

    // ---- the desk globe (riding on a plate) -------------------------------
    const globeLand = root.querySelector('.globe-land');
    const AMERICAS = -64;                        // how far the land has to slide for the Americas to face us
    // Speed up without changing its place (changing animation-duration in CSS makes the land jump).
    function spinGlobe(rate) {
        if (globeLand && globeLand.getAnimations) globeLand.getAnimations().forEach(a => a.updatePlaybackRate(rate));
    }
    // The big copy starts exactly where the little globe has got to, at the same speed, then speeds up
    // smoothly and slows to a stop with the Americas facing us. (It used to keep pace for 1.3 s and then
    // whip most of a turn in one second, which looked like a jolt.)
    let bigGlobeTurn = null;
    function turnBigGlobe(world, now) {
        const land = world.querySelector('.zoom-land');
        if (!land || !globeLand) return;
        const spin = globeLand.getAnimations()[0];
        const speed = (spin ? spin.playbackRate : 1) * 100 / 14;     // land units per second (one turn = 100 units in 14 s)
        const DURATION = 2650;                                       // done just before the dive starts
        const x = new DOMMatrix(getComputedStyle(globeLand).transform).m41;
        const pace = speed * DURATION / 1000;                        // how far it would go at its own speed
        // distance forwards to the Americas (one full turn looks identical, so add turns as needed); at least
        // 3/4 of its own pace, so it never slows down before speeding up
        let d = (((x - AMERICAS) % 100) + 100) % 100;
        while (d < 0.75 * pace) d += 100;
        const start = AMERICAS + d;              // same look as x (whole turns apart), so it ends exactly on the Americas
        // a smooth curve that starts at the globe's own speed and ends at rest (cubic Hermite), sampled as keyframes
        const frames = [];
        for (let i = 0; i <= 40; i++) {
            const u = i / 40;
            const moved = (u ** 3 - 2 * u ** 2 + u) * pace + (3 * u ** 2 - 2 * u ** 3) * d;
            frames.push({ transform: `translateX(${(start - moved).toFixed(3)}px)` });
        }
        bigGlobeTurn = land.animate(frames, { duration: DURATION, fill: 'forwards' });
        bigGlobeTurn.startTime = now;            // start this very frame, in step with the little globe
    }

    // ---- labels ---------------------------------------------------------
    function show(p) {
        if (zooming) return;
        held = p;
        const href = p.getAttribute('href');
        tag.querySelector('strong').textContent = p.dataset.title;
        tag.dataset.href = href || '';
        tag.dataset.external = p.dataset.external ? '1' : '';
        tag.hidden = false;
        const box = svg.getBoundingClientRect();
        const r = p.querySelector('.pick-art').getBoundingClientRect();
        tag.style.left = `${r.left + r.width / 2 - box.left}px`;
        tag.style.top = `${r.top - box.top}px`;
        // keep the label inside the picture (the globe sits right at the edge)
        const half = tag.offsetWidth / 2 + 4;
        const x = Math.min(Math.max(r.left + r.width / 2 - box.left, half), box.width - half);
        tag.style.left = `${x}px`;
        p.classList.add('is-held');
        if (p.dataset.zoom === 'globe') spinGlobe(3.5);
    }

    function hide() {
        if (zooming) return;                     // the room sliding under the pointer mustn't drop the globe
        if (held) held.classList.remove('is-held');
        spinGlobe(1);
        held = null;
        tag.hidden = true;
    }

    picks.forEach(p => {
        p.addEventListener('pointerenter', e => { if (e.pointerType !== 'touch') show(p); });
        p.addEventListener('pointerleave', e => { if (e.pointerType !== 'touch') hide(); });
        p.addEventListener('focus', () => show(p));
        p.addEventListener('blur', () => { if (!touch.matches) hide(); });   // phones close it by tapping elsewhere
        // Tapping also focuses the item, so remember whether its label was already up before this tap.
        p.addEventListener('pointerdown', () => { p.dataset.wasHeld = held === p ? '1' : ''; });
        p.addEventListener('click', e => {
            const keyboard = e.detail === 0;
            if (touch.matches && !keyboard && !p.dataset.wasHeld) { e.preventDefault(); show(p); }
            p.dataset.wasHeld = '';
        });
    });

    // ---- worlds inside worlds --------------------------------------------
    // Clicking the globe (day), or the framed photo or bookcase (after hours), zooms the room into it.
    // Then its big copy (.zoom-world) takes over: the globe spins to the Americas / the photo comes
    // forward / the Book Notes book slides out, and we dive in and open the page.
    const worlds = Array.from(document.querySelectorAll('.zoom-world'));
    let zoomMoves = [];
    function zoomInto(el) {
        const href = el.getAttribute('href');
        const world = document.querySelector(`.zoom-world[data-for="${el.dataset.zoom}"]`);
        if (!world || reduceMotion.matches) { window.location.href = href; return; }
        if (zooming) return;
        zooming = true;
        held = el;                               // the belt stops while we zoom (the globe rides on a plate)
        tag.hidden = true;                       // keep the object 'picked up' so it doesn't shrink mid-zoom
        // measure it in its final 'picked up' pose, not halfway through growing into it
        const art = el.querySelector('.pick-art');
        art.style.transition = 'none';
        el.classList.add('is-held');
        const print = root.closest('.print');
        const box = print.getBoundingClientRect();
        const r = el.querySelector('.zoom-from').getBoundingClientRect();
        const gx = r.left + r.width / 2, gy = r.top + r.height / 2;
        void art.offsetWidth;
        art.style.transition = '';
        const target = world.querySelector('.zoom-art').getBoundingClientRect();     // where the big copy will be
        const big = target.width * parseFloat(world.dataset.fit);                 // its .zoom-from part, on screen
        const scale = big / r.width;
        const landing = world.querySelector('.zoom-from').getBoundingClientRect();    // the same part on the big copy
        const lx = landing.left + landing.width / 2, ly = landing.top + landing.height / 2;
        const dx = lx - gx, dy = ly - gy;
        const pivot = `${lx - target.left}px ${ly - target.top}px`;
        print.style.transformOrigin = `${gx - box.left}px ${gy - box.top}px`;
        document.documentElement.classList.add('is-zooming');
        root.classList.add('is-zooming');
        // The big copy rides along on top of the room, starting at the object's exact size and place, and grows
        // to fill the screen; it covers the object from the first frame, so the swap can't show.
        // The room itself only zooms part of the way (at most ROOM_ZOOM), then fades under the big copy's
        // background: drawing the whole illustration at the globe's full 17x froze the zoom for a second.
        const ROOM_ZOOM = 3;
        const glide = { duration: 1000, easing: 'cubic-bezier(.5, 0, .7, 1)' };
        zoomMoves = [
            print.animate([{ transform: 'translate(0px, 0px) scale(1)' }, { transform: `translate(${dx}px, ${dy}px) scale(${Math.min(scale, ROOM_ZOOM)})` }], { ...glide, fill: 'forwards' }),
            world.querySelector('.zoom-art').animate([{ transformOrigin: pivot, transform: `translate(${-dx}px, ${-dy}px) scale(${1 / scale})` }, { transformOrigin: pivot, transform: 'translate(0px, 0px) scale(1)' }], glide),
        ];
        const now = document.timeline.currentTime;
        zoomMoves.forEach(a => { a.startTime = now; });
        world.classList.add('is-gliding');
        turnBigGlobe(world, now);
        setTimeout(() => world.classList.add('is-on'), 650);               // the background fades in over the room
        zoomMoves[0].finished.then(() => { print.style.visibility = 'hidden'; }, () => {});   // covered: stop drawing it
        // once the room has finished zooming in, the big copy takes over
        let started = false;
        const next = () => {
            if (started) return;
            started = true;
            [
                [0, () => world.classList.add('is-on')],                   // (already on; in case the timer was late)
                [300, () => world.classList.add('is-turning')],            // spin / come forward / slide out
                [1700, () => world.classList.add('is-diving')],            // and we dive in
                [2600, () => { window.location.href = href; }],
            ].forEach(([ms, fn]) => setTimeout(fn, ms));
        };
        zoomMoves[0].finished.then(next, () => {});
        setTimeout(next, 1300);                                            // in case the animation never reports back
    }
    // coming back with the browser's Back button: put the room back as it was
    window.addEventListener('pageshow', () => {
        zooming = false;
        hide();
        picks.forEach(p => p.classList.remove('is-held'));
        root.classList.remove('is-zooming');
        document.documentElement.classList.remove('is-zooming');
        const print = root.closest('.print');
        print.style.transformOrigin = '';
        print.style.visibility = '';
        zoomMoves.forEach(a => a.cancel());
        zoomMoves = [];
        worlds.forEach(w => w.classList.remove('is-gliding', 'is-on', 'is-turning', 'is-diving'));
        if (bigGlobeTurn) bigGlobeTurn.cancel();
    });
    picks.forEach(p => {
        if (!p.dataset.zoom) return;
        p.addEventListener('click', e => {
            if (e.defaultPrevented) return;                          // first tap on a phone just shows the label
            e.preventDefault();
            zoomInto(p);
        });
    });

    // ---- the framed photo (after hours) ----------------------------------
    // Every few seconds it fades to the next photo, slowly cycling through all of them.
    const wall = svg.querySelector('.photo-wall');
    if (wall && wall.dataset.photos && !reduceMotion.matches) {
        const all = wall.dataset.photos.split(' ');
        // the zoomed-in copy follows along, so the dive lands on the photo you clicked
        const imgs = document.querySelectorAll('.photo-wall .wall-img, .zoom-world[data-for="photos"] .wall-img');
        let pointer = Math.max(0, all.indexOf(imgs[0].getAttribute('href')));
        all.forEach(src => { const im = new Image(); im.src = src; });   // so the fades never show a blank frame
        setInterval(() => {
            if (!isNight() || zooming || document.hidden) return;
            pointer = (pointer + 1) % all.length;
            imgs.forEach(im => im.classList.add('is-fading'));
            setTimeout(() => imgs.forEach(im => { im.setAttribute('href', all[pointer]); im.classList.remove('is-fading'); }), 600);
        }, 3200);
    }

    // on phones the label itself is a button: tapping it opens the item's page
    tag.addEventListener('click', () => {
        if (held && held.dataset.zoom) { zoomInto(held); return; }
        const href = tag.dataset.href;
        if (!href) return;
        if (tag.dataset.external) window.open(href, '_blank', 'noopener');
        else window.location.href = href;
    });
    document.addEventListener('click', e => { if (held && !e.target.closest('.belt-plate, .bar-drink, .scene-link, .plate-tag')) hide(); });
    window.addEventListener('resize', () => { if (held) show(held); });

    // ---- day and night --------------------------------------------------
    function setMode(night) {
        hide();
        html.classList.toggle('is-night', night);
        try { localStorage.setItem('mode', night ? 'night' : 'day'); } catch (e) {}
        if (history.replaceState) history.replaceState(null, '', night ? '#after-hours' : location.pathname);
    }

    // ---- the door: a password before After Hours (just for fun; remembered once given) ----
    const door = document.querySelector('.ah-door');
    const doorInput = door.querySelector('.ah-door-input');
    const doorWrong = door.querySelector('.ah-door-wrong');
    const sun = svg.querySelector('.celestial.sun');
    const isOpen = () => { try { return localStorage.getItem('afterHours') === 'open'; } catch (e) { return false; } };
    function openDoor() {
        hide();
        doorWrong.textContent = '';
        doorInput.value = '';
        door.hidden = false;
        doorInput.focus();
    }
    function closeDoor() {
        door.hidden = true;
        door.classList.remove('is-wrong');
        if (sun) sun.focus();
    }
    door.addEventListener('submit', e => {
        e.preventDefault();
        if (doorInput.value.trim().toLowerCase() === door.dataset.password.toLowerCase()) {
            try { localStorage.setItem('afterHours', 'open'); } catch (err) {}
            door.hidden = true;
            setMode(true);
            return;
        }
        doorWrong.textContent = "That's not it.";
        doorInput.value = '';
        door.classList.remove('is-wrong');
        void door.offsetWidth;                                     // restart the shake
        door.classList.add('is-wrong');
        doorInput.focus();
    });
    door.querySelector('.ah-door-leave').addEventListener('click', closeDoor);
    door.addEventListener('keydown', e => { if (e.key === 'Escape') closeDoor(); });
    function goNight() { if (isOpen()) setMode(true); else openDoor(); }

    svg.querySelectorAll('.celestial').forEach(c => {
        const toggle = () => (isNight() ? setMode(false) : goNight());
        c.addEventListener('click', toggle);
        c.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); }
        });
    });
    if (location.hash === '#after-hours' && !isNight()) openDoor();
    window.addEventListener('hashchange', () => {
        if (location.hash === '#after-hours') goNight();
        else if (location.hash === '#daytime') setMode(false);
    });

    place();
    root.classList.add('is-live');
    requestAnimationFrame(tick);
})();
