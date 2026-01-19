import { XprezSectionConfigDeleter, XprezModuleConfigDeleter } from './deleters.js';

export class XprezConfigBase {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
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
