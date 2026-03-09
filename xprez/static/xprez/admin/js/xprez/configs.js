import { XprezSectionConfigDeleter, XprezModuleConfigDeleter } from './deleters.js';
import { resolveFieldControllerClass, XprezFieldLink, XprezShowWhen } from './fields.js';
import { XprezControllerBase } from './controller_base.js';

/** Mixin for Section/Module that own configs. Apply via Object.assign(Class.prototype, XprezConfigParentMixin) */
export const XprezConfigParentMixin = {
    getConfigsOrdered() {
        return [...this.configs]
            .filter(c => !c.isDeleted())
            .sort((a, b) => a.cssBreakpoint() - b.cssBreakpoint());
    },
    updateConfigFieldsActive() {
        for (const config of this.configs) {
            for (const field of config.fields) {
                field.refreshActive();
            }
        }
    }
};

export class XprezConfigBase extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.initFields();
        this.initShowWhens();
        this.initFieldLinks();
    }

    initField(fieldEl) {
        const field = new (resolveFieldControllerClass(fieldEl))(this, fieldEl);
        this.fields.push(field);
        return field;
    }

    initFields() {
        this.fields = [];
        this.el.querySelectorAll('[data-xprez-field]').forEach(fieldEl => this.initField(fieldEl));
    }

    initShowWhens() {
        this.el.querySelectorAll("[data-show-when]").forEach(fieldEl => {
            new XprezShowWhen(this, fieldEl);
        });
    }

    initFieldLinks() {
        this.fieldLinks = [];
        this.el.querySelectorAll("[data-field-link]").forEach(el => {
            this.fieldLinks.push(new XprezFieldLink(this, el));
        });
    }

    getFields(fieldName) {
        return this.fields.filter(f => f.fieldName === fieldName);
    }

    getFieldByInputName(htmlName) {
        return this.fields.find(f => f.inputEl && f.inputEl.name === htmlName) ?? null;
    }

    isDeleted() { return this.deleter.inputEl && this.deleter.inputEl.checked; }
    cssBreakpoint() { return parseInt(this.el.dataset.cssBreakpoint); }

    copyValuesFrom(sourceConfig) {
        for (let i = 0; i < this.fieldLinks.length; i++) {
            this.fieldLinks[i].setLinked(sourceConfig.fieldLinks[i].checkbox.checked);
        }
        for (const field of this.fields) {
            const sourceField = sourceConfig.getFields(field.fieldName)[0];
            if (sourceField) {
                field.setValuePrepare(sourceField.getValue());
            }
        }
        for (const field of this.fields) {
            field.setValueConfirm();
        }
    }

    getPreviousConfig() {
        const ordered = this.parent.getConfigsOrdered();
        return ordered.filter(c => c.cssBreakpoint() < this.cssBreakpoint()).pop() ?? null;
    }

    copyValuesFromPreviousConfig() {
        const prev = this.getPreviousConfig();
        if (prev) this.copyValuesFrom(prev);
    }
}

export class XprezSectionConfig extends XprezConfigBase {
    constructor(parent, el) {
        super(parent, el);
        this.deleter = new XprezSectionConfigDeleter(this);
    }
}

export class XprezModuleConfig extends XprezConfigBase {
    constructor(parent, el) {
        super(parent, el);
        this.deleter = new XprezModuleConfigDeleter(this);
    }
}
