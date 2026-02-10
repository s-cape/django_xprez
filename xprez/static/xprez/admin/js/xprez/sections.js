import { XprezContentBase } from './contents_base.js';
import { XprezSectionPopover } from './popovers.js';
import { XprezAdderSectionBefore, XprezAdderSectionEnd, XprezSectionConfigAdder } from './adders.js';
import { XprezSectionDeleter } from './deleters.js';
import { XprezSectionConfig, XprezConfigParentMixin } from './configs.js';
import { XprezSortable } from './sortable.js';

export class XprezSection extends XprezContentBase {
    constructor(xprez, sectionEl) {
        super(sectionEl);
        this.xprez = xprez;
        this.popover = new XprezSectionPopover(this);
        this.adderBefore = new XprezAdderSectionBefore(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-before']"), this);
        this.adderEnd = new XprezAdderSectionEnd(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-end']"), this);
        this.deleter = new XprezSectionDeleter(this);
        this.initModules();
        this.initFields();
        this.initCollapser();
        this.initConfigs();
        this.initModulesSortable();
        this.initShowWhens();
    }

    get configsContainerSelector() { return "[data-component='xprez-section-configs']"; }
    get configSelector() { return "[data-component='xprez-section-config']"; }
    createConfig(configEl) { return new XprezSectionConfig(this, configEl); }
    createConfigAdder() { return new XprezSectionConfigAdder(this.xprez, this); }

    id() { return this.el.querySelector("[name='section-id']").value; }

    initModules() {
        this.gridEl = this.el.querySelector("[data-component='xprez-section-grid']");
        this.modules = [];
        this.el.querySelectorAll("[data-component='xprez-module']").forEach(
            this.initModule.bind(this)
        );
    }
    initModule(moduleEl) {
        const ControllerClass = window[moduleEl.dataset.jsControllerClass];
        if (!ControllerClass) {
            console.error(`Controller class ${moduleEl.dataset.jsControllerClass} not found`);
            return;
        }
        const module = new ControllerClass(this, moduleEl);
        this.modules.push(module);
    }

    get collapsedIds() {
        try { return JSON.parse(localStorage.getItem("xprez-sections-collapsed") || "[]"); } catch { return []; }
    }
    initCollapser() {
        this.collapserEl = this.el.querySelector("[data-component='xprez-section-collapser']");
        this.collapserEl.addEventListener("click", this.toggleCollapse.bind(this));
        const id = this.id();
        if (id && this.collapsedIds.includes(id)) this.el.setAttribute("data-collapsed", "");
    }
    isCollapsed() { return this.el.hasAttribute("data-collapsed"); }
    collapse() { this.el.setAttribute("data-collapsed", ""); this.persistCollapse(); }
    expand() { this.el.removeAttribute("data-collapsed"); this.persistCollapse(); }
    toggleCollapse() { this.isCollapsed() ? this.expand() : this.collapse(); }
    persistCollapse() {
        const id = this.id();
        if (!id) return;
        let ids = this.collapsedIds.filter(i => i !== id);
        if (this.isCollapsed()) ids.push(id);
        localStorage.setItem("xprez-sections-collapsed", JSON.stringify(ids));
    }

    initModulesSortable() {
        this.modulesSortable = new XprezSortable(this.gridEl, {
            group: 'xprez-modules',
            handle: '[data-draggable-module-handle]',
            onEnd: () => this.xprez.setPlacementToInputs()
        });
    }
}

Object.assign(XprezSection.prototype, XprezConfigParentMixin);
