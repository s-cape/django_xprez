import { XprezSectionConfigDeleter } from './deleters.js';

export class XprezConfigBase {
    constructor(el) {
        this.el = el;
    }
}

export class XprezSectionConfig extends XprezConfigBase {
    constructor(section, ...args) {
        super(...args);
        this.section = section;
        this.deleter = new XprezSectionConfigDeleter(this);
    }
    isDeleted() { return this.deleter.inputEl && this.deleter.inputEl.checked; }
    cssBreakpoint() { return parseInt(this.el.dataset.cssBreakpoint); }
}

export class XprezContentConfig extends XprezConfigBase {
    constructor(content, ...args) {
        super(...args);
        this.content = content;
    }
}

