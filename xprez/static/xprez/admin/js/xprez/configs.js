import { XprezSectionConfigDeleter, XprezModuleConfigDeleter } from './deleters.js';
import { XprezShowWhen } from './utils.js';

export class XprezConfigBase {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.initShowWhens();
    }

    initShowWhens() {
        this.el.querySelectorAll("[data-show-when]").forEach(fieldEl => {
            new XprezShowWhen(this, fieldEl);
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
