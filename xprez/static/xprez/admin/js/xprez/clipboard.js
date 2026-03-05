import { getCsrfToken, executeScripts } from './utils.js';

export class XprezClipboardList {
    constructor(adder) {
        this.adder = adder;
        this.triggerEl = adder.el.querySelector('[data-component="xprez-clipboard-list-trigger"]');
        this.listContainerEl = adder.el.querySelector('[data-component="xprez-clipboard-list-container"]');
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
                    executeScripts(this.listContainerEl);
                    this.bindPasteButtons();
                });
        }
    }

    bindPasteButtons() {
        this.listContainerEl.querySelectorAll('[data-component="xprez-clipboard-paste"]').forEach(btn => {
            btn.addEventListener('click', () => this.onPaste(btn));
        });
    }

    onPaste(btn) {
        fetch(btn.dataset.url, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCsrfToken() },
        })
            .then(response => response.json())
            .then(items => {
                items.forEach(({ html }) => this.adder.addFromHtml(html));
                this.hide();
                this.adder.hide();
            });
    }
}
