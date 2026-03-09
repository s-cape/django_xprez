import { xprezGetCsrfToken } from './utils.js';
import { XprezControllerBase } from './controller_base.js';

export class XprezClipboardClipBase extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.el.addEventListener('click', this.onClick.bind(this));
    }

    getClipUrls() {
        return [];
    }

    onClipDone() {
        this.xprez.emit('clipboard-clipped');
        this.el.classList.add('success');
        setTimeout(() => {
            this.el.classList.remove('success');
            if (this.parent && this.parent.el) {
                this.parent.el.removeAttribute('data-open');
            }
        }, 2000);
    }

    onClick(e) {
        e.stopPropagation();
        const urls = this.getClipUrls();
        if (urls.length === 0) return;
        const clipRequests = urls.map((url) =>
            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': xprezGetCsrfToken() },
            })
        );
        Promise.all(clipRequests).then(() => this.onClipDone());
    }
}

export class XprezClipboardClipContent extends XprezClipboardClipBase {
    getClipUrls() {
        return this.el.dataset.url ? [this.el.dataset.url] : [];
    }
}

export class XprezClipboardClipContainer extends XprezClipboardClipBase {
    getClipUrls() {
        return this.el.dataset.url ? [this.el.dataset.url] : [];
    }
}

export class XprezCopyMenu extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.initDuplicateAdder();
        this.initSubmenuToggle();
        this.initClipboard();
    }

    initDuplicateAdder() {
        const triggerEl = this.el.querySelector('[data-xprez-duplicate-trigger]');
        this.duplicateAdder = this.mountChild(triggerEl);
    }

    initSubmenuToggle() {
        this.el.addEventListener('click', (e) => {
            e.stopPropagation();
            const isOpen = this.el.hasAttribute('data-open');
            this.el.toggleAttribute('data-open', !isOpen);
            if (!isOpen) {
                const close = (ev) => {
                    if (!this.el.contains(ev.target)) {
                        this.el.removeAttribute('data-open');
                        document.removeEventListener('click', close);
                    }
                };
                document.addEventListener('click', close);
            }
        });
    }

    initClipboard() {
        const clipEl = this.el.querySelector('[data-controller="XprezClipboardClipContent"]');
        this.mountChild(clipEl);
    }
}

export class XprezSectionCopyMenu extends XprezCopyMenu {}

export class XprezModuleCopyMenu extends XprezCopyMenu {}
