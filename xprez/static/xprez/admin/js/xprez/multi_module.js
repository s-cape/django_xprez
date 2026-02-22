import { XprezModule } from './modules.js';
import { XprezSortable } from './sortable.js';
import { XprezMultiModuleItemDeleter } from './deleters.js';
import {
    XprezMultiModuleAdder,
    XprezUploadMultiModuleAdder,
} from './adders.js';

export class XprezMultiModuleItem {
    constructor(module, itemEl) {
        this.module = module;
        this.el = itemEl;
        const trigger = this.el.querySelector(
            "[data-component='xprez-multi-module-item-delete']"
        );
        this.prefix = trigger
            ? trigger.dataset.targetPrefix
            : `item-${this.el.querySelector('input[name="item-id"]')?.value ?? ''}`;
        this.deleter = new XprezMultiModuleItemDeleter(this);
    }
}

export class XprezMultiModuleBase extends XprezModule {
    constructor(section, moduleEl) {
        super(section, moduleEl);
        this.items = [];
        this.itemsContainer = this.el.querySelector(
            "[data-component='xprez-multi-module-items']"
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
            draggable: '[data-component="xprez-multi-module-item"]',
        });
    }

    initItem(itemEl) {
        const ControllerClass =
            window[itemEl.dataset.jsControllerClass] || XprezMultiModuleItem;
        const item = new ControllerClass(this, itemEl);
        this.items.push(item);
        return item;
    }

    initItems() {
        this.itemsContainer
            .querySelectorAll('[data-component="xprez-multi-module-item"]')
            .forEach((itemEl) => this.initItem(itemEl));
    }

    initAdder() {
        const { adderSelector, adderClass } = this.constructor;
        if (adderSelector && adderClass) {
            const el = this.el.querySelector(adderSelector);
            if (el) new adderClass(this.section.xprez, el, this);
        }
    }
}

export class XprezMultiModule extends XprezMultiModuleBase {
    static adderSelector = "[data-component='xprez-adder-multi-module']";
    static adderClass = XprezMultiModuleAdder;
}

export class XprezUploadMultiModule extends XprezMultiModuleBase {
    static adderSelector = "[data-component='xprez-adder-upload-multi-module']";
    static adderClass = XprezUploadMultiModuleAdder;
}
