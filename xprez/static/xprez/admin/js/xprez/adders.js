import { executeScripts } from './utils.js';

export class XprezAddBase {
    constructor(xprez, el) {
        this.xprez = xprez;
        this.el = el;

        this.el.querySelectorAll("[data-component='xprez-add-item']").forEach(
            this.initItem.bind(this)
        );
    }

    initItem(itemEl) {
        itemEl.addEventListener("click", this.add.bind(this, itemEl));
    }

    add(itemEl) {
        fetch(itemEl.dataset.url)
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
                this.placeNewElement(newEl);
                this.initNewElement(newEl);
                executeScripts(newEl);
                this.xprez.setPlacementToInputs();
            })
            .catch(error => {
                console.error('Error adding content:', error);
            });
    }

    placeNewElement(el) {}
    initNewElement(el) {}
}

export class XprezAddContainerEnd extends XprezAddBase {
    placeNewElement(el) { this.xprez.sectionsContainerEl.appendChild(el); }
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezAddSectionBase extends XprezAddBase {
    constructor(xprez, el, section) {
        super(xprez, el);
        this.section = section;
        this.setTriggerEl();
        this.triggerEl.addEventListener("click", this.toggle.bind(this));
    }
    setTriggerEl() {}
    add(itemEl) {
        super.add(itemEl);
        this.hide();
    }
    isVisible() { return !this.el.hasAttribute("data-hidden"); }
    show() { this.el.removeAttribute("data-hidden"); }
    hide() { this.el.setAttribute("data-hidden", ""); }
    toggle() { this.isVisible() ? this.hide() : this.show(); }
}

export class XprezAddSectionBefore extends XprezAddSectionBase {
    setTriggerEl() { this.triggerEl = this.section.el.querySelector("[data-component='xprez-add-section-before-trigger']"); }
    placeNewElement(el) { this.section.el.before(el); }
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezAddSectionEnd extends XprezAddSectionBase {
    setTriggerEl() { this.triggerEl = this.section.el.querySelector("[data-component='xprez-add-section-end-trigger']"); }
    placeNewElement(el) { this.section.gridEl.appendChild(el); }
    initNewElement(el) { this.section.initContent(el); }
}

// TODO: think about inheritance
export class XprezSectionConfigAdder {
    constructor(xprez, section) {
        this.xprez = xprez;
        this.section = section;
        this.el = this.section.el.querySelector("[data-xprez-component='xprez-section-config-adder']");
        this.selectEl = this.el.querySelector("select");
        this.options = this.selectEl.querySelectorAll("option");
        this.selectEl.addEventListener("change", this.add.bind(this));
    
        this.setOptionsDisabledState();
    }
    
    setOptionsDisabledState() {
        var existingConfigBreakpoints = [];
        for (const config of this.section.configs) {
            if (!config.isDeleted()) {
                existingConfigBreakpoints.push(config.cssBreakpoint());
            }
        }
        console.log(existingConfigBreakpoints);
        for (const option of this.options) {
            if (existingConfigBreakpoints.includes(option.value)) {
                console.log(option.value, "is disabled");
                option.setAttribute("disabled", "");
            } else {
                console.log(option.value, "is enabled");
                option.removeAttribute("disabled");
            }
        }
    }

    add() {
        const selectedOption = this.selectEl.value;
        console.log(selectedOption);
    }
}