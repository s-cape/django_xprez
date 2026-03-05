import { XprezContentBase } from './contents_base.js';
import { XprezSectionPopover } from './popovers.js';
import { XprezSectionAdderSectionBefore, XprezModuleAdderSectionEnd, XprezSectionConfigAdder } from './adders.js';
import { XprezSectionCopyMenu } from './copy.js';
import { XprezSectionDeleter } from './deleters.js';
import { XprezSectionConfig, XprezConfigParentMixin } from './configs.js';
import { XprezSortable } from './sortable.js';
import { XprezShortcutParentMixin } from './shortcuts.js';
import { XprezCollapserMixin } from './collapser.js';

export class XprezSectionSymlink {
    constructor(xprez, el) {
        this.xprez = xprez;
        this.el = el;
        this.deleter = new XprezSectionDeleter(this);
        this.adderBefore = new XprezSectionAdderSectionBefore(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-before']"), this);
        this.initCollapser();
    }

    id() { return this.el.querySelector("[name='section-symlink-id']").value; }
    get collapsedStorageKey() { return "xprez-section-symlinks-collapsed"; }
    get modules() { return []; }
    get popover() { return null; }
}

Object.assign(XprezSectionSymlink.prototype, XprezCollapserMixin);

export class XprezSection extends XprezContentBase {
    constructor(xprez, sectionEl) {
        super(sectionEl);
        this.xprez = xprez;
        this.deleter = new XprezSectionDeleter(this);
        this.popover = new XprezSectionPopover(this);
        this.adderBefore = new XprezSectionAdderSectionBefore(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-before']"), this);
        this.adderEnd = new XprezModuleAdderSectionEnd(this.xprez, this.el.querySelector("[data-component='xprez-adder-section-end']"), this);
        this.initModules();
        this.initFields();
        this.initCollapser();
        this.initConfigs();
        this.initModulesSortable();
        this.initShowWhens();
        this.initShortcuts();
        this.initCopyMenus();
    }

    get unmanagedContainers() {
        return [this.gridEl, this.configsContainerEl].filter(Boolean);
    }

    get configsContainerSelector() { return "[data-component='xprez-section-configs']"; }
    get configSelector() { return "[data-component='xprez-section-config']"; }
    createConfig(configEl) { return new XprezSectionConfig(this, configEl); }
    createConfigAdder() { return new XprezSectionConfigAdder(this.xprez, this); }

    id() { return this.el.querySelector("[name='section-id']").value; }
    get collapsedStorageKey() { return "xprez-sections-collapsed"; }

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
        return module;
    }

    initCopyMenus() {
        this.el.querySelectorAll('[data-component="xprez-copy-menu"]').forEach(el => {
            if (this.isUnmanaged(el)) return;
            new XprezSectionCopyMenu(el, this);
        });
    }

    initModulesSortable() {
        this.modulesSortable = new XprezSortable(this.gridEl, {
            group: 'xprez-modules',
            handle: '[data-draggable-module-handle]',
            onEnd: () => this.xprez.setPlacementToInputs()
        });
    }
}

Object.assign(XprezSection.prototype, XprezCollapserMixin, XprezConfigParentMixin, XprezShortcutParentMixin);
