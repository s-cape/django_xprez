import { XprezFieldController, XprezShowWhen } from './fields.js';
import { XprezControllerBase } from './controller_base.js';

/** Common base for content types (Section, Module): shared fields, configs, show-when. */
export class XprezContentBase extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.configsContainerEl = this.el.querySelector(this.configsContainerSelector);
        this.shortcutsContainerEl = this.el.querySelector("[data-xprez-shortcuts]");
    }

    get unmanagedContainers() {
        return [this.configsContainerEl, this.shortcutsContainerEl].filter(c => c !== null);
    }

    isUnmanaged(el) {
        return this.unmanagedContainers.some(c => c.contains(el));
    }

    initFields() {
        this.fields = [];
        this.popover.el.querySelectorAll('[data-xprez-field]').forEach(fieldEl => {
            if (this.isUnmanaged(fieldEl)) return;
            this.fields.push(new XprezFieldController(this, fieldEl));
        });
    }

    getFieldByInputName(htmlName) {
        return this.fields?.find(f => f.inputEl?.name === htmlName) ?? null;
    }

    initShowWhens() {
        this.popover.el.querySelectorAll("[data-show-when]").forEach(showWhenEl => {
            if (this.isUnmanaged(showWhenEl)) return;
            new XprezShowWhen(this, showWhenEl);
        });
    }

    initConfigs() {
        this.configs = [];
        this.el.querySelectorAll(this.configSelector).forEach(configEl =>
            this.initConfig(configEl)
        );
        this.configAdder = this.createConfigAdder();
    }

    initConfig(configEl) {
        const config = this.createConfig(configEl);
        this.configs.push(config);
        return config;
    }
}
