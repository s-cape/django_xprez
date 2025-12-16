import { XprezModulePopover } from './popovers.js';
import { XprezModuleDeleter } from './deleters.js';

export class XprezModule {
    constructor(section, moduleEl) {
        this.section = section;
        this.el = moduleEl;
        this.popover = new XprezModulePopover(this);
        this.deleter = new XprezModuleDeleter(this);
    }
}
