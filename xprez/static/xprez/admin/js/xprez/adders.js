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

