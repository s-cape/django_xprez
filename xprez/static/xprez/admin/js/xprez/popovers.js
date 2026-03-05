export class XprezPopoverBase {
    constructor(...args) {
        this.bindElements(...args);
        this.bindEvents();
        queueMicrotask(() => this.openOnErrors());
    }

    bindEvents() {
        document.addEventListener("click", (e) => {
            if (this.isOpen() && (!e.target.closest("[popover]"))) {
                this.hide();
            } else if (!this.isOpen() && this.triggerEl?.contains(e.target)) {
                this.show();
            }
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && this.isOpen()) {
                this.hide();
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
    show() {
        this.el.showPopover();
    }
    hide() {
        this.el.hidePopover();
        this.parent.checkShortcuts?.();
    }
    hideOthers() {
        this.parent.xprez.getPopovers().filter(p => p !== this).forEach(p => p.hide());
    }
}

export class XprezSectionPopover extends XprezPopoverBase {
    bindElements(section) {
        this.parent = section;
        this.el = this.parent.el.querySelector("[data-component='xprez-section-popover']");
        this.triggerEl = this.parent.el.querySelector("[data-component='xprez-section-popover-trigger']");
    }
    show() {
        this.hideOthers();
        super.show();
        this.parent.el.dataset.mode = "edit";
    }
    hide() {
        super.hide();
        this.parent.el.dataset.mode = "";
    }
}

export class XprezModulePopover extends XprezPopoverBase {
    bindElements(module) {
        this.parent = module;
        this.el = this.parent.el.querySelector("[data-component='xprez-module-popover']");
        this.triggerEl = this.parent.el.querySelector("[data-component='xprez-module-popover-trigger']");
    }
    show() {
        this.hideOthers();
        super.show();
        this.parent.el.dataset.mode = "edit";
        this.parent.section.xprez.sync.selectRelated(this.parent);
    }
    hide() {
        this.parent.section.xprez.sync.clearSelection();
        super.hide();
        this.parent.el.dataset.mode = "";
    }
}
