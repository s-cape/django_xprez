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

    queueItem(targetParent, targetBreakpoint, fieldName, value) {
        this._queue.push({ targetParent, targetBreakpoint, fieldName, value });
    }

    syncField(field) {
        const targetBreakpoint = field.parent.cssBreakpoint?.() ?? null;
        for (const targetParent of this.getSelectedModules()) {
            this.queueItem(targetParent, targetBreakpoint, field.fieldName, field.getValue());
        }
    }

    async processQueue() {
        if (this._processing) return;
        this._startProcessing();
        const affectedParents = new Set();
        try {
            while (this._queue.length > 0) {
                const action = this._queue.shift();
                if (this._isRedundant(action)) continue;

                affectedParents.add(action.targetParent);
                await this._ensureBreakpoint(action.targetParent, action.targetBreakpoint);
                this._processItem(action);
            }
            this._finalizeSync(affectedParents);
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

    getEffectiveValue(parent, breakpoint, fieldName) {
        const config = parent.configs.find(
            (c) => !c.isDeleted() && c.cssBreakpoint() === breakpoint
        );
        if (config) return config.getFields(fieldName)[0]?.getValue();
        const inherited = parent.configs
            .filter((c) => !c.isDeleted() && c.cssBreakpoint() < breakpoint)
            .sort((a, b) => b.cssBreakpoint() - a.cssBreakpoint())[0];
        return inherited?.getFields(fieldName)[0]?.getValue();
    }

    _isRedundant({ targetParent, targetBreakpoint, fieldName, value }) {
        if (targetBreakpoint === null) return false;
        if (targetParent.configs.find(c => !c.isDeleted() && c.cssBreakpoint() === targetBreakpoint)) {
            return false;
        }
        return this.getEffectiveValue(targetParent, targetBreakpoint, fieldName) === value;
    }

    async _ensureBreakpoint(parent, breakpoint) {
        if (breakpoint !== null) {
            await parent.configAdder.addBreakpoint(breakpoint);
        }
    }

    _processItem({ targetParent, targetBreakpoint, fieldName, value }) {
        let targetField;
        if (targetBreakpoint == null) {
            targetField = targetParent.fields.find(f => f.fieldName === fieldName);
        } else {
            const config = targetParent.configs.find(
                c => !c.isDeleted() && c.cssBreakpoint() === targetBreakpoint
            );
            targetField = config?.getFields(fieldName)[0];
        }
        if (targetField) {
            targetField._setValueSilent(value);
        }
    }

    _finalizeSync(affectedParents) {
        for (const parent of affectedParents) {
            for (const config of parent.configs) {
                if (config.isDeleted()) continue;
                for (const fieldLink of config.fieldLinks) {
                    fieldLink.setLinked(fieldLink.allGroupsMatch());
                }
            }
            const allFields = [
                ...parent.fields,
                ...parent.configs.flatMap((c) => c.fields),
            ];
            for (const field of allFields) {
                for (const sw of field.showWhens) sw.updateVisibility();
                field.refreshActive();
            }
            parent.checkShortcuts?.();
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
