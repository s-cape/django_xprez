export const XprezCollapserMixin = {
    collapsedIds() {
        try { return JSON.parse(localStorage.getItem(this.collapsedStorageKey) || "[]"); } catch { return []; }
    },
    initCollapser() {
        this.collapserEl = this.el.querySelector("[data-component='xprez-section-collapser']");
        this.collapserEl.addEventListener("click", this.toggleCollapse.bind(this));
        const id = this.id();
        if (id && this.collapsedIds().includes(id)) this.el.setAttribute("data-collapsed", "");
    },
    isCollapsed() { return this.el.hasAttribute("data-collapsed"); },
    collapse() { this.el.setAttribute("data-collapsed", ""); this.persistCollapse(); },
    expand() { this.el.removeAttribute("data-collapsed"); this.persistCollapse(); },
    toggleCollapse() { this.isCollapsed() ? this.expand() : this.collapse(); },
    persistCollapse() {
        const id = this.id();
        if (!id) return;
        let ids = this.collapsedIds().filter(i => i !== id);
        if (this.isCollapsed()) ids.push(id);
        localStorage.setItem(this.collapsedStorageKey, JSON.stringify(ids));
    },
};
