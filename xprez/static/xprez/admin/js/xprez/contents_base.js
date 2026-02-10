import { XprezFieldController } from './fields.js';
import { XprezShowWhen } from './utils.js';

/** Common base for content types (Section, Module): shared fields, configs, show-when. */
export class XprezContentBase {
    constructor(el) {
        this.el = el;
        this.configsContainerEl = this.el.querySelector(this.configsContainerSelector);
    }

    initFields() {
        this.fields = [];
        this.popover.el.querySelectorAll('[data-component="field"]').forEach(fieldEl => {
            if (this.configsContainerEl.contains(fieldEl)) return;
            this.fields.push(new XprezFieldController(this, fieldEl));
        });
    }

    initShowWhens() {
        this.popover.el.querySelectorAll("[data-show-when]").forEach(showWhenEl => {
            if (this.configsContainerEl?.contains(showWhenEl)) return;
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
