import { XprezContentBase } from './contents_base.js';
import { XprezModulePopover } from './popovers.js';
import { XprezModuleDeleter } from './deleters.js';
import { XprezModuleConfig, XprezConfigParentMixin } from './configs.js';
import { XprezModuleConfigAdder } from './adders.js';

export class XprezModule extends XprezContentBase {
    constructor(section, moduleEl) {
        super(moduleEl);
        this.section = section;
        this.popover = new XprezModulePopover(this);
        this.deleter = new XprezModuleDeleter(this);
        this.initFields();
        this.initConfigs();
        this.initShowWhens();
    }

    get configsContainerSelector() { return "[data-component='xprez-module-configs']"; }
    get configSelector() { return "[data-component='xprez-module-config']"; }
    createConfig(configEl) { return new XprezModuleConfig(this, configEl); }
    createConfigAdder() { return new XprezModuleConfigAdder(this.section.xprez, this); }

    contentType() { return this.el.dataset.contentType; }
}

Object.assign(XprezModule.prototype, XprezConfigParentMixin);
