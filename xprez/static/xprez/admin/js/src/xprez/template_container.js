import { XprezAdderSublistBase } from './adders_sublist_base.js';

export class XprezTemplateContainerList extends XprezAdderSublistBase {
    findTriggerEl() {
        return this.adder.el.querySelector('[data-xprez-templatecontainer-list-trigger]');
    }

    onLoad() {
        this.listContainerEl.querySelectorAll('[data-xprez-templatecontainer-paste]').forEach(btn => {
            btn.addEventListener('click', () => this.onPaste(btn));
        });
    }
}
