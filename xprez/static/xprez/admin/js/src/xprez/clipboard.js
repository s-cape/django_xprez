import { xprezGetCsrfToken } from './utils.js';
import { XprezAdderSublistBase } from './adders_sublist_base.js';

export class XprezClipboardList extends XprezAdderSublistBase {
    constructor(parent, el) {
        super(parent, el);
        this.xprez.on('clipboard-clipped', () => this.onClipboardClipped());
    }

    findTriggerEl() {
        return this.adder.el.querySelector('[data-xprez-clipboard-list-trigger]');
    }

    onClipboardClipped() {
        if (this.triggerEl) this.triggerEl.removeAttribute('data-hidden');
        if (this.isOpen()) this.loadList();
    }

    onLoad() {
        this.emptyEl = this.listContainerEl.querySelector('[data-xprez-clipboard-empty]');
        this.listContainerEl.querySelectorAll('[data-xprez-clipboard-paste]').forEach(btn => {
            btn.addEventListener('click', () => this.onPaste(btn));
        });
        this.listContainerEl.querySelectorAll('[data-xprez-clipboard-remove]').forEach(btn => {
            btn.addEventListener('click', () => this.onRemove(btn));
        });
    }

    checkEmpty() {
        const remaining = this.listContainerEl.querySelectorAll('.xprez-clipboard-list__item');
        if (!remaining.length) {
            this.emptyEl.removeAttribute('data-hidden');
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
                }
            });
    }
}
