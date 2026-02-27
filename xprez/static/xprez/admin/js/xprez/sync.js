export class XprezSyncManager {
    static VISUAL_FEEDBACK_MIN_DURATION_MS = 500;

    constructor(xprez) {
        this.xprez = xprez;
        this._queue = [];
        this._processing = false;
    }

    selectRelated(module) {
        const contentType = module.contentType();
        const sectionModules = module.section.modules;
        const modules = this.xprez.getModules();
        for (const m of modules) {
            if (m === module || m.el.dataset.mode === "delete") {
                continue;
            } else if (sectionModules.includes(m) && m.contentType() === contentType) {
                m.setSyncMode("selected", {updateUI: false});
            } else {
                m.setSyncMode("selectable", {updateUI: false});
            }
        }
        module.updateSyncSelectedUI();
    }

    clearSelection() {
        for (const module of this.xprez.getModules()) {
            if (module.el.dataset.mode === "selected" || module.el.dataset.mode === "selectable") {
                module.el.dataset.mode = "";
            }
        }
    }

    getSelectedModules() {
        return this.xprez.getModules().filter((m) => m.el.dataset.mode === "selected");
    }

    getSelectedCount() {
        return this.getSelectedModules().length;
    }

    getEditedModule() {
        return this.xprez.getModules().find((m) => m.el.dataset.mode === "edit") ?? null;
    }

    markMissingBreakpointsForDelete(sourceModule) {
        const sourceBreakpoints = new Set(
            sourceModule.configs
                .filter((c) => !c.isDeleted())
                .map((c) => c.cssBreakpoint())
        );
        for (const targetModule of this.getSelectedModules()) {
            for (const config of targetModule.configs) {
                if (!config.isDeleted() && !sourceBreakpoints.has(config.cssBreakpoint())) {
                    config.deleter.delete();
                }
            }
        }
    }

    syncField(field) {
        const targetBreakpoint = field.parent.cssBreakpoint?.() ?? null;
        for (const targetModule of this.getSelectedModules()) {
            this._queue.push({ sourceField: field, targetModule, targetBreakpoint });
        }
    }

    async processQueue() {
        if (this._processing) return;
        this._startProcessing();
        const affectedModules = new Set();
        try {
            while (this._queue.length > 0) {
                const action = this._queue.shift();
                affectedModules.add(action.targetModule);
                await this._ensureBreakpoint(action.targetModule, action.targetBreakpoint);
                this._processItem(action);
            }
            this._finalizeSync(affectedModules);
        } finally {
            await this._stopProcessing();
            if (this._queue.length > 0) this.processQueue();
        }
    }

    _startProcessing() {
        this._processing = true;
        this._processingStartedAt = Date.now();
        this.xprez.el.toggleAttribute("data-sync-processing", true);
    }

    async _stopProcessing() {
        this._processing = false;
        const remaining = XprezSyncManager.VISUAL_FEEDBACK_MIN_DURATION_MS - (Date.now() - this._processingStartedAt);
        if (remaining > 0) await new Promise(resolve => setTimeout(resolve, remaining));
        this.xprez.el.toggleAttribute("data-sync-processing", false);
    }

    async _ensureBreakpoint(module, breakpoint) {
        if (breakpoint !== null) {
            await module.configAdder.addBreakpoint(breakpoint);
        }
    }

    _processItem({sourceField, targetModule, targetBreakpoint}) {
        let targetField;
        if (targetBreakpoint == null) {
            targetField = targetModule.fields.find(f => f.fieldName === sourceField.fieldName);
        } else {
            const config = targetModule.configs.find(
                c => !c.isDeleted() && c.cssBreakpoint() === targetBreakpoint
            );
            targetField = config?.getFields(sourceField.fieldName)[0];
        }
        if (targetField) targetField._setValueSilent(sourceField.getValue());
    }

    _finalizeSync(affectedModules) {
        for (const module of affectedModules) {
            for (const config of module.configs) {
                if (config.isDeleted()) continue;
                for (const fieldLink of config.fieldLinks) {
                    fieldLink.setLinked(fieldLink.allGroupsMatch());
                }
            }
            const allFields = [
                ...module.fields,
                ...module.configs.flatMap((c) => c.fields),
            ];
            for (const field of allFields) {
                for (const sw of field.showWhens) sw.updateVisibility();
                field.refreshActive();
            }
        }
    }
}

export const XprezModuleSyncMixin = {
    initSync() {
        this.syncSelectTrigger = this.el.querySelector("[data-component='xprez-select-trigger']");
        this.syncSelectedBtn = this.popover.el.querySelector("[data-component='xprez-module-sync-selected']");
        this.syncSelectedCountEl = this.popover.el.querySelector("[data-component='xprez-module-sync-selected-count']");
        this.syncSelectTrigger.addEventListener("click", (e) => {
            if (this.el.dataset.mode === "edit") return;
            e.stopPropagation();
            this.setSyncMode(this.el.dataset.mode === "selected" ? "selectable" : "selected");
        });
        this.syncSelectedBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            this.syncSelected();
        });
    },

    setSyncMode(mode, options = {}) {
        this.el.dataset.mode = mode;
        if (options.updateUI !== false) {
            this.section.xprez.sync.getEditedModule()?.updateSyncSelectedUI();
        }
    },

    syncSelected() {
        const sync = this.section.xprez.sync;
        sync.markMissingBreakpointsForDelete(this);

        const syncableFields = [
            ...this.fields.filter((field) => this.popover.el.contains(field.el)),
            ...this.configs.filter((c) => !c.isDeleted()).flatMap((config) => config.fields),
        ].filter((field) => field.syncAllowed());
        for (const field of syncableFields) { sync.syncField(field); }

        sync.processQueue();
    },

    updateSyncSelectedUI() {
        const count = this.section.xprez.sync.getSelectedCount();
        this.syncSelectedBtn.toggleAttribute("data-hidden", count < 1);
        this.syncSelectedCountEl.textContent = count;
    },
};
