import { xprezGetCsrfToken, xprezExecuteScripts } from './utils.js';
import { XprezControllerBase } from './controller_base.js';

export class XprezClipboardList extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.listContainerEl = this.el;
        this.triggerEl = this.el.nextElementSibling?.querySelector(
            '[data-xprez-clipboard-list-trigger]'
        );
        if (this.triggerEl) {
            this.triggerEl.addEventListener('click', this.onTriggerClick.bind(this));
        }
        this.xprez.on('clipboard-clipped', () => this.onClipboardClipped());
    }

    get adder() {
        return this.parent;
    }

    isOpen() { return !this.listContainerEl.hasAttribute('data-hidden'); }
    show() { this.listContainerEl.removeAttribute('data-hidden'); }
    hide() { this.listContainerEl.setAttribute('data-hidden', ''); }

    onClipboardClipped() {
        if (this.triggerEl) this.triggerEl.removeAttribute('data-hidden');
        if (this.isOpen()) this.loadList();
    }

    loadList() {
        if (!this.triggerEl?.dataset.url) return;
        fetch(this.triggerEl.dataset.url)
            .then(response => response.text())
            .then(html => {
                this.listContainerEl.innerHTML = html;
                this.show();
                xprezExecuteScripts(this.listContainerEl);
                this.onLoad();
            });
    }

    onTriggerClick() {
        if (this.isOpen()) {
            this.hide();
        } else {
            this.loadList();
        }
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

    onPaste(btn) {
        fetch(btn.dataset.url, {
            method: 'POST',
            headers: { 'X-CSRFToken': xprezGetCsrfToken() },
        })
            .then(response => response.json())
            .then(items => {
                items.forEach(({ html }) => this.adder.addFromHtml(html));
                this.hide();
                this.adder.hide?.();
            });
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
