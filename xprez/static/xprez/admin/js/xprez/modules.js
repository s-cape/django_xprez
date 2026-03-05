import { XprezContentBase } from './contents_base.js';
import { XprezModulePopover } from './popovers.js';
import { XprezModuleDeleter } from './deleters.js';
import { XprezModuleConfig, XprezConfigParentMixin } from './configs.js';
import { XprezModuleConfigAdder } from './adders.js';
import { resolveFieldControllerClass } from './fields.js';
import { XprezModuleSyncMixin } from './sync.js';
import { XprezShortcutParentMixin } from './shortcuts.js';

export class XprezModule extends XprezContentBase {
    constructor(section, moduleEl) {
        super(moduleEl);
        this.section = section;
        this.popover = new XprezModulePopover(this);
        this.deleter = new XprezModuleDeleter(this);
        this.initFields();
        this.initConfigs();
        this.initShowWhens();
        this.initSync();
        this.initShortcuts();
    }

    initFields() {
        this.fields = [];
        this.el.querySelectorAll('[data-component="field"]').forEach((fieldEl) => {
            if (this.configsContainerEl?.contains(fieldEl)) return;
            this.initField(fieldEl);
        });
    }

    initField(fieldEl) {
        const field = new (resolveFieldControllerClass(fieldEl))(this, fieldEl);
        this.fields.push(field);
        return field;
    }

    get configsContainerSelector() { return "[data-component='xprez-module-configs']"; }
    get configSelector() { return "[data-component='xprez-module-config']"; }
    createConfig(configEl) { return new XprezModuleConfig(this, configEl); }
    createConfigAdder() { return new XprezModuleConfigAdder(this.section.xprez, this); }

    get xprez() { return this.section.xprez; }

    contentType() { return this.el.dataset.contentType; }
}

Object.assign(XprezModule.prototype, XprezConfigParentMixin, XprezModuleSyncMixin, XprezShortcutParentMixin);
