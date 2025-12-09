export class XprezConfigBase {
    constructor(el) {
        this.el = el;
    }
}

export class XprezSectionConfig extends XprezConfigBase {
    constructor(section, ...args) {
        super(...args);
        this.section = section;
    }
}

export class XprezContentConfig extends XprezConfigBase {
    constructor(content, ...args) {
        super(...args);
        this.content = content;
    }
}

