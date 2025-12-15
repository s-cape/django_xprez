export class XprezDeleterBase {
    constructor(obj) {
        this.obj = obj;
        this.initElements();
        if (this.triggerEl) {
            this.triggerEl.addEventListener("click", this.delete.bind(this));
        }
        if (this.undoEl) {
            this.undoEl.addEventListener("click", this.undo.bind(this));
        }
    }
    initElements() { throw new Error("Not implemented"); }
    delete() { this.obj.el.dataset.mode = "delete"; this.inputEl.checked = true; }
    undo() { this.obj.el.dataset.mode = ""; this.inputEl.checked = false; }
}

export class XprezSectionDeleter extends XprezDeleterBase {
    initElements() {
        this.triggerEl = this.obj.el.querySelector("[data-component='xprez-section-delete-trigger']");
        this.inputEl = this.triggerEl.querySelector("input");
        this.undoEl = this.obj.el.querySelector("[data-component='xprez-section-delete-undo']");
    }
}

export class XprezContentDeleter extends XprezDeleterBase {
    initElements() {
        this.triggerEl = this.obj.el.querySelector("[data-component='xprez-content-delete-trigger']");
        this.inputEl = this.triggerEl.querySelector("input");
        this.undoEl = this.obj.el.querySelector("[data-component='xprez-content-delete-undo']");
    }
}

export class XprezSectionConfigDeleter extends XprezDeleterBase {
    initElements() {
        this.triggerEl = this.obj.el.querySelector("[data-component='xprez-section-config-delete-trigger']");
        if (!this.triggerEl) { return; }
        this.inputEl = this.triggerEl.querySelector("input");
        this.undoEl = this.obj.el.querySelector("[data-component='xprez-section-config-delete-undo']");
    }

    delete() {
        super.delete();
        this.obj.configAdder.setOptionsDisabledState();
    }
    undo() {
        super.undo();
        this.obj.configAdder.setOptionsDisabledState();
    }
}