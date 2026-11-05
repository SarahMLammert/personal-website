// The homepage sushi belt: plates ride around the conveyor in the illustration.
// Hover or focus a plate to stop the belt and see where it goes; click to open it.
(function () {
    const root = document.querySelector('[data-belt]');
    if (!root) return;

    const SPEED = 55;                 // canvas units per second
    const svg = root.querySelector('svg');
    const line = svg.querySelector('#belt-line');
    const slats = svg.querySelector('.belt-slats');
    const back = svg.querySelector('#plates-back');
    const front = svg.querySelector('#plates-front');
    const plates = Array.from(svg.querySelectorAll('.belt-plate'));
    const tag = root.querySelector('.plate-tag');
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const touch = window.matchMedia('(hover: none)');

    const length = line.getTotalLength();
    const gap = length / plates.length;
    const TOP = 520, BOTTOM = 680;    // the belt's back and front straights
    let offset = 0, held = null, last = null;

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
        if (last !== null && !held && !reduceMotion.matches) {
            offset = (offset + SPEED * Math.min((t - last) / 1000, 0.1)) % length;
            place();
        }
        last = t;
        requestAnimationFrame(tick);
    }

    function show(p) {
        held = p;
        tag.querySelector('strong').textContent = p.dataset.title + (p.dataset.external ? ' ↗' : '');
        tag.querySelector('span').textContent = p.dataset.sub;
        tag.hidden = false;
        const box = root.getBoundingClientRect();
        const r = p.querySelector('.plate-art').getBoundingClientRect();
        tag.style.left = `${r.left + r.width / 2 - box.left}px`;
        tag.style.top = `${r.top - box.top}px`;
        p.classList.add('is-held');
    }

    function hide() {
        if (held) held.classList.remove('is-held');
        held = null;
        tag.hidden = true;
    }

    plates.forEach(p => {
        p.addEventListener('pointerenter', e => { if (e.pointerType !== 'touch') show(p); });
        p.addEventListener('pointerleave', e => { if (e.pointerType !== 'touch') hide(); });
        p.addEventListener('focus', () => show(p));
        p.addEventListener('blur', hide);
        // on touch screens the first tap stops the belt and shows the label, the second opens it
        p.addEventListener('click', e => {
            if (touch.matches && held !== p) { e.preventDefault(); show(p); }
        });
    });
    document.addEventListener('click', e => { if (held && !e.target.closest('.belt-plate')) hide(); });
    window.addEventListener('resize', () => { if (held) show(held); });

    place();
    root.classList.add('is-live');
    requestAnimationFrame(tick);
})();
