import { XprezSectionConfigDeleter, XprezModuleConfigDeleter } from './deleters.js';
import { XprezShowWhen, XprezFieldLink } from './utils.js';
import { XprezFieldController } from './fields.js';

/** Mixin for Section/Module that own configs. Apply via Object.assign(Class.prototype, XprezConfigParentMixin) */
export const XprezConfigParentMixin = {
    getConfigsOrdered() {
        return [...this.configs]
            .filter(c => !c.isDeleted())
            .sort((a, b) => a.cssBreakpoint() - b.cssBreakpoint());
    },
    updateAllFieldsActive() {
        for (const config of this.configs) {
            for (const field of config.fields) {
                field.updateActive();
            }
        }
    }
};

export class XprezConfigBase {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.initFields();
        this.initShowWhens();
        this.initFieldLinks();
    }

    initFields() {
        this.fields = [];
        this.el.querySelectorAll('[data-component="field"]').forEach(fieldEl => {
            const field = new XprezFieldController(this, fieldEl);
            this.fields.push(field);
        });
    }

    initShowWhens() {
        this.el.querySelectorAll("[data-show-when]").forEach(fieldEl => {
            new XprezShowWhen(this, fieldEl);
        });
    }

    initFieldLinks() {
        this.el.querySelectorAll("[data-field-link]").forEach(el => {
            new XprezFieldLink(this, el);
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
        for (const field of this.fields) {
            const sourceField = sourceConfig.getFields(field.fieldName)[0];
            if (sourceField) {
                field.setValue(sourceField.getValue());
            }
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
    constructor(section, el) {
        super(section, el);
        this.section = section;
        this.deleter = new XprezSectionConfigDeleter(this);
    }

    getDefault(fieldName) {
        return this.parent.xprez.defaults.section_config[fieldName];
    }
}

export class XprezModuleConfig extends XprezConfigBase {
    constructor(module, el) {
        super(module, el);
        this.module = module;
        this.deleter = new XprezModuleConfigDeleter(this);
    }

    getDefault(fieldName) {
        return this.parent.section.xprez.defaults.module_config[this.parent.contentType()][fieldName];
    }
}
