export class XprezFieldController {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.fieldName = el.dataset.fieldName;
        this.inputEl = el.querySelector('select, input');

        if (this.inputEl) {
            this._previousValue = this.getValue();
            this.refreshActive();
            this.inputEl.addEventListener('input', this._onInputChange.bind(this));
            this.inputEl.addEventListener('change', this._onInputChange.bind(this));
        }
    }

    getValue() {
        if (!this.inputEl) return null;
        if (this.inputEl.type === 'checkbox') {
            return this.inputEl.checked ? 'true' : 'false';
        }
        return this.inputEl.value;
    }

    setValue(value) {
        const changed = this._setValueSilent(value);
        if (changed) {
            this.inputEl.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    _setValueSilent(value) {
        if (!this.inputEl) return false;
        if (this.getValue() === value) return false;

        if (this.inputEl.type === 'checkbox') {
            this.inputEl.checked = value === 'true';
        } else {
            this.inputEl.value = value;
        }
        this._previousValue = value;
        return true;
    }

    _getConfigParent() {
        return this.parent.parent;
    }

    _getOrderedConfigs() {
        const configParent = this._getConfigParent();
        return configParent ? configParent.getConfigsOrdered() : [];
    }

    getPreviousField() {
        if (!this.parent.cssBreakpoint) return null;  // Only config fields have breakpoints
        const ordered = this._getOrderedConfigs();
        const bp = this.parent.cssBreakpoint();
        const prevConfig = ordered.filter(c => c.cssBreakpoint() < bp).pop();
        return prevConfig?.getFields(this.fieldName)[0] ?? null;
    }

    getNextField() {
        if (!this.parent.cssBreakpoint) return null;
        const ordered = this._getOrderedConfigs();
        const bp = this.parent.cssBreakpoint();
        const nextConfig = ordered.find(c => c.cssBreakpoint() > bp);
        return nextConfig?.getFields(this.fieldName)[0] ?? null;
    }

    getAllFollowingFields() {
        if (!this.parent.cssBreakpoint) return [];

        const ordered = this._getOrderedConfigs();
        const bp = this.parent.cssBreakpoint();
        return ordered
            .filter(c => c.cssBreakpoint() > bp)
            .flatMap(c => c.getFields(this.fieldName));
    }

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
        this.el.dataset.active = isActive ? 'true' : 'false';
    }

    _isLinked() {
        return this.fieldLink?.checkbox?.checked ?? false;
    }

    _onInputChange() {
        const oldValue = this._previousValue;
        const newValue = this.getValue();
        if (oldValue === newValue) return;
        this._previousValue = newValue;

        const affected = this._cascadeAndSyncValues(oldValue, newValue);
        this._refreshActiveStates(affected);
    }

    _cascadeAndSyncValues(oldValue, newValue) {
        const affected = [this];

        if (this.fieldLink && this._isLinked()) {
            const inputName = this.inputEl?.name;
            for (const group of this.fieldLink.groups) {
                if (!group.includes(inputName)) continue;
                for (const name of group) {
                    if (name === inputName) continue;
                    const linkedField = this.fieldLink.getFieldController(name);
                    if (linkedField && linkedField.getValue() !== newValue) {
                        const linkedOldValue = linkedField.getValue();
                        linkedField._setValueSilent(newValue);
                        affected.push(linkedField);
                        this._cascadeField(linkedField, linkedOldValue, newValue, affected);
                    }
                }
            }
        }

        this._cascadeField(this, oldValue, newValue, affected);
        return affected;
    }

    _cascadeField(field, oldValue, newValue, affected) {
        const linkState = field._isLinked();
        for (const following of field.getAllFollowingFields()) {
            if (following.getValue() !== oldValue) break;
            if (following._isLinked() !== linkState) break;
            following._setValueSilent(newValue);
            affected.push(following);
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
        for (const f of allFields) {
            f.refreshActive();
        }
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

    getFieldController(name) {
        return this.parent.getFieldByInputName?.(name) ?? null;
    }

    getFieldInput(name) {
        return this.getFieldController(name)?.inputEl ?? null;
    }

    getFieldWrapper(name) {
        return this.getFieldController(name)?.el ?? null;
    }

    getFieldValue(name) {
        return this.getFieldController(name)?.getValue() ?? null;
    }

    setFieldValue(name, value) {
        this.getFieldController(name)?.setValue(value);
    }

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

    syncAllGroups(silent = false) {
        this.groups.forEach(group => {
            const value = this.getFieldValue(group[0]);
            if (value == null) return;
            group.slice(1).forEach(name => {
                const controller = this.getFieldController(name);
                if (controller) {
                    silent ? controller._setValueSilent(value) : controller.setValue(value);
                }
            });
        });
    }

    syncGroupSilent(sourceName, group) {
        if (!this.checkbox.checked) return [];
        const value = this.getFieldValue(sourceName);
        const affected = [];
        for (const name of group) {
            if (name === sourceName) continue;
            const controller = this.getFieldController(name);
            if (controller && controller.getValue() !== value) {
                controller._setValueSilent(value);
                affected.push(controller);
            }
        }
        return affected;
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

        for (const following of firstController.getAllFollowingFields()) {
            const nextFieldLink = following.fieldLink;
            if (!nextFieldLink) break;
            if (nextFieldLink.checkbox.checked !== wasLinked) break;

            const theirValues = nextFieldLink.getAllValues();
            const valuesMatch = valuesBefore.length === theirValues.length &&
                valuesBefore.every((v, i) => v === theirValues[i]);
            if (!valuesMatch) break;

            nextFieldLink.setLinked(nowLinked);
            if (nowLinked) {
                nextFieldLink.syncAllGroups(true);
            }
            affected.push(nextFieldLink);
        }
        return affected;
    }

    // Listeners

    initListeners() {
        this.checkbox.addEventListener('change', () => {
            const wasLinked = !this.checkbox.checked;
            // Capture values BEFORE sync (for cascade comparison)
            const valuesBefore = this.getAllValues();
            this.updateUI();
            if (this.checkbox.checked) {
                this.syncAllGroups();
            }
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

        this.groups.forEach(group => {
            group.forEach(name => {
                const input = this.getFieldInput(name);
                if (input) {
                    input.addEventListener('input', () => {
                        const affected = this.syncGroupSilent(name, group);
                        affected.forEach(c => c.refreshActive());
                    });
                }
            });
        });
    }
}
