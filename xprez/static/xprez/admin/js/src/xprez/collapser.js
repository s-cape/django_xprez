import { XprezControllerBase } from "./controller_base.js";

export const XprezCollapserMixin = {
    collapsedIds() {
        try { return JSON.parse(localStorage.getItem(this.collapsedStorageKey) || "[]"); } catch { return []; }
    },
    initCollapser() {
        this.collapserEl = this.el.querySelector("[data-xprez-section-collapser]");
        this.collapserEl.addEventListener("click", this.toggleCollapse.bind(this));
        const id = this.id();
        if (id && this.collapsedIds().includes(id)) this.el.setAttribute("data-collapsed", "");
    },
    isCollapsed() { return this.el.hasAttribute("data-collapsed"); },
    collapse() {
        this.el.setAttribute("data-collapsed", "");
        this.persistCollapse();
        this.xprez.emit('section-collapse-changed');
    },
    expand() {
        this.el.removeAttribute("data-collapsed");
        this.persistCollapse();
        this.xprez.emit('section-collapse-changed');
    },
    toggleCollapse() { this.isCollapsed() ? this.expand() : this.collapse(); },
    persistCollapse() {
        const id = this.id();
        if (!id) return;
        let ids = this.collapsedIds().filter(i => i !== id);
        if (this.isCollapsed()) ids.push(id);
        localStorage.setItem(this.collapsedStorageKey, JSON.stringify(ids));
    },
};

export class XprezAllSectionsCollapseExpand extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.collapserEl = this.el.querySelector("[data-xprez-all-sections-collapser]");
        this.expanderEl = this.el.querySelector("[data-xprez-all-sections-expander]");
        this.collapserEl.addEventListener("click", this.collapseAll.bind(this));
        this.expanderEl.addEventListener("click", this.expandAll.bind(this));
        this.xprez.on("section-collapse-changed", () => this.updateButtonState());
        this.xprez.on("section-rows-changed", () => this.updateButtonState());
        this.updateButtonState();
    }

    _allSectionRows() {
        return [...this.xprez.sections, ...this.xprez.sectionSymlinks];
    }

    updateButtonState() {
        const rows = this._allSectionRows();
        const allCollapsed = rows.length > 0 && rows.every((s) => s.isCollapsed());
        const allExpanded = rows.length === 0 || rows.every((s) => !s.isCollapsed());
        if (allCollapsed) {
            this.collapserEl.setAttribute("data-hidden", "");
        } else {
            this.collapserEl.removeAttribute("data-hidden");
        }
        if (allExpanded) {
            this.expanderEl.setAttribute("data-hidden", "");
        } else {
            this.expanderEl.removeAttribute("data-hidden");
        }
    }

    collapseAll() {
        if (this.collapserEl.hasAttribute("data-hidden")) return;
        for (const row of this._allSectionRows()) {
            row.collapse();
        }
    }

    expandAll() {
        if (this.expanderEl.hasAttribute("data-hidden")) return;
        for (const row of this._allSectionRows()) {
            row.expand();
        }
    }
}
