import { XprezSectionPopover } from './popovers.js';
import { XprezAdderSectionBefore, XprezAdderSectionEnd, XprezSectionConfigAdder } from './adders.js';
import { XprezSectionDeleter } from './deleters.js';
import { XprezSectionConfig } from './configs.js';
import { XprezSortable } from './sortable.js';

export class XprezSection {
    constructor(xprez, sectionEl) {
        this.xprez = xprez;
        this.el = sectionEl;
        this.initModules();
        this.popover = new XprezSectionPopover(this);
        this.adderBefore = new XprezAdderSectionBefore(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-before']"), this);
        this.adderEnd = new XprezAdderSectionEnd(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-end']"), this);
        this.deleter = new XprezSectionDeleter(this);

        this.initCollapser();
        this.initConfigs();
        this.initModulesSortable();
    }

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

    initModulesSortable() {
        this.modulesSortable = new XprezSortable(this.gridEl, {
            group: 'xprez-modules',
            handle: '[data-draggable-module-handle]',
            onEnd: () => this.xprez.setPlacementToInputs()
        });
    }
}
