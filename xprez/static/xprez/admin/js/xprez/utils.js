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
