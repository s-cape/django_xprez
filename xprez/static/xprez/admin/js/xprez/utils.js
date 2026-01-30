export function executeScripts(el) {
    el.querySelectorAll("script").forEach(script => {
        const newScript = document.createElement("script");
        if (script.src) {
            newScript.src = script.src;
            newScript.async = script.async;
            document.body.appendChild(newScript);
        } else {
            newScript.textContent = script.textContent;
            document.body.appendChild(newScript);
        }
    });
}

export class XprezShowWhen {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        const [fieldName, targetValue] = this.el.getAttribute("data-show-when").split(":");
        this.selectEl = this.parent.el.querySelector(`[name="${fieldName}"]`);
        this.targetValue = targetValue;
        if (this.selectEl) {
            this.selectEl.addEventListener("change", () => this.updateVisibility());
            this.updateVisibility();
        }
    }

    updateVisibility() {
        if (!this.selectEl) return;
        const currentValue =
            this.selectEl.type === "checkbox"
                ? this.selectEl.checked
                    ? "true"
                    : "false"
                : this.selectEl.value;
        if (currentValue === this.targetValue) {
            this.el.removeAttribute("data-hidden");
        } else {
            this.el.setAttribute("data-hidden", "");
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
        this.initListeners();
        this.setLinked(this.allGroupsMatch());
    }

    // Parsing & helpers

    parseGroups(str) {
        if (!str) return [];
        return str.split(',').map(g => g.split(':').filter(Boolean)).filter(g => g.length > 1);
    }

    getFieldController(name) {
        if (this.parent.getFieldByInputName) {
            return this.parent.getFieldByInputName(name);
        }
        return null;
    }

    getFieldInput(name) {
        const controller = this.getFieldController(name);
        if (controller) return controller.inputEl;
        return this.parent.el.querySelector(`[name="${name}"]`);
    }

    getFieldWrapper(name) {
        const controller = this.getFieldController(name);
        if (controller) return controller.el;
        const input = this.parent.el.querySelector(`[name="${name}"]`);
        return input ? input.closest('.xprez-option') : null;
    }

    getFieldValue(name) {
        const controller = this.getFieldController(name);
        if (controller) return controller.getValue();
        const input = this.parent.el.querySelector(`[name="${name}"]`);
        return input?.value ?? null;
    }

    setFieldValue(name, value) {
        const controller = this.getFieldController(name);
        if (controller) {
            controller.setValue(value);
            return;
        }
        const input = this.parent.el.querySelector(`[name="${name}"]`);
        if (input && input.value !== value) {
            input.value = value;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        }
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

    syncAllGroups() {
        this.groups.forEach(group => {
            const value = this.getFieldValue(group[0]);
            if (value == null) return;
            group.slice(1).forEach(name => {
                if (this.getFieldValue(name) !== value) {
                    this.setFieldValue(name, value);
                }
            });
        });
    }

    syncGroup(event, group) {
        if (!this.checkbox.checked) return;
        const { name: sourceName } = event.target;
        const value = this.getFieldValue(sourceName);
        group.forEach(name => {
            if (name === sourceName) return;
            if (this.getFieldValue(name) !== value) {
                this.setFieldValue(name, value);
            }
        });
    }

    // Listeners

    initListeners() {
        this.checkbox.addEventListener('change', () => {
            this.updateUI();
            if (this.checkbox.checked) this.syncAllGroups();
        });
        this.groups.forEach(group => {
            group.forEach(name => {
                const input = this.getFieldInput(name);
                if (input) {
                    input.addEventListener('input', e => this.syncGroup(e, group));
                    input.addEventListener('change', e => this.syncGroup(e, group));
                }
            });
        });
    }
}
