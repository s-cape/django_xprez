import { XprezContentPopover } from './popovers.js';
import { XprezContentDeleter } from './deleters.js';

export class XprezContent {
    constructor(section, contentEl) {
        this.section = section;
        this.el = contentEl;
        this.popover = new XprezContentPopover(this);
        this.deleter = new XprezContentDeleter(this);
    }
}

