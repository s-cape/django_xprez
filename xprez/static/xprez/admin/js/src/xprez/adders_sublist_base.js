import { xprezGetCsrfToken, xprezExecuteScripts } from './utils.js';
import { XprezControllerBase } from './controller_base.js';

export class XprezAdderSublistBase extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.listContainerEl = this.el;
        this.triggerEl = this.findTriggerEl();
        if (this.triggerEl) {
            this.triggerEl.addEventListener('click', this.onTriggerClick.bind(this));
        }
    }

    get adder() { return this.parent; }

    findTriggerEl() { return null; }

    isOpen() { return !this.listContainerEl.hasAttribute('data-hidden'); }
    show() { this.listContainerEl.removeAttribute('data-hidden'); }
    hide() { this.listContainerEl.setAttribute('data-hidden', ''); }

    loadList() {
        if (!this.triggerEl?.dataset.url) { return; }
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
        this.adder.toggleSublist(this);
    }

    onLoad() {}

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
}
