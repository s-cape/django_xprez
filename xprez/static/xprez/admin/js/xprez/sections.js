import { XprezContentBase } from './contents_base.js';
import { XprezSectionDeleter } from './deleters.js';
import { XprezConfigParentMixin } from './configs.js';
import { XprezSortable } from './sortable.js';
import { XprezShortcutParentMixin } from './shortcuts.js';
import { XprezCollapserMixin } from './collapser.js';
import { XprezControllerBase } from './controller_base.js';

export class XprezSectionSymlink extends XprezControllerBase {
    constructor(xprez, el) {
        super(xprez, el);
        this.deleter = new XprezSectionDeleter(this);
        this.adderBefore = this.mountChild(this.el.querySelector("[data-controller='XprezSectionAdderSectionBefore']"));
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
        super(xprez, sectionEl);
        this.deleter = new XprezSectionDeleter(this);
        this.popover = this.mountChild(this.el.querySelector("[data-controller='XprezSectionPopover']"));
        this.adderBefore = this.mountChild(this.el.querySelector("[data-controller='XprezSectionAdderSectionBefore']"));
        this.adderEnd = this.mountChild(this.el.querySelector("[data-controller='XprezModuleAdderSectionEnd']"));
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
        return [...super.unmanagedContainers, this.gridEl];
    }

    get configsContainerSelector() { return "[data-xprez-section-configs]"; }
    get configSelector() { return "[data-controller='XprezSectionConfig']"; }
    createConfig(configEl) { return this.mountChild(configEl); }
    createConfigAdder() { return this.mountChild(this.el.querySelector("[data-controller='XprezSectionConfigAdder']")); }

    id() { return this.el.querySelector("[name='section-id']").value; }
    get collapsedStorageKey() { return "xprez-sections-collapsed"; }

    initModules() {
        this.gridEl = this.el.querySelector("[data-xprez-section-grid]");
        this.modules = [];
        Array.from(this.gridEl.children).forEach(this.initModule.bind(this));
    }

    initModule(moduleEl) {
        const module = this.mountChild(moduleEl);
        this.modules.push(module);
        return module;
    }

    initCopyMenus() {
        this.el.querySelectorAll('[data-controller="XprezSectionCopyMenu"]').forEach(el => {
            if (this.isUnmanaged(el)) return;
            this.mountChild(el);
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
