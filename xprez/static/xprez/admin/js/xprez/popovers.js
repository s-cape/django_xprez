import { XprezControllerBase } from './controller_base.js';

export class XprezPopoverBase extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.bindEvents();
        queueMicrotask(() => this.openOnErrors());
    }

    bindEvents() {
        this.xprez.on('popover-show', (opening) => {
            if (opening !== this) this.hide();
        });
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
        this.xprez.emit('popover-show', this);
        this.el.showPopover();
    }
    hide() {
        this.el.hidePopover();
        this.parent.checkShortcuts?.();
    }
}

export class XprezSectionPopover extends XprezPopoverBase {
    constructor(section, el) {
        super(section, el);
        this.triggerEl = section.el.querySelector("[data-xprez-section-popover-trigger]");
    }

    show() {
        super.show();
        this.parent.el.dataset.mode = "edit";
    }
    hide() {
        super.hide();
        this.parent.el.dataset.mode = "";
    }
}

export class XprezModulePopover extends XprezPopoverBase {
    constructor(module, el) {
        super(module, el);
        this.triggerEl = module.el.querySelector("[data-xprez-module-popover-trigger]");
    }

    show() {
        super.show();
        this.parent.el.dataset.mode = "edit";
        this.parent.section.xprez.sync.selectRelated(this.parent);
    }
    hide() {
        super.hide();
        this.parent.el.dataset.mode = "";
        this.parent.section.xprez.sync.clearSelection();
    }
}
