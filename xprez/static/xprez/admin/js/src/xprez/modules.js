import { XprezContentBase } from './contents_base.js';
import { XprezModuleDeleter } from './deleters.js';
import { XprezConfigParentMixin } from './configs.js';
import { resolveFieldControllerClass } from './fields.js';
import { XprezModuleSyncMixin } from './sync.js';
import { XprezShortcutParentMixin } from './shortcuts.js';

export { XprezModuleSyncMixin };

export class XprezModule extends XprezContentBase {
    static KEY = "module";
    constructor(section, moduleEl) {
        super(section, moduleEl);
        this.popover = this.mountChild(this.el.querySelector("[data-controller='XprezModulePopover']"));
        this.deleter = new XprezModuleDeleter(this);
        this.initFields();
        this.initConfigs();
        this.initShowWhens();
        this.initSync();
        this.initShortcuts();
        this.initCopyMenus();
    }

    initFields() {
        this.fields = [];
        this.el.querySelectorAll('[data-xprez-field]').forEach((fieldEl) => {
            if (this.isUnmanaged(fieldEl)) return;
            this.initField(fieldEl);
        });
    }

    initField(fieldEl) {
        const field = new (resolveFieldControllerClass(fieldEl))(this, fieldEl);
        this.fields.push(field);
        return field;
    }

    get configsContainerSelector() { return "[data-xprez-module-configs]"; }
    get configSelector() { return "[data-controller='XprezModuleConfig']"; }
    createConfig(configEl) { return this.mountChild(configEl); }
    createConfigAdder() { return this.mountChild(this.el.querySelector("[data-controller='XprezModuleConfigAdder']")); }

    initCopyMenus() {
        this.el.querySelectorAll('[data-controller="XprezModuleCopyMenu"]').forEach(el => {
            if (this.isUnmanaged(el)) return;
            this.mountChild(el);
        });
    }

    contentType() { return this.el.dataset.contentType; }
}

Object.assign(XprezModule.prototype, XprezConfigParentMixin, XprezModuleSyncMixin, XprezShortcutParentMixin);
