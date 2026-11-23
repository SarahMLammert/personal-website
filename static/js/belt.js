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

    // ---- the Earth: the desk globe riding on a plate, and its big copy ------
    // The same photo as the Sports Pipeline Atlas's globe (NASA's Blue Marble, 2048x1024, latitude and longitude in a
    // grid), wrapped the same way: seen from space, its axis leaning 23.4 degrees with the north pole to the right,
    // turning west to east. Each pixel of a globe's canvas works out once where on the photo it looks; turning the
    // Earth only slides that sideways, so a redraw is one quick pass (the atlas does the same).
    const TILT = 23.4 * Math.PI / 180;
    const ATLAS_START = 20;                      // the atlas's globe starts with 20 degrees east (Africa) facing us
    const SPIN = 360 / 14;                       // degrees a second: one turn in 14 s
    let earth = null;                            // { w, h, data } once the photo has loaded
    let globeLon = -75;                          // the longitude facing us on the desk globe
    let globeRate = 1;
    function painter(canvas) {
        const n = canvas.width, R = n / 2, g = canvas.getContext('2d');
        let u0 = null, row, out, px;
        return lon => {
            if (!earth) return false;
            const { w, h, data } = earth;
            if (!u0) {
                const c = Math.cos(TILT), s = Math.sin(TILT);
                u0 = new Float32Array(n * n); row = new Int32Array(n * n);
                for (let y = 0; y < n; y++) {
                    for (let x = 0; x < n; x++) {
                        let sx = (x + 0.5 - R) / R, sy = (R - y - 0.5) / R;
                        const d = Math.hypot(sx, sy);
                        if (d > 1 + 2 / R) { u0[y * n + x] = -1; continue; }
                        if (d > 0.999) { sx *= 0.999 / d; sy *= 0.999 / d; }   // just past the edge: repeat the rim (the clip trims it)
                        const z = Math.sqrt(1 - sx * sx - sy * sy);
                        const ux = sx * c - sy * s, uy = sx * s + sy * c;      // undo the lean
                        const lat = Math.asin(uy) * 180 / Math.PI, dlon = Math.atan2(ux, z) * 180 / Math.PI;
                        u0[y * n + x] = (dlon + 180) / 360 * w;
                        row[y * n + x] = Math.min(h - 1, Math.max(0, Math.floor((90 - lat) / 180 * h))) * w;
                    }
                }
                out = g.createImageData(n, n);
                px = new Uint32Array(out.data.buffer);
            }
            const shift = lon / 360 * w;
            for (let k = 0; k < px.length; k++) {
                const a = u0[k];
                if (a < 0) { px[k] = 0; continue; }
                let u = (a + shift) % w;
                if (u < 0) u += w;
                px[k] = data[row[k] + (u | 0)];
            }
            g.putImageData(out, 0, 0);
            return true;
        };
    }
    const deskGlobe = root.querySelector('.plate-globe');
    const globePhoto = root.querySelector('.globe-photo');
    const smallCanvas = document.createElement('canvas');
    smallCanvas.width = smallCanvas.height = 100;
    const paintSmall = painter(smallCanvas);
    let paintBig = null, bigTurn = null, lastT = null, frame = 0;
    if (deskGlobe) {
        const img = new Image();
        img.onload = () => {
            try {
                const c = document.createElement('canvas');
                c.width = img.width; c.height = img.height;
                const g = c.getContext('2d');
                g.drawImage(img, 0, 0);
                earth = { w: c.width, h: c.height, data: new Uint32Array(g.getImageData(0, 0, c.width, c.height).data.buffer) };
                if (paintSmall(globeLon)) globePhoto.setAttribute('href', smallCanvas.toDataURL());
            } catch (e) { earth = null; }          // then the globe stays plain blue sea
        };
        img.src = deskGlobe.dataset.earth;
        const tick = t => {
            const dt = lastT === null ? 0 : Math.min(0.1, (t - lastT) / 1000);
            lastT = t;
            if (!reduceMotion.matches) globeLon -= SPIN * globeRate * dt;
            // the little globe: about 30 redraws a second, only while it can be seen
            if (earth && !reduceMotion.matches && !isNight() && !document.hidden && !zooming && (frame++ & 1) === 0) {
                if (paintSmall(globeLon)) globePhoto.setAttribute('href', smallCanvas.toDataURL());
            }
            // the big copy, while it turns round to Africa
            if (bigTurn && paintBig) {
                const u = Math.min(1, Math.max(0, (t - bigTurn.t0) / bigTurn.dur));
                const moved = (u ** 3 - 2 * u ** 2 + u) * bigTurn.pace + (3 * u ** 2 - 2 * u ** 3) * bigTurn.d;
                paintBig(bigTurn.from - moved);
                if (u >= 1) bigTurn = null;
            }
            requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }
    // Speed the desk globe up (hover) or back down.
    function spinGlobe(rate) { globeRate = rate; }
    // The big copy starts exactly where the little globe has got to, at the same speed, then speeds up smoothly and
    // slows to a stop with Africa facing us, just as the atlas's globe starts (a cubic Hermite curve).
    function turnBigGlobe(world, now) {
        const cv = world.querySelector('.zoom-earth-cv');
        if (!cv) return;
        paintBig = paintBig || painter(cv);
        const DURATION = 2650;                                       // done just before it settles into the atlas
        const pace = SPIN * globeRate * DURATION / 1000;             // how far it would turn at its own speed
        let d = (((globeLon - ATLAS_START) % 360) + 360) % 360;      // degrees still to turn (always forwards)
        while (d < 0.75 * pace) d += 360;                            // never slow down before speeding up
        paintBig(globeLon);
        bigTurn = { t0: now, from: globeLon, d, pace, dur: DURATION };
    }
    // Then it settles into the atlas's ring: the atlas's globe is centred across the window, 20 px + half the room
    // below its 151 px of header and legend down, with a radius of 220 x the atlas's scale (from its fit()).
    // Phones get the atlas's list instead of the ring, so there it dives in (CSS).
    function landOnAtlas(world) {
        const art = world.querySelector('.zoom-globe'), ball = world.querySelector('.zoom-earth');
        const w = window.innerWidth, h = window.innerHeight;
        if (art && ball && w > 700) {
            const a = art.getBoundingClientRect(), b = ball.getBoundingClientRect();
            const bx = b.left + b.width / 2, by = b.top + b.height / 2;
            const k = Math.max(0.3, Math.min(1, (w - 32) / 1180, (h - 151) / 1060));
            const s = (220 * k) / (b.width / 2);
            const origin = `${bx - a.left}px ${by - a.top}px`;
            ball.style.setProperty('--s', s.toFixed(4));
            art.animate([
                { transformOrigin: origin, transform: 'translate(0px, 0px) scale(1)' },
                { transformOrigin: origin, transform: `translate(${w / 2 - bx}px, ${20 + (h - 151) / 2 - by}px) scale(${s})` },
            ], { duration: 800, easing: 'cubic-bezier(.45, 0, .2, 1)', fill: 'forwards' });
        }
        world.classList.add('is-diving');
    }

    // ---- labels ---------------------------------------------------------
    function show(p) {
        if (zooming) return;
        held = p;
        const href = p.getAttribute('href');
        tag.querySelector('strong').textContent = p.dataset.title;
        tag.dataset.href = href || '';
        tag.dataset.external = p.dataset.external ? '1' : '';
        // plates and drinks carry their own place cards, so with a mouse they're just picked up, no label;
        // on phones the cards are hidden and tapping still shows the label
        tag.hidden = p.matches('.belt-plate, .bar-drink') && !touch.matches;
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
    // Then its big copy (.zoom-world) takes over: the globe turns to Africa and settles into the atlas / the photo comes
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
                [1700, () => (world.dataset.for === 'globe' ? landOnAtlas(world) : world.classList.add('is-diving'))],   // and we dive in
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
        bigTurn = null;
        document.querySelectorAll('.zoom-globe').forEach(g => g.getAnimations().forEach(a => a.cancel()));
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
