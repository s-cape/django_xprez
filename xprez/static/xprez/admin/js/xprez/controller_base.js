export class XprezControllerBase {
    constructor(parent, el) {
        this.parent = parent;
        this.el = el;
        this.el._xprezController = this;
    }

    get xprez() { return this._findAncestor("Xprez"); }
    get config() { return this._findAncestor("XprezConfigBase"); }
    get module() { return this._findAncestor("XprezModule"); }
    get section() { return this._findAncestor("XprezSection"); }

    mountChild(el, options={}) {
        if (el == null && options.allowNull) return null;
        const ControllerClass = window[el.dataset.controller];
        if (!ControllerClass) {
            throw new Error(`[xprez] Controller class "${el.dataset.controller}" not found`);
        }
        if (el._xprezController) {
            throw new Error(`[xprez] Double-binding: ${el._xprezController.constructor.name} already bound`, { cause: el });
        }
        return new ControllerClass(this, el);
    }

    _isInstance(obj, className) {
        let proto = obj;
        while (proto !== null) {
            if (proto.constructor?.name === className) return true;
            proto = Object.getPrototypeOf(proto);
        }
        return false;
    }

    _findAncestor(className) {
        let p = this;
        while (p !== null) {
            if (this._isInstance(p, className)) return p;
            p = p.parent;
        }
        return null;
    }
}
