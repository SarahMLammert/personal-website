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
    const slats = svg.querySelector('.belt-slats');
    const back = svg.querySelector('#plates-back');
    const front = svg.querySelector('#plates-front');
    const plates = Array.from(svg.querySelectorAll('.belt-plate'));
    const picks = Array.from(svg.querySelectorAll('.belt-plate, .bar-drink, .scene-link'));
    const tag = root.querySelector('.plate-tag');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const touch = window.matchMedia('(hover: none)');

    const length = line.getTotalLength();
    const gap = length / plates.length;
    const TOP = 520, BOTTOM = 680;    // the belt's back and front straights
    let offset = 0, held = null, last = null, zooming = false;

    const isNight = () => html.classList.contains('is-night');

    // ---- the belt -------------------------------------------------------
    function place() {
        plates.forEach((p, i) => {
            const pt = line.getPointAtLength((offset + i * gap) % length);
            const depth = (pt.y - TOP) / (BOTTOM - TOP);           // 0 at the back, 1 at the front
            const scale = 0.98 + 0.3 * depth;
            p.setAttribute('transform', `translate(${pt.x.toFixed(1)} ${pt.y.toFixed(1)}) scale(${scale.toFixed(3)})`);
            const group = pt.y < 600 ? back : front;                // pass behind or in front of the chef
            if (p.parentNode !== group && p !== held) group.appendChild(p);
        });
        slats.setAttribute('stroke-dashoffset', (-offset).toFixed(1));
    }

    function tick(t) {
        if (last !== null && !held && !isNight() && !reduceMotion.matches) {
            offset = (offset + SPEED * Math.min((t - last) / 1000, 0.1)) % length;
            place();
        }
        last = t;
        requestAnimationFrame(tick);
    }

    // ---- the desk globe --------------------------------------------------
    const globeLand = root.querySelector('.globe-land');
    const AMERICAS = -64;                        // how far the land has to slide for the Americas to face us
    // Speed up without changing its place (changing animation-duration in CSS makes the land jump).
    function spinGlobe(rate) {
        if (globeLand && globeLand.getAnimations) globeLand.getAnimations().forEach(a => a.updatePlaybackRate(rate));
    }
    // The big copy starts exactly where the little globe has got to, then carries on round to the Americas.
    function turnBigGlobe(world) {
        const land = world.querySelector('.zoom-land');
        if (!land || !globeLand) return;
        let x = new DOMMatrix(getComputedStyle(globeLand).transform).m41;
        if (x < AMERICAS) x += 100;              // already past them: one full turn back looks identical, and keeps it spinning forwards
        land.style.transition = 'none';
        land.style.transform = `translateX(${x}px)`;
        void land.getBoundingClientRect();
        land.style.transition = '';
        land.style.transform = `translateX(${AMERICAS}px)`;
    }

    // ---- labels ---------------------------------------------------------
    function show(p) {
        if (zooming) return;
        held = p;
        const href = p.getAttribute('href');
        tag.querySelector('strong').textContent = p.dataset.title + (p.dataset.external ? ' ↗' : '');
        tag.querySelector('span').textContent = p.dataset.sub;
        tag.dataset.href = href || '';
        tag.dataset.external = p.dataset.external ? '1' : '';
        tag.classList.toggle('is-link', !!href);
        tag.classList.toggle('is-external', !!p.dataset.external);
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
    // Clicking the globe (day), or the framed photos or bookcase (after hours), zooms the room into it.
    // Then its big copy (.zoom-world) takes over: the globe spins to the Americas / the middle photo comes
    // forward / the Book Notes book slides out, and we dive in and open the page.
    const worlds = Array.from(document.querySelectorAll('.zoom-world'));
    function zoomInto(el) {
        const href = el.getAttribute('href');
        const world = document.querySelector(`.zoom-world[data-for="${el.dataset.zoom}"]`);
        if (!world || reduceMotion.matches) { window.location.href = href; return; }
        if (zooming) return;
        zooming = true;
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
        print.style.transformOrigin = `${gx - box.left}px ${gy - box.top}px`;
        print.style.setProperty('--zoom', `translate(${target.left + target.width / 2 - gx}px, ${target.top + target.height / 2 - gy}px) scale(${scale})`);
        document.documentElement.classList.add('is-zooming');
        root.classList.add('is-zooming');
        // once the room has finished zooming in, the big copy takes over
        let started = false;
        const next = () => {
            if (started) return;
            started = true;
            [
                [0, () => { turnBigGlobe(world); world.classList.add('is-on'); }],   // the big copy fills the screen
                [300, () => world.classList.add('is-turning')],            // spin / come forward / slide out
                [1700, () => world.classList.add('is-diving')],            // and we dive in
                [2600, () => { window.location.href = href; }],
            ].forEach(([ms, fn]) => setTimeout(fn, ms));
        };
        print.addEventListener('transitionend', e => { if (e.target === print) next(); }, { once: true });
        setTimeout(next, 1300);                                            // in case the transition never reports back
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
        print.style.removeProperty('--zoom');
        worlds.forEach(w => w.classList.remove('is-on', 'is-turning', 'is-diving'));
        const bigLand = document.querySelector('.zoom-land');
        if (bigLand) bigLand.style.transform = '';
    });
    picks.forEach(p => {
        if (!p.dataset.zoom) return;
        p.addEventListener('click', e => {
            if (e.defaultPrevented) return;                          // first tap on a phone just shows the label
            e.preventDefault();
            zoomInto(p);
        });
    });

    // ---- the framed photos (after hours) ---------------------------------
    // Every few seconds one frame fades to the next photo, so the wall slowly cycles through all of them.
    const wall = svg.querySelector('.photo-wall');
    if (wall && wall.dataset.photos && !reduceMotion.matches) {
        const all = wall.dataset.photos.split(' ');
        const slots = [1, 0, 2];                               // middle, left, right, middle, ...
        const shown = [0, 1, 2].map(i => wall.querySelector(`.wall-img[data-slot="${i}"]`).getAttribute('href'));
        let turn = 0, pointer = Math.max(...shown.map(h => all.indexOf(h)));
        all.forEach(src => { const im = new Image(); im.src = src; });   // so the fades never show a blank frame
        setInterval(() => {
            if (!isNight() || zooming || document.hidden) return;
            const slot = slots[turn++ % slots.length];
            do { pointer = (pointer + 1) % all.length; } while (shown.includes(all[pointer]) && all.length > 3);
            shown[slot] = all[pointer];
            // the zoomed-in copy follows along, so the dive lands on the photo you clicked
            const imgs = document.querySelectorAll(`.photo-wall .wall-img[data-slot="${slot}"], .zoom-world[data-for="photos"] .wall-img[data-slot="${slot}"]`);
            imgs.forEach(im => im.classList.add('is-fading'));
            setTimeout(() => imgs.forEach(im => { im.setAttribute('href', shown[slot]); im.classList.remove('is-fading'); }), 600);
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
    svg.querySelectorAll('.celestial').forEach(c => {
        c.addEventListener('click', () => setMode(!isNight()));
        c.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setMode(!isNight()); }
        });
    });
    window.addEventListener('hashchange', () => {
        if (location.hash === '#after-hours') setMode(true);
        else if (location.hash === '#daytime') setMode(false);
    });

    place();
    root.classList.add('is-live');
    requestAnimationFrame(tick);
})();
