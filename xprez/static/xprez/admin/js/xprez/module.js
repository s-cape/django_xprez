import { XprezModulePopover } from './popovers.js';
import { XprezModuleDeleter } from './deleters.js';
import { XprezModuleConfig } from './configs.js';
import { XprezModuleConfigAdder } from './adders.js';

export class XprezModule {
    constructor(section, moduleEl) {
        this.section = section;
        this.el = moduleEl;
        this.popover = new XprezModulePopover(this);
        this.deleter = new XprezModuleDeleter(this);
        this.initConfigs();
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
}
