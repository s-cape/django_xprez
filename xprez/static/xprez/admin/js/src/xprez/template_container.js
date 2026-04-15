import { XprezPopoverBase } from './popovers.js';
import { WithAdderSublist } from './adders_sublist_base.js';

export class XprezTemplateContainerList extends WithAdderSublist(XprezPopoverBase) {
    constructor(adder, el) {
        super(adder, el);
        this.triggerEl = adder.el.querySelector('[data-xprez-templatecontainer-list-trigger]');
        this.listContainerEl = el.querySelector('[data-xprez-templatecontainer-list-container]');
        this.filterEl = el.querySelector('[data-xprez-templatecontainer-filter]');
        this.filterEl.addEventListener('input', () => this.applyFilter());
    }

    show() {
        this.adder.clipboardList?.hide();
        this.filterEl.value = '';
        super.show();
        this.filterEl.focus();
        this.loadList();
    }

    onLoad() {
        this.listContainerEl.querySelectorAll('[data-xprez-templatecontainer-paste]').forEach(btn => {
            btn.addEventListener('click', () => this.onPaste(btn));
        });
        this.applyFilter();
    }

    applyFilter() {
        const q = this.filterEl.value.toLowerCase();
        this.listContainerEl.querySelectorAll('.xprez-templatecontainer-list__item').forEach(item => {
            const searchable = [
                item.dataset.filterId,
                item.dataset.filterDescription,
                item.dataset.filterKeywords,
            ].join(' ').toLowerCase();
            if (searchable.includes(q)) {
                item.removeAttribute('data-hidden');
            } else {
                item.setAttribute('data-hidden', '');
            }
        });
    }
}
