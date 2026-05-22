import { xprezGetCsrfToken } from './utils.js';
import { XprezControllerBase } from './controller_base.js';
import { WithAdderSublist } from './adders_sublist_base.js';

export class XprezClipboardList extends WithAdderSublist(XprezControllerBase) {
    constructor(parent, el) {
        super(parent, el);
        this.listContainerEl = this.el;
        this.triggerEl = this.adder.el.querySelector('[data-xprez-clipboard-list-trigger]');
        if (this.triggerEl) {
            this.triggerEl.addEventListener('click', () => this.adder.toggleSublist(this));
        }
        this.xprez.on('clipboard-item-clipped', () => this.onClipboardItemClipped());
        this.xprez.on('clipboard-item-removed', (data) => this.onClipboardItemRemoved(data));
    }

    isOpen() { return !this.listContainerEl.hasAttribute('data-hidden'); }
    show() { this.listContainerEl.removeAttribute('data-hidden'); }
    hide() { this.listContainerEl.setAttribute('data-hidden', ''); }

    onListLoaded() { this.show(); }

    onClipboardItemClipped() {
        if (this.triggerEl) this.triggerEl.removeAttribute('data-hidden');
        if (this.isOpen()) this.loadList();
    }

    onClipboardItemRemoved({ isEmpty }) {
        if (this.isOpen()) {
            this.loadList();
        } else if (isEmpty && this.triggerEl) {
            this.triggerEl.setAttribute('data-hidden', '');
        }
    }

    onLoad() {
        this.listContainerEl.querySelectorAll('[data-xprez-clipboard-paste]').forEach(btn => {
            btn.addEventListener('click', () => this.onPaste(btn));
        });
        this.listContainerEl.querySelectorAll('[data-xprez-clipboard-remove]').forEach(btn => {
            btn.addEventListener('click', () => this.onRemove(btn));
        });
        this.checkEmpty();
    }

    checkEmpty() {
        const remaining = this.listContainerEl.querySelectorAll('.xprez-clipboard-list__item');
        if (!remaining.length) {
            if (this.triggerEl) this.triggerEl.setAttribute('data-hidden', '');
            this.hide();
        }
    }

    onRemove(btn) {
        fetch(btn.dataset.url, {
            method: 'POST',
            headers: { 'X-CSRFToken': xprezGetCsrfToken() },
        })
            .then(response => {
                if (response.ok) {
                    btn.closest('.xprez-clipboard-list__item').remove();
                    this.checkEmpty();
                    const isEmpty = !this.listContainerEl.querySelectorAll('.xprez-clipboard-list__item').length;
                    this.xprez.emit('clipboard-item-removed', { isEmpty });
                }
            });
    }
}
