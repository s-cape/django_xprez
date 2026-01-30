import { XprezModulePopover } from './popovers.js';
import { XprezModuleDeleter } from './deleters.js';
import { XprezModuleConfig, XprezConfigParentMixin } from './configs.js';
import { XprezModuleConfigAdder } from './adders.js';
import { XprezFieldController } from './fields.js';

export class XprezModule {
    constructor(section, moduleEl) {
        this.section = section;
        this.el = moduleEl;
        this.initFields();
        this.popover = new XprezModulePopover(this);
        this.deleter = new XprezModuleDeleter(this);
        this.initConfigs();
    }

    initFields() {
        this.fields = [];
        const popoverEl = this.el.querySelector("[data-component='xprez-module-popover']");
        if (!popoverEl) return;

        const configsContainerEl = popoverEl.querySelector("[data-component='xprez-module-configs']");
        popoverEl.querySelectorAll('[data-component="field"]').forEach(fieldEl => {
            // Skip fields inside configs container
            if (configsContainerEl && configsContainerEl.contains(fieldEl)) return;
            this.fields.push(new XprezFieldController(this, fieldEl));
        });
    }

    getDefault(fieldName) {
        return this.section.xprez.defaults.module[this.contentType()][fieldName];
    }

    initConfigs() {
        this.configsContainerEl = this.el.querySelector("[data-component='xprez-module-configs']");
        this.configs = [];
        this.el.querySelectorAll("[data-component='xprez-module-config']").forEach(
            this.initConfig.bind(this)
        );
        this.configAdder = new XprezModuleConfigAdder(this.section.xprez, this);
    }

    initConfig(configEl) {
        const config = new XprezModuleConfig(this, configEl);
        this.configs.push(config);
        return config;
    }

    contentType() { return this.el.dataset.contentType; }
}

Object.assign(XprezModule.prototype, XprezConfigParentMixin);
