// Full-screen photo viewer for the Photos page.
(function () {
    const links = Array.from(document.querySelectorAll('.gallery a[data-index]'));
    const box = document.querySelector('.lightbox');
    if (!links.length || !box) return;

    const img = box.querySelector('.lb-img');
    const text = box.querySelector('.lb-text');
    const count = box.querySelector('.lb-count');
    let index = 0, opener = null;

    function show(i) {
        index = (i + links.length) % links.length;
        const a = links[index];
        box.classList.remove('is-loaded');
        img.onload = () => box.classList.add('is-loaded');
        img.src = a.href;
        img.alt = a.querySelector('img').alt;
        text.textContent = a.dataset.caption || '';
        count.textContent = `${index + 1} / ${links.length}`;
        // warm up the neighbours
        [index + 1, index - 1].forEach(j => { new Image().src = links[(j + links.length) % links.length].href; });
    }

    function open(i) {
        opener = document.activeElement;
        box.hidden = false;
        document.body.classList.add('lb-open');
        requestAnimationFrame(() => box.classList.add('is-open'));
        show(i);
        box.querySelector('.lb-close').focus();
    }

    function close() {
        box.classList.remove('is-open');
        document.body.classList.remove('lb-open');
        setTimeout(() => { box.hidden = true; img.removeAttribute('src'); }, 250);
        if (opener) opener.focus();
    }

    links.forEach(a => a.addEventListener('click', e => { e.preventDefault(); open(+a.dataset.index); }));
    box.querySelector('.lb-close').addEventListener('click', close);
    box.querySelector('.lb-prev').addEventListener('click', () => show(index - 1));
    box.querySelector('.lb-next').addEventListener('click', () => show(index + 1));
    box.addEventListener('click', e => { if (e.target === box || e.target.classList.contains('lb-figure')) close(); });

    document.addEventListener('keydown', e => {
        if (box.hidden) return;
        if (e.key === 'Escape') close();
        if (e.key === 'ArrowRight') show(index + 1);
        if (e.key === 'ArrowLeft') show(index - 1);
        if (e.key === 'Tab') {                       // keep focus inside the viewer
            const f = Array.from(box.querySelectorAll('button'));
            const i = f.indexOf(document.activeElement);
            e.preventDefault();
            f[(i + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
        }
    });

    // swipe on phones
    let sx = null;
    box.addEventListener('touchstart', e => { sx = e.touches[0].clientX; }, { passive: true });
    box.addEventListener('touchend', e => {
        if (sx === null) return;
        const dx = e.changedTouches[0].clientX - sx;
        if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
        sx = null;
    });

    // fade the photos in as they scroll into view
    const io = 'IntersectionObserver' in window && new IntersectionObserver(entries => {
        entries.forEach(en => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.shot').forEach(s => io ? io.observe(s) : s.classList.add('in'));
})();
