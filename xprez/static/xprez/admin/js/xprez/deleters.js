export class XprezDeleterBase {
    constructor(obj) {
        this.obj = obj;
        this.initElements();
        if (this.triggerEl) {
            this.triggerEl.addEventListener("click", this.delete.bind(this));
        }
        if (this.undeleteEl) {
            this.undeleteEl.addEventListener("click", this.undelete.bind(this));
        }
    }
    initElements() { throw new Error("Not implemented"); }
    delete() { this.obj.el.dataset.mode = "delete"; this.inputEl.checked = true; }
    undelete() { this.obj.el.dataset.mode = ""; this.inputEl.checked = false; }
}

export class XprezSectionDeleter extends XprezDeleterBase {
    initElements() {
        this.triggerEl = this.obj.el.querySelector("[data-component='xprez-section-delete-trigger']");
        this.inputEl = this.triggerEl.querySelector("input");
        this.undeleteEl = this.obj.el.querySelector("[data-component='xprez-section-undelete']");
    }
}

export class XprezModuleDeleter extends XprezDeleterBase {
    initElements() {
        this.triggerEl = this.obj.el.querySelector("[data-component='xprez-module-delete-trigger']");
        this.inputEl = this.triggerEl.querySelector("input");
        this.undeleteEl = this.obj.el.querySelector("[data-component='xprez-module-undelete']");
    }
}

export class XprezConfigDeleterBase extends XprezDeleterBase {
    _initElements(dataComponentName) {
        this.triggerEl = this.obj.el.querySelector(`[data-component='xprez-${dataComponentName}-delete-trigger']`);
        if (!this.triggerEl) { return; }
        this.inputEl = this.triggerEl.querySelector("input");
        this.undeleteEl = this.obj.el.querySelector(`[data-component='xprez-${dataComponentName}-undelete']`);
    }

    _afterDeleteChange() {
        this.obj.parent.configAdder.setOptionsDisabledState();
        this.obj.parent.updateAllFieldsActive();
    }

    delete() {
        super.delete();
        this._afterDeleteChange();
    }

    undelete() {
        super.undelete();
        this._afterDeleteChange();
    }
}

export class XprezSectionConfigDeleter extends XprezConfigDeleterBase {
    initElements() { this._initElements("section-config"); }
}

export class XprezModuleConfigDeleter extends XprezConfigDeleterBase {
    initElements() { this._initElements("module-config"); }
}
