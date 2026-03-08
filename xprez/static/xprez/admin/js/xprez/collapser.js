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
        this.xprez.allSectionsCollapseExpand?.updateButtonState();
    },
    expand() {
        this.el.removeAttribute("data-collapsed");
        this.persistCollapse();
        this.xprez.allSectionsCollapseExpand?.updateButtonState();
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
        this.updateButtonState();
    }

    updateButtonState() {
        const sections = this.xprez.sections;
        const allCollapsed = sections.length > 0 && sections.every((s) => s.isCollapsed());
        const allExpanded = sections.length === 0 || sections.every((s) => !s.isCollapsed());
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
        for (const section of Object.values(this.xprez.sections)) {
            section.collapse();
        }
        this.updateButtonState();
    }

    expandAll() {
        if (this.expanderEl.hasAttribute("data-hidden")) return;
        for (const section of Object.values(this.xprez.sections)) {
            section.expand();
        }
        this.updateButtonState();
    }
}
