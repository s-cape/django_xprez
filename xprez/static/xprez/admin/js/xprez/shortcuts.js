const ADVANCED = "advanced";

export class XprezShortcutFieldController {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.inputEl = el.querySelector('select');
        this.config = JSON.parse(this.inputEl.dataset.shortcut);
        this.el.addEventListener("click", (e) => e.stopPropagation());
        this.inputEl.addEventListener("focus", (e) => this._onSelectActivate(e));
        this.inputEl.addEventListener("change", () => this._onChange());
        this.check();
    }

    getValue() { return this.inputEl.value; }

    check() {
        if (this.config.clone) {
            const field = this.parent.fields?.find(
                (f) => f.fieldName === this.config.clone
            );
            this.inputEl.value = field ? field.getValue() : "";
        } else {
            const sync = this.parent.xprez.sync;
            for (const [fieldName, breakpointMap] of Object.entries(this.config)) {
                const presetKeys = Object.keys(breakpointMap).filter((k) => k !== ADVANCED);
                const breakpoints = Object.keys(breakpointMap[presetKeys[0]] || {}).map(Number);
                const matched = presetKeys.find((key) =>
                    breakpoints.every(
                        (bp) => String(sync.getEffectiveValue(this.parent, bp, fieldName) ?? "") === String(breakpointMap[key][bp])
                    )
                );
                this.inputEl.value = matched ?? ADVANCED;
            }
        }
    }

    _onSelectActivate(e) {
        if (!this.parent.popover.isOpen()) {
            this.parent.popover.hideOthers();
        }
        if (this.getValue() === ADVANCED) {
            this.inputEl.blur();
            this.parent.popover.show();
        }
    }

    _onChange() {
        const value = this.getValue();
        if (value === ADVANCED) {
            this.parent.popover.show();
            if (this.config.clone) {
                this._apply(value);
            }
        } else {
            this._apply(value);
        }
    }

    _apply(value) {
        const sync = this.parent.xprez.sync;
        if (this.config.clone) {
            sync.queueItem(this.parent, null, this.config.clone, String(value));
        } else {
            for (const [fieldName, breakpointMap] of Object.entries(this.config)) {
                const desiredValues = breakpointMap[value];
                if (!desiredValues) continue;
                for (const [breakpoint, desiredValue] of Object.entries(desiredValues)) {
                    sync.queueItem(this.parent, parseInt(breakpoint), fieldName, String(desiredValue));
                }
            }
        }
        sync.processQueue();
    }
}

export const XprezShortcutParentMixin = {
    initShortcuts() {
        this.shortcuts = [];
        this.shortcutsEl = this.el.querySelector("[data-component='xprez-shortcuts']");
        if (this.shortcutsEl) {
            this.shortcutsEl.querySelectorAll('[data-js-controller-class="XprezShortcutFieldController"]').forEach((fieldEl) => {
                this.shortcuts.push(new XprezShortcutFieldController(this, fieldEl));
            });
            this.shortcutsEl.removeAttribute("data-hidden");
        }
    },

    checkShortcuts() {
        for (const shortcut of this.shortcuts) shortcut.check();
    },
};
