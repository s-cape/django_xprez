import { xprezGetCsrfToken, xprezExecuteScripts } from './utils.js';

export class XprezClipboardList {
    constructor(adder) {
        this.adder = adder;
        this.triggerEl = adder.el.querySelector('[data-xprez-clipboard-list-trigger]');
        this.listContainerEl = adder.el.querySelector('[data-xprez-clipboard-list-container]');
        this.triggerEl.addEventListener('click', this.onTriggerClick.bind(this));
    }

    isOpen() { return !this.listContainerEl.hasAttribute('data-hidden'); }
    show() { this.listContainerEl.removeAttribute('data-hidden'); }
    hide() { this.listContainerEl.setAttribute('data-hidden', ''); }

    onTriggerClick() {
        if (this.isOpen()) {
            this.hide();
        } else {
            fetch(this.triggerEl.dataset.url)
                .then(response => response.text())
                .then(html => {
                    this.listContainerEl.innerHTML = html;
                    this.show();
                    xprezExecuteScripts(this.listContainerEl);
                    this.onLoad();
                });
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
                this.adder.hide();
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
