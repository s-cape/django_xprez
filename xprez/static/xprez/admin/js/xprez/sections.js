import { XprezSectionPopover } from './popovers.js';
import { XprezAdderSectionBefore, XprezAdderSectionEnd, XprezSectionConfigAdder } from './adders.js';
import { XprezSectionDeleter } from './deleters.js';
import { XprezSectionConfig } from './configs.js';
import { XprezSortable } from './sortable.js';

export class XprezSection {
    constructor(xprez, sectionEl) {
        this.xprez = xprez;
        this.el = sectionEl;
        this.initContents();
        this.popover = new XprezSectionPopover(this);
        this.adderBefore = new XprezAdderSectionBefore(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-before']"), this);
        this.adderEnd = new XprezAdderSectionEnd(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-end']"), this);
        this.deleter = new XprezSectionDeleter(this);

        this.initCollapser();
        this.initConfigs();
        this.initContentsSortable();
    }

    id() { return this.el.querySelector("[name='section-id']").value; }

    initContents() {
        this.gridEl = this.el.querySelector("[data-component='xprez-section-grid']");
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
        this.configsContainerEl = this.el.querySelector("[data-component='xprez-section-configs']");
        this.configs = [];
        this.el.querySelectorAll("[data-component='xprez-section-config']").forEach(
            this.initConfig.bind(this)
        );
        this.configAdder = new XprezSectionConfigAdder(this.xprez, this);
    }
    initConfig(configEl) {
        const config = new XprezSectionConfig(this, configEl);
        this.configs.push(config);
        return config;
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
