import { xprezGetCsrfToken } from './utils.js';
import { XprezControllerBase } from './controller_base.js';

export class XprezClipboardClip extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.el.addEventListener('click', this.onClick.bind(this));
    }

    onClick(e) {
        e.stopPropagation();
        fetch(this.el.dataset.url, {
            method: 'POST',
            headers: { 'X-CSRFToken': xprezGetCsrfToken() },
        }).then(() => {
            this.el.classList.add('success');
            setTimeout(() => {
                this.el.classList.remove('success');
                this.parent.el.removeAttribute('data-open');
            }, 2000);
        });
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
        const clipEl = this.el.querySelector('[data-controller="XprezClipboardClip"]');
        this.mountChild(clipEl);
    }
}

export class XprezSectionCopyMenu extends XprezCopyMenu {}

export class XprezModuleCopyMenu extends XprezCopyMenu {}
