export class XprezFieldController {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.fieldName = el.dataset.fieldName;
        this.inputEl = el.querySelector('select, input');

        if (this.inputEl) {
            this._previousValue = this.getValue();
            this.updateActive();
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
        if (!this.inputEl) return;
        if (this.getValue() === value) return;

        if (this.inputEl.type === 'checkbox') {
            this.inputEl.checked = value === 'true';
        } else {
            this.inputEl.value = value;
        }
        this._previousValue = value;
        this.updateActive();
        this.inputEl.dispatchEvent(new Event('change', { bubbles: true }));
    }

    _getConfigParent() {
        // For config fields, get the section/module that owns the config
        return this.parent.parent;
    }

    _getOrderedConfigs() {
        const configParent = this._getConfigParent();
        return configParent ? configParent.getConfigsOrdered() : [];
    }

    getPreviousField() {
        // Section/module fields don't have breakpoints - no previous field
        if (!this.parent.cssBreakpoint) return null;

        const ordered = this._getOrderedConfigs();
        const bp = this.parent.cssBreakpoint();
        const prevConfig = ordered.filter(c => c.cssBreakpoint() < bp).pop();
        return prevConfig?.getFields(this.fieldName)[0] ?? null;
    }

    getNextField() {
        // Section/module fields don't have breakpoints - no next field
        if (!this.parent.cssBreakpoint) return null;

        const ordered = this._getOrderedConfigs();
        const bp = this.parent.cssBreakpoint();
        const nextConfig = ordered.find(c => c.cssBreakpoint() > bp);
        return nextConfig?.getFields(this.fieldName)[0] ?? null;
    }

    getAllFollowingFields() {
        // Section/module fields don't have breakpoints - no following fields
        if (!this.parent.cssBreakpoint) return [];

        const ordered = this._getOrderedConfigs();
        const bp = this.parent.cssBreakpoint();
        return ordered
            .filter(c => c.cssBreakpoint() > bp)
            .flatMap(c => c.getFields(this.fieldName));
    }

    _valuesMatch(a, b) {
        // Treat null/undefined/empty string as equivalent
        const normalize = v => (v === null || v === undefined || v === '') ? '' : String(v);
        return normalize(a) === normalize(b);
    }

    updateActive() {
        const prev = this.getPreviousField();
        if (prev) {
            const isSame = prev.getValue() === this.getValue();
            this.el.dataset.active = isSame ? 'false' : 'true';
        } else {
            const defaultValue = this.parent.getDefault?.(this.fieldName);
            if (defaultValue === undefined) {
                this.el.dataset.active = 'true';
            } else {
                const isSame = this._valuesMatch(defaultValue, this.getValue());
                this.el.dataset.active = isSame ? 'false' : 'true';
            }
        }
    }

    _onInputChange() {
        const oldValue = this._previousValue;
        const newValue = this.getValue();
        if (oldValue === newValue) return;

        this._previousValue = newValue;
        this.updateActive();

        // Cascade: update following fields while they match oldValue, stop on first mismatch
        const following = this.getAllFollowingFields();
        for (const field of following) {
            if (field.getValue() !== oldValue) {
                break;
            }
            field.setValue(newValue);
        }

        const next = this.getNextField();
        if (next) {
            next.updateActive();
        }
    }
}
