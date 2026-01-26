import { XprezSectionConfigDeleter, XprezModuleConfigDeleter } from './deleters.js';
import { XprezCustomToggle } from './utils.js';

export class XprezConfigBase {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.initCustomToggles();
    }

    initCustomToggles() {
        this.el.querySelectorAll("[data-custom-toggle-select]").forEach(fieldEl => {
            new XprezCustomToggle(this, fieldEl);
        });
    }

    isDeleted() { return this.deleter.inputEl && this.deleter.inputEl.checked; }
    cssBreakpoint() { return parseInt(this.el.dataset.cssBreakpoint); }
}

export class XprezSectionConfig extends XprezConfigBase {
    constructor(section, el) {
        super(section, el);
        this.section = section;
        this.deleter = new XprezSectionConfigDeleter(this);
    }
}

export class XprezModuleConfig extends XprezConfigBase {
    constructor(module, el) {
        super(module, el);
        this.module = module;
        this.deleter = new XprezModuleConfigDeleter(this);
    }
}
