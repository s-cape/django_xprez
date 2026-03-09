import { XprezModule } from './modules.js';
import { XprezSortable } from './sortable.js';
import { XprezMultiModuleItemDeleter } from './deleters.js';
import { XprezControllerBase } from './controller_base.js';

export class XprezMultiModuleItem extends XprezControllerBase {
    constructor(module, itemEl) {
        super(module, itemEl);
        this.deleter = new XprezMultiModuleItemDeleter(this);
    }
}

export class XprezMultiModuleBase extends XprezModule {
    constructor(section, moduleEl) {
        super(section, moduleEl);
        this.items = [];
        this.itemsContainer = this.el.querySelector(
            "[data-xprez-multi-module-items]"
        );
        if (!this.itemsContainer) return;

        this.initSortable();
        this.initItems();
        this.initAdder();
    }

    initSortable() {
        const handleSelector = '[data-draggable-multi-module-item-handle]';
        const hasHandles =
            this.itemsContainer.querySelector(handleSelector) !== null;
        this.sortable = new XprezSortable(this.itemsContainer, {
            handle: hasHandles ? handleSelector : undefined,
            draggable: '[data-controller]',
            onEnd: () => this.setItemPositionsToInputs(),
        });
    }

    setItemPositionsToInputs() {
        Array.from(this.itemsContainer.children).forEach((itemEl, itemIndex) => {
            const input = itemEl.querySelector(
                `input[name="${itemEl.dataset.prefix}-position"]`
            );
            if (input) input.value = itemIndex;
        });
    }

    initItem(itemEl) {
        const item = this.mountChild(itemEl);
        this.items.push(item);
        return item;
    }

    initItems() {
        Array.from(this.itemsContainer.children).forEach(
            (itemEl) => this.initItem(itemEl)
        );
    }

    initAdder() {
        const { adderSelector } = this.constructor;
        if (adderSelector) {
            const el = this.el.querySelector(adderSelector);
            if (el) this.mountChild(el);
        }
    }
}

export class XprezMultiModule extends XprezMultiModuleBase {
    static adderSelector = "[data-controller='XprezMultiModuleAdder']";
}

export class XprezUploadMultiModule extends XprezMultiModuleBase {
    static adderSelector = "[data-controller='XprezUploadMultiModuleAdder']";
}
