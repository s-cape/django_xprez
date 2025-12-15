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
        if (!this.el.dataset.isDefault) {
            this.deleter = new XprezSectionConfigDeleter(this);
        }
    }
}

export class XprezContentConfig extends XprezConfigBase {
    constructor(content, ...args) {
        super(...args);
        this.content = content;
    }
}

