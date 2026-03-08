export class XprezControllerBase {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.el._xprezController = this;
    }

    get xprez() {
        let p = this;
        while (p.parent !== null) {
            p = p.parent;
        }
        return p;
    }

    mountChild(el) {
        const ControllerClass = window[el.dataset.controller];
        if (!ControllerClass) {
            throw new Error(`[xprez] Controller class "${el.dataset.controller}" not found`);
        }
        if (el._xprezController) {
            throw new Error(`[xprez] Double-binding: ${el._xprezController.constructor.name} already bound`, { cause: el });
        }
        return new ControllerClass(this, el);
    }

    mountChildOrNull(el) {
        if (!el) return null;
        return this.mountChild(el);
    }
}
