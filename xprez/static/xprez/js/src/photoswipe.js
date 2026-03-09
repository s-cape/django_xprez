let _pswpPromise = null;

async function getPswpElement() {
    const existing = document.querySelector('[data-photoswipe]');
    if (existing) {
        return existing;
    }
    if (!_pswpPromise) {
        const url = document.querySelector('[data-photoswipe-url]').dataset.photoswipeUrl;
        _pswpPromise = fetch(url)
            .then((r) => r.text())
            .then((html) => {
                const wrapper = document.createElement('div');
                wrapper.innerHTML = html;
                document.body.appendChild(wrapper.firstElementChild);
                return document.querySelector('[data-photoswipe]');
            })
            .catch((err) => {
                console.error('[xprez] Failed to load PhotoSwipe element:', err);
                _pswpPromise = null;
            });
    }
    return _pswpPromise;
}

async function openPhotoSwipe(photos, index) {
    const items = photos.map((el) => ({
        src: el.dataset.original_url,
        w: parseInt(el.dataset.original_width),
        h: parseInt(el.dataset.original_height),
        title: el.dataset.title,
    }));
    const options = {
        history: false,
        focus: false,
        showAnimationDuration: 0,
        hideAnimationDuration: 0,
        index: index,
        shareEl: false,
    };
    const pswpElement = await getPswpElement();
    if (pswpElement) {
        new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, items, options).init();
    }
}

function initGallery() {
    const photos = Array.from(document.querySelectorAll('.js-photo'));
    photos.forEach((el, index) => {
        el.addEventListener('click', (e) => {
            e.preventDefault();
            openPhotoSwipe(photos, index);
        });
    });
}

document.addEventListener('DOMContentLoaded', initGallery);
