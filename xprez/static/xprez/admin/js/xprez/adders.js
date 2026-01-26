import { executeScripts } from './utils.js';

export class XprezAdderBase {
    constructor(xprez, el) {
        this.xprez = xprez;
        this.el = el;
        this.bindEvents();
    }

    bindEvents() {}

    add(url) {
        fetch(url)
            .then(response => {
                if (response.ok) {
                    return response.text();
                } else {
                    console.log("TODO: show error message");
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
            })
            .then(html => {
                const newEl = new DOMParser().parseFromString(html, 'text/html').body.firstElementChild;
                this.processNewElement(newEl);
            })
            .catch(error => {
                console.error('Error adding:', error);
            });
    }

    processNewElement(newEl) {
        this.placeNewElement(newEl);
        this.initNewElement(newEl);
        executeScripts(newEl);
    }

    placeNewElement(el) {}
    initNewElement(el) {}
}

export class XprezAdderItemsBase extends XprezAdderBase {
    bindEvents() {
        this.el.querySelectorAll("[data-component='xprez-add-item']").forEach(
            itemEl => itemEl.addEventListener("click", () => this.add(itemEl.dataset.url))
        );
    }

    processNewElement(newEl) {
        super.processNewElement(newEl);
        this.xprez.setPlacementToInputs();
    }
}

export class XprezAdderSelectBase extends XprezAdderBase {
    bindEvents() {
        this.selectEl = this.el.querySelector("select");
        this.options = this.selectEl.querySelectorAll("option");
        this.selectEl.addEventListener("change", this.onSelectChange.bind(this));
    }

    onSelectChange() {
        if (!this.selectEl.value) return;

        const selectedOption = this.selectEl.options[this.selectEl.selectedIndex];
        this.handleSelection(selectedOption);
        this.selectEl.value = "";
    }

    handleSelection(selectedOption) {
        this.add(selectedOption.dataset.url);
    }
}

export class XprezAdderContainerEnd extends XprezAdderItemsBase {
    placeNewElement(el) { this.xprez.sectionsContainerEl.appendChild(el); }
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezAdderSectionBase extends XprezAdderItemsBase {
    constructor(xprez, el, section) {
        super(xprez, el);
        this.section = section;
        this.setTriggerEl();
        this.triggerEl.addEventListener("click", this.toggle.bind(this));
    }

    setTriggerEl() {}

    add(url) {
        super.add(url);
        this.hide();
    }

    isOpen() { return !this.el.hasAttribute("data-hidden"); }
    show() { this.el.removeAttribute("data-hidden"); }
    hide() { this.el.setAttribute("data-hidden", ""); }
    toggle() { this.isOpen() ? this.hide() : this.show(); }
}

export class XprezAdderSectionBefore extends XprezAdderSectionBase {
    setTriggerEl() {
        this.triggerEl = this.section.el.querySelector("[data-component='xprez-adder-section-before-trigger']");
    }
    placeNewElement(el) { this.section.el.before(el); }
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezAdderSectionEnd extends XprezAdderSectionBase {
    setTriggerEl() {
        this.triggerEl = this.section.el.querySelector("[data-component='xprez-adder-section-end-trigger']");
    }
    placeNewElement(el) { this.section.gridEl.appendChild(el); }
    initNewElement(el) { this.section.initModule(el); }
}

export class XprezConfigAdderBase extends XprezAdderSelectBase {
    constructor(xprez, parent, componentName) {
        super(xprez, parent.el.querySelector(`[data-component='${componentName}']`));
        this.parent = parent;
        this.setOptionsDisabledState();
    }

    handleSelection(selectedOption) {
        const selectedBreakpoint = parseInt(selectedOption.value);
        const existingConfig = this.parent.configs.find(
            config => config.cssBreakpoint() === selectedBreakpoint
        );

        if (existingConfig) {
            if (existingConfig.isDeleted()) {
                existingConfig.deleter.undo();
                this.setOptionsDisabledState();
            }
        } else {
            this.add(selectedOption.dataset.url);
        }
    }

    setOptionsDisabledState() {
        const existingBreakpoints = this.parent.configs
            .filter(config => !config.isDeleted())
            .map(config => config.cssBreakpoint());

        for (const option of this.options) {
            if (existingBreakpoints.includes(parseInt(option.value))) {
                option.setAttribute("disabled", "");
            } else {
                option.removeAttribute("disabled");
            }
        }
    }

    placeNewElement(newEl) {
        const newBreakpoint = parseInt(newEl.dataset.cssBreakpoint);
        for (const config of this.parent.configs) {
            if (newBreakpoint < config.cssBreakpoint()) {
                config.el.before(newEl);
                return;
            }
        }
        this.parent.configsContainerEl.appendChild(newEl);
    }

    initNewElement(newEl) {
        this.parent.initConfig(newEl);
        this.setOptionsDisabledState();
    }
}

export class XprezSectionConfigAdder extends XprezConfigAdderBase {
    constructor(xprez, section) {
        super(xprez, section, "xprez-adder-section-config");
        this.section = section;
    }
}

export class XprezModuleConfigAdder extends XprezConfigAdderBase {
    constructor(xprez, module) {
        super(xprez, module, "xprez-adder-module-config");
        this.module = module;
    }
}
