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

export class XprezCustomToggle {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.selectEl = this.parent.el.querySelector(`[name="${this.el.getAttribute("data-custom-toggle-select")}"]`);
        this.selectEl.addEventListener("change", () => this.updateVisibility());
        this.updateVisibility();
    }

    updateVisibility() {
        if (this.selectEl.value === "custom") {
            this.el.removeAttribute("data-hidden");
        } else {
            this.el.setAttribute("data-hidden", "");
        }
    }
}
