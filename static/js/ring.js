// The homepage sushi belt: a ring of plates that turns to bring one into the spotlight.
(function () {
    const root = document.querySelector('[data-ring]');
    if (!root) return;

    const AUTO_EVERY = 4000;    // ms between automatic turns (0 = off)
    const stage = root.querySelector('.stage');
    const plates = Array.from(stage.querySelectorAll('.plate'));
    const dots = Array.from(root.querySelectorAll('.dot'));
    const n = plates.length;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    const caption = {
        box: root.querySelector('.caption'),
        title: root.querySelector('.caption-title'),
        sub: root.querySelector('.caption-sub'),
        cta: root.querySelector('.caption-cta'),
    };

    let angle = 0;      // where the ring is now (in plates)
    let target = 0;     // where it is heading
    let front = -1;
    let hovering = false, focused = false, dragging = null;
    let lastTurn = performance.now();
    let size = {};

    const mod = (a, m) => ((a % m) + m) % m;
    const wrap = d => { d = mod(d + n / 2, n) - n / 2; return d; };   // shortest way round

    const svg = stage.querySelector('.belt');
    const part = name => svg.querySelector('.' + name);
    const SLATS = 72;

    function measure() {
        const W = stage.clientWidth, H = stage.clientHeight;
        const small = W < 640;
        const rx = Math.min(W * (small ? 0.40 : 0.38), 460);   // ring radius (side to side)
        const k = small ? 0.42 : 0.34;                          // how flat the ring looks
        size = {
            W, H, rx, k,
            ry: rx * k,
            band: small ? 46 : 80,                              // half the belt width
            thick: small ? 10 : 16,                             // belt edge thickness
            cx: W / 2,
            cy: H * 0.5,
        };
        svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
        const { cx, cy, band, thick } = size;
        const ell = (a, b, dy = 0) =>
            `M${cx - a} ${cy + dy} A${a} ${b} 0 1 0 ${cx + a} ${cy + dy} A${a} ${b} 0 1 0 ${cx - a} ${cy + dy}Z`;
        const oa = rx + band, ob = (rx + band) * k;
        const ia = rx - band, ib = (rx - band) * k;
        part('belt-side').setAttribute('d', ell(oa, ob, thick));
        part('belt-top').setAttribute('d', ell(oa, ob) + ell(ia, ib));
        part('belt-rail').setAttribute('d', ell(oa, ob) + ell(ia, ib));
        part('counter').setAttribute('d', ell(ia - 10, ib - 10 * k));

        // spotlight lands where the front plate sits
        stage.style.setProperty('--spot-x', `${cx}px`);
        stage.style.setProperty('--spot-y', `${cy + rx * k}px`);
        stage.style.setProperty('--spot-w', `${band * 2.6}px`);
    }

    function drawSlats() {
        const { cx, cy, rx, k, band } = size;
        const turn = (angle / n) * Math.PI * 2;
        let d = '';
        for (let j = 0; j < SLATS; j++) {
            const t = (j / SLATS) * Math.PI * 2 - turn;
            const s = Math.sin(t), c = Math.cos(t);
            const ia = rx - band + 3, oa = rx + band - 3;
            d += `M${(cx + ia * s).toFixed(1)} ${(cy + ia * k * c).toFixed(1)}L${(cx + oa * s).toFixed(1)} ${(cy + oa * k * c).toFixed(1)}`;
        }
        part('belt-slats').setAttribute('d', d);
    }

    function render() {
        const { cx, cy, rx, ry } = size;
        plates.forEach((plate, i) => {
            const d = wrap(i - angle);
            const phi = (d / n) * Math.PI * 2;
            const c = Math.cos(phi), s = Math.sin(phi);
            const depth = (c + 1) / 2;                      // 1 front … 0 back
            const x = cx + rx * s;
            const y = cy + ry * c;
            const scale = 0.66 + 0.34 * depth;
            plate.style.transform =
                `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px) translate(-50%, -78%) scale(${scale.toFixed(3)})`;
            const lit = Math.exp(-(d * d) / 0.12);          // 1 inside the spotlight, 0 outside
            plate.style.filter = `brightness(${(0.42 + 0.48 * depth + 0.28 * lit).toFixed(3)})`;
            plate.style.zIndex = Math.round(100 + y);
        });
        drawSlats();

        const f = mod(Math.round(angle), n);
        if (f !== front) setFront(f);
    }

    function setFront(f) {
        const first = front === -1;
        front = f;
        if (!first) {                                       // the light flickers onto the new plate
            stage.classList.remove('spot-swap');
            void stage.offsetWidth;
            stage.classList.add('spot-swap');
        }
        plates.forEach((p, i) => {
            p.classList.toggle('is-front', i === f);
            p.tabIndex = i === f ? 0 : -1;
        });
        dots.forEach((d, i) => d.setAttribute('aria-current', i === f ? 'true' : 'false'));

        const plate = plates[f];
        caption.box.classList.remove('show');
        void caption.box.offsetWidth;                         // restart fade
        caption.title.textContent = plate.dataset.title;
        caption.sub.textContent = plate.dataset.sub;
        if (plate.dataset.href) {
            caption.cta.textContent = plate.dataset.external ? 'Visit ↗' : 'Open →';
            caption.cta.href = plate.dataset.href;
            caption.cta.target = plate.dataset.external ? '_blank' : '';
            caption.cta.rel = plate.dataset.external ? 'noopener' : '';
            caption.cta.classList.remove('is-soon');
            caption.cta.removeAttribute('aria-disabled');
        } else {
            caption.cta.textContent = 'Coming soon';
            caption.cta.removeAttribute('href');
            caption.cta.classList.add('is-soon');
            caption.cta.setAttribute('aria-disabled', 'true');
        }
        caption.box.classList.add('show');
    }

    function go(step) { target = Math.round(target) + step; lastTurn = performance.now(); }
    function goTo(i) { target = Math.round(target) + wrap(i - mod(Math.round(target), n)); lastTurn = performance.now(); }

    let last = performance.now();
    function tick(t) {
        const dt = Math.min((t - last) / 1000, 0.1);
        last = t;

        const still = hovering || focused || dragging || reduceMotion.matches;
        if (AUTO_EVERY && !still && t - lastTurn > AUTO_EVERY) go(1);
        // after a pause, wait a moment before turning again
        if (still) lastTurn = Math.max(lastTurn, t - AUTO_EVERY + 1200);

        const k = reduceMotion.matches ? 1 : 1 - Math.exp(-dt * 6);
        angle += (target - angle) * k;
        if (Math.abs(target - angle) < 0.0005) angle = target;
        render();
        requestAnimationFrame(tick);
    }

    // ---- controls -------------------------------------------------------
    root.querySelector('.nav--prev').addEventListener('click', () => go(-1));
    root.querySelector('.nav--next').addEventListener('click', () => go(1));
    dots.forEach((d, i) => d.addEventListener('click', () => goTo(i)));

    stage.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight') { go(1); e.preventDefault(); }
        if (e.key === 'ArrowLeft') { go(-1); e.preventDefault(); }
    });

    plates.forEach((plate, i) => {
        plate.addEventListener('click', e => {
            if (stage.dataset.dragged) { e.preventDefault(); return; }
            if (i !== front) { e.preventDefault(); goTo(i); }    // side plate: bring it round
        });
    });

    stage.addEventListener('pointerenter', () => { hovering = true; });
    stage.addEventListener('pointerleave', () => { hovering = false; });
    root.addEventListener('focusin', () => { focused = true; });
    root.addEventListener('focusout', () => { focused = false; });

    // drag / swipe to spin
    stage.addEventListener('pointerdown', e => {
        dragging = { x: e.clientX, start: target, moved: false };
        delete stage.dataset.dragged;
    });
    window.addEventListener('pointermove', e => {
        if (!dragging) return;
        const dx = e.clientX - dragging.x;
        if (Math.abs(dx) > 6) dragging.moved = true;
        if (dragging.moved) target = dragging.start - dx / (size.rx * 0.9);
    });
    window.addEventListener('pointerup', () => {
        if (!dragging) return;
        if (dragging.moved) { stage.dataset.dragged = '1'; setTimeout(() => delete stage.dataset.dragged, 50); }
        target = Math.round(target);
        dragging = null;
        lastTurn = performance.now();
    });

    window.addEventListener('resize', () => { measure(); render(); });

    measure();
    root.classList.add('is-live');
    render();
    requestAnimationFrame(tick);
})();
