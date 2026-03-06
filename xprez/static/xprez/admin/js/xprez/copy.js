import { xprezGetCsrfToken } from './utils.js';
import { XprezSectionDuplicateAdder, XprezModuleDuplicateAdder } from './adders.js';

export class XprezClipboardClip {
    constructor(el, copyMenu) {
        this.el = el;
        this.copyMenu = copyMenu;
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
                this.copyMenu.el.removeAttribute('data-open');
            }, 2000);
        });
    }
}

export class XprezCopyMenu {
    constructor(el, parent) {
        this.el = el;
        this.parent = parent;
        this.initDuplicateAdder();
        this.initSubmenuToggle();
        this.initClipboard();
    }

    initDuplicateAdder() {
        this.duplicateAdder = new (this.duplicateAdderClass)(
            this.parent.xprez,
            this.el.querySelector('[data-component="xprez-duplicate-trigger"]'),
            this
        );
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
        const clipEl = this.el.querySelector('[data-component="xprez-clipboard-clip"]');
        new XprezClipboardClip(clipEl, this);
    }
}

export class XprezSectionCopyMenu extends XprezCopyMenu {
    get duplicateAdderClass() { return XprezSectionDuplicateAdder; }
}

export class XprezModuleCopyMenu extends XprezCopyMenu {
    get duplicateAdderClass() { return XprezModuleDuplicateAdder; }
}
