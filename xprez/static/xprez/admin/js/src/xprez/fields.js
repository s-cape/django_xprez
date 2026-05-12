import { XprezControllerBase } from './controller_base.js';

export class XprezFieldController extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.fieldName = el.dataset.fieldName;
        this.inputEl = el.querySelector('select, input');

        this.showWhens = [];

        if (this.inputEl) {
            this._previousValue = this.getValue();
            this.refreshActive();
            this.inputEl.addEventListener('input', (e) => this._onInputChange(e));
            this.inputEl.addEventListener('change', (e) => this._onInputChange(e));
        }
    }

    syncAllowed() {
        return this.el.hasAttribute("data-sync-allowed");
    }

    // Value
    // Public: setValue (set + propagate), setValuePrepare + setValueConfirm (batch: apply DOM then propagate)
    // Internal: _setValueSilent (set DOM + state, no propagation/notifications; used by sync/cascade)
    getValue() {
        if (this.inputEl.type === 'checkbox') {
            return this.inputEl.checked ? 'true' : 'false';
        } else {
            return this.inputEl.value;
        }
    }

    _applyValue(value) {
        if (this.inputEl.type === 'checkbox') {
            this.inputEl.checked = value === 'true';
        } else {
            this.inputEl.value = value;
        }
    }

    setValue(value) {
        if (this.getValue() === value) return;
        this.setValuePrepare(value);
        this.setValueConfirm();
    }

    setValuePrepare(value) { this._applyValue(value); }
    setValueConfirm() { this._propagateChange(this._previousValue, this.getValue()); }

    // Internal: set DOM + state only; no propagation, no notifications
    _setValueSilent(value) {
        if (this.getValue() === value) return false;
        this._applyValue(value);
        this._previousValue = value;
        return true;
    }

    // Breakpoint navigation
    _getConfigParent() { return this.parent.parent; }

    _getConfigsOrdered() {
        const configParent = this._getConfigParent();
        return configParent ? configParent.getConfigsOrdered() : [];
    }

    _getAdjacentConfig(direction) {
        if (!this.parent.cssBreakpoint) return null;
        const ordered = this._getConfigsOrdered();
        const bp = this.parent.cssBreakpoint();
        if (direction < 0) {
            return ordered.filter(c => c.cssBreakpoint() < bp).pop() ?? null;
        } else {
            return ordered.find(c => c.cssBreakpoint() > bp) ?? null;
        }
    }

    _getPreviousConfig() { return this._getAdjacentConfig(-1); }
    _getNextConfig() { return this._getAdjacentConfig(1); }

    getPreviousField() { return this._getPreviousConfig()?.getFields(this.fieldName)[0] ?? null; }
    getNextField() { return this._getNextConfig()?.getFields(this.fieldName)[0] ?? null; }

    getNextFields() {
        const result = [];
        let next = this.getNextField();
        while (next) {
            result.push(next);
            next = next.getNextField();
        }
        return result;
    }

    isVisible() {
        const hidden = this.el.closest('[data-hidden]');
        return !hidden || !this.parent.el.contains(hidden);
    }

    // Active state (data-active).
    computeIsActive() {
        const prev = this.getPreviousField();
        if (!prev) return true;  // Base breakpoint always active
        if (prev._isLinked() !== this._isLinked()) return true;
        return prev.getValue() !== this.getValue();
    }

    refreshActive() {
        let isActive = this.computeIsActive();
        // If linked and any linked field is active, all are active
        if (!isActive && this._isLinked()) {
            isActive = this.fieldLink.computeAnyActive();
        }
        // Previous hidden by ShowWhen → this field is effectively new
        if (!isActive) {
            const prev = this.getPreviousField();
            if (prev && !prev.isVisible()) isActive = true;
        }
        this.el.dataset.active = isActive ? 'true' : 'false';
    }

    _isLinked() {
        return this.fieldLink?.checkbox?.checked ?? false;
    }

    // Single path: sync link, cascade, refresh, notify ShowWhens, dispatch
    _propagateChange(oldValue, newValue) {
        if (oldValue === newValue) return [];
        this._previousValue = newValue;

        const linkResult = this.fieldLink?.syncFrom(this, oldValue, newValue)
            ?? [{ controller: this, oldValue }];
        const affected = linkResult.map(r => r.controller);
        for (const { controller, oldValue: ov } of linkResult) {
            this._cascadeField(controller, ov, newValue, affected);
        }

        this._refreshActiveStates(affected);
        affected.forEach(f => f.showWhens.forEach(sw => sw.updateVisibility()));
        affected.filter(f => f !== this).forEach(f =>
            f.inputEl.dispatchEvent(new Event("change", { bubbles: true }))
        );
        this.parent?.parent?.checkShortcuts?.();
        return affected;
    }

    _tryLiveSync(affectedFields = [this]) {
        const module = this.module;
        if (
            !module?.liveSyncInput.checked
            || !this.syncAllowed()
            || !module.popover?.el?.contains(this.el)
        ) return;

        const sync = this.xprez.sync;
        if (sync.getSelectedCount() < 1) return;

        // Sync linked siblings and cascades too, not just the source field.
        for (const field of affectedFields) {
            if (field.syncAllowed()) sync.syncField(field);
        }
        sync.processQueue();
    }

    _onInputChange(e) {
        const newValue = this.getValue();
        if (newValue === this._previousValue) return;
        const affected = this._propagateChange(this._previousValue, newValue);
        if (e?.isTrusted) this._tryLiveSync(affected);
    }

    _cascadeField(field, oldValue, newValue, affected) {
        const linkState = field._isLinked();
        for (const nextField of field.getNextFields()) {
            if (nextField.getValue() !== oldValue) break;
            if (nextField._isLinked() !== linkState) break;
            nextField._setValueSilent(newValue);
            affected.push(nextField);
        }
    }

    _refreshActiveStates(fields) {
        const allFields = new Set(fields);
        for (const f of fields) {
            if (f.fieldLink) {
                f.fieldLink.getAllControllers().forEach(c => allFields.add(c));
            }
            const next = f.getNextField();
            if (next) allFields.add(next);
        }
        for (const f of allFields) { f.refreshActive(); }
    }
}


export class XprezFieldLink {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.checkbox = el.querySelector('input[type="checkbox"]');
        this.groups = this.parseGroups(el.dataset.fieldLink || '');
        this.linkIcon = el.dataset.fieldLinkIcon || null;
        this.originalIcons = this.storeOriginalIcons();
        this.registerWithControllers();
        this.initListeners();
        this.setLinked(this.allGroupsMatch());
        this.getAllControllers().forEach(c => c.refreshActive());
    }

    registerWithControllers() {
        this.groups.forEach(group => {
            group.forEach(name => {
                const controller = this.getFieldController(name);
                if (controller) controller.fieldLink = this;
            });
        });
    }

    // Parsing & helpers

    parseGroups(str) {
        if (!str) return [];
        return str.split(',').map(g => g.split(':').filter(Boolean)).filter(g => g.length > 1);
    }

    getFieldController(name) { return this.parent.getFieldByInputName?.(name) ?? null; }
    getFieldWrapper(name) { return this.getFieldController(name)?.el ?? null; }
    getFieldValue(name) { return this.getFieldController(name)?.getValue() ?? null; }
    setFieldValue(name, value) { this.getFieldController(name)?.setValue(value); }

    // State management

    allGroupsMatch() {
        return this.groups.every(group => {
            const values = group.map(name => this.getFieldValue(name)).filter(v => v != null);
            return values.length > 1 && values.every(v => v === values[0]);
        });
    }

    setLinked(linked) {
        this.checkbox.checked = linked;
        this.updateUI();
    }

    // UI updates

    storeOriginalIcons() {
        const icons = new Map();
        if (!this.linkIcon) return icons;
        this.groups.forEach(group => {
            const icon = this.getFieldWrapper(group[0])?.querySelector('label > i');
            if (icon) icons.set(group[0], icon.className);
        });
        return icons;
    }

    updateUI() {
        const linked = this.checkbox.checked;
        this.groups.forEach(group => {
            const secondWrapper = this.getFieldWrapper(group[1]);
            if (secondWrapper) {
                secondWrapper.toggleAttribute('data-field-link-hidden', linked);
            }
            if (this.linkIcon) {
                const icon = this.getFieldWrapper(group[0])?.querySelector('label > i');
                if (icon) {
                    icon.className = linked ? this.linkIcon : (this.originalIcons.get(group[0]) || '');
                }
            }
        });
    }

    // Syncing

    // Sync linked fields in same config to newValue; return { controller, oldValue } for each (for cascade)
    syncFrom(sourceController, oldValue, newValue) {
        const result = [{ controller: sourceController, oldValue }];
        if (!this.checkbox.checked) return result;
        const inputName = sourceController.inputEl?.name;
        for (const group of this.groups) {
            if (!group.includes(inputName)) continue;
            for (const name of group) {
                if (name === inputName) continue;
                const linkedField = this.getFieldController(name);
                if (linkedField && linkedField.getValue() !== newValue) {
                    result.push({ controller: linkedField, oldValue: linkedField.getValue() });
                    linkedField._setValueSilent(newValue);
                }
            }
        }
        return result;
    }

    syncAllGroups() {
        this.groups.forEach(group => {
            const value = this.getFieldValue(group[0]);
            if (value == null) return;
            group.slice(1).forEach(name => {
                this.getFieldController(name)?.setValue(value);
            });
        });
    }

    getAllControllers() {
        const controllers = new Set();
        for (const group of this.groups) {
            for (const name of group) {
                const c = this.getFieldController(name);
                if (c) controllers.add(c);
            }
        }
        return controllers;
    }

    computeAnyActive() {
        for (const c of this.getAllControllers()) {
            if (c.computeIsActive()) return true;
        }
        return false;
    }

    getAllValues() {
        return this.groups.flatMap(g => g.map(name => this.getFieldValue(name)));
    }

    cascadeLinkState(wasLinked, valuesBefore) {
        const nowLinked = this.checkbox.checked;
        const affected = [];

        const firstController = this.getFieldController(this.groups[0]?.[0]);
        if (!firstController) return affected;

        for (const following of firstController.getNextFields()) {
            const nextFieldLink = following.fieldLink;
            if (!nextFieldLink) break;
            if (nextFieldLink.checkbox.checked !== wasLinked) break;

            const theirValues = nextFieldLink.getAllValues();
            const valuesMatch = valuesBefore.length === theirValues.length &&
                valuesBefore.every((v, i) => v === theirValues[i]);
            if (!valuesMatch) break;

            nextFieldLink.setLinked(nowLinked);
            if (nowLinked) { nextFieldLink.syncAllGroups(); }
            affected.push(nextFieldLink);
        }
        return affected;
    }

    // Listeners

    initListeners() {
        this.checkbox.addEventListener('change', () => {
            const wasLinked = !this.checkbox.checked;
            const valuesBefore = this.getAllValues();
            this.updateUI();
            if (this.checkbox.checked) { this.syncAllGroups(); }

            const affected = this.cascadeLinkState(wasLinked, valuesBefore);

            const allControllers = new Set(this.getAllControllers());
            for (const fl of affected) {
                fl.getAllControllers().forEach(c => allControllers.add(c));
            }
            allControllers.forEach(c => {
                c.refreshActive();
                c.getNextField()?.refreshActive();
            });
        });
    }
}


export class XprezShowWhen {
    constructor(parent, el) {
        this.el = el;
        const [fieldName, targetValue] = this.el.getAttribute("data-show-when").split(":");
        this.targetValues = new Set(targetValue.split("|"));
        this.controller = parent.getFieldByInputName(fieldName);
        this.controller.showWhens.push(this);
        this.updateVisibility();
    }

    updateVisibility() {
        const wasHidden = this.el.hasAttribute("data-hidden");
        if (this.targetValues.has(this.controller.getValue())) {
            this.el.removeAttribute("data-hidden");
        } else {
            this.el.setAttribute("data-hidden", "");
        }
        if (wasHidden !== this.el.hasAttribute("data-hidden")) {
            this._refreshContainedFields();
        }
    }

    _refreshContainedFields() {
        const fields = this.controller.parent.fields?.filter(f => this.el.contains(f.el)) ?? [];
        for (const field of fields) {
            field.refreshActive();
            field.getNextField()?.refreshActive();
        }
    }
}

export function resolveFieldControllerClass(fieldEl) {
    const className = fieldEl.dataset.controller;
    if (className && !window[className]) {
        console.error(`Field controller class ${className} not found`);
    }
    return (className && window[className]) || XprezFieldController;
}

