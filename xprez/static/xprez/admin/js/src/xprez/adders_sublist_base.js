import { xprezGetCsrfToken, xprezExecuteScripts } from './utils.js';

export const WithAdderSublist = (Base) => class extends Base {
    get adder() { return this.parent; }

    loadList() {
        if (!this.triggerEl?.dataset.url) return;
        fetch(this.triggerEl.dataset.url)
            .then(response => response.text())
            .then(html => {
                this.listContainerEl.innerHTML = html;
                this.onListLoaded();
                xprezExecuteScripts(this.listContainerEl);
                this.onLoad();
            });
    }

    onListLoaded() {}
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
};
