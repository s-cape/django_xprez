export class XprezPopoverBase {
    constructor(...args) {
        this.bindElements(...args);
        this.bindEvents();
        this.openOnErrors();
    }

    bindEvents() {
        document.addEventListener("click", (e) => {
            if (this.isOpen() && (!e.target.closest("[popover]"))) {
                this.hide();
            } else if (!this.isOpen() && this.triggerEl.contains(e.target)) {
                this.show();
            }
        });
    }

    hasErrors() { return this.el.querySelector("[data-has-errors]"); }
    openOnErrors() {
        if (this.hasErrors()) {
            this.show();
        }
    }

    isOpen() { return this.el.matches(":popover-open"); }
    show() { this.el.showPopover(); }
    hide() { this.el.hidePopover(); }
}

export class XprezSectionPopover extends XprezPopoverBase {
    bindElements(section) {
        this.section = section;
        this.el = this.section.el.querySelector("[data-component='xprez-section-popover']");
        this.triggerEl = this.section.el.querySelector("[data-component='xprez-section-popover-trigger']");
    }
    show() {
        this.section.xprez.getPopovers().filter(popover => popover !== this).forEach(popover => popover.hide());
        super.show();
        this.section.el.dataset.mode = "edit";
    }
    hide() {
        super.hide();
        this.section.el.dataset.mode = "";
    }
}

export class XprezContentPopover extends XprezPopoverBase {
    bindElements(content) {
        this.content = content;
        this.el = this.content.el.querySelector("[data-component='xprez-content-popover']");
        this.triggerEl = this.content.el.querySelector("[data-component='xprez-content-popover-trigger']");
    }
    show() {
        super.show();
        this.content.el.dataset.mode = "edit";
    }
    hide() {
        super.hide();
        this.content.el.dataset.mode = "";
    }
}

