import { XprezSectionPopover } from './popovers.js';
import { XprezAddSectionBefore, XprezAddSectionEnd, XprezSectionConfigAdder } from './adders.js';
import { XprezSectionDeleter } from './deleters.js';
import { XprezSectionConfig } from './configs.js';
import { XprezSortable } from './sortable.js';

export class XprezSection {
    constructor(xprez, sectionEl) {
        this.xprez = xprez;
        this.el = sectionEl;
        this.gridEl = this.el.querySelector("[data-component='xprez-section-grid']");
        this.initContents();
        this.popover = new XprezSectionPopover(this);
        this.addSectionBefore = new XprezAddSectionBefore(this.xprez, this.el.querySelector("[data-component='xprez-add-section-before']"), this);
        this.addSectionEnd = new XprezAddSectionEnd(this.xprez, this.el.querySelector("[data-component='xprez-add-section-end']"), this);
        this.deleter = new XprezSectionDeleter(this);

        this.initCollapser();
        this.initConfigs();
        this.initConfigAdder();
        this.initContentsSortable();
    }

    id() { return this.el.querySelector("[name='section-id']").value; }

    initContents() {
        this.contents = [];
        this.el.querySelectorAll("[data-component='xprez-content']").forEach(
            this.initContent.bind(this)
        );
    }
    initContent(contentEl) {
        const ControllerClass = window[contentEl.dataset.jsControllerClass];
        if (!ControllerClass) {
            console.error(`Controller class ${contentEl.dataset.jsControllerClass} not found`);
            return;
        }
        const content = new ControllerClass(this, contentEl);
        this.contents.push(content);
    }

    initConfigs() {
        this.configs = [];
        this.el.querySelectorAll("[data-component='xprez-section-config']").forEach(
            this.initConfig.bind(this)
        );
    }
    initConfig(configEl) {
        this.configs.push(new XprezSectionConfig(this, configEl));
    }

    initConfigAdder() {
        this.configAdder = new XprezSectionConfigAdder(this.xprez, this);
    }

    initCollapser() {
        this.collapserEl = this.el.querySelector("[data-component='xprez-section-collapser']");
        this.collapserEl.addEventListener("click", this.toggleCollapse.bind(this));
    }
    isCollapsed() { return this.el.hasAttribute("data-collapsed"); }
    collapse() { this.el.setAttribute("data-collapsed", ""); }
    expand() { this.el.removeAttribute("data-collapsed"); }
    toggleCollapse() { this.isCollapsed() ? this.expand() : this.collapse(); }

    initContentsSortable() {
        this.contentsSortable = new XprezSortable(this.gridEl, {
            group: 'xprez-contents',
            handle: '[data-draggable-content-handle]',
            onEnd: () => this.xprez.setPlacementToInputs()
        });
    }
}

