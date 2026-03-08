import { XprezSectionSymlink } from './sections.js';
import { XprezSortable } from './sortable.js';
import { XprezSyncManager } from './sync.js';
import { XprezControllerBase } from './controller_base.js';

export class Xprez extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
        this.sectionsContainerEl = this.el.querySelector("[data-xprez-sections-container]");
        this.viewSelectEl = this.el.querySelector("[data-xprez-view-select]");
        this.viewSelectEl.addEventListener("change", this.updateView.bind(this));
        this.sync = new XprezSyncManager(this);
        this.initSections();
        this.updateView();
        this.adder = this.mountChildOrNull(
            this.el.querySelector("[data-controller='XprezSectionAdderContainerEnd']")
        );
        this.allSectionsCollapseExpand = this.mountChildOrNull(
            this.el.querySelector("[data-controller='XprezAllSectionsCollapseExpand']")
        );
        this.initSectionsSortable();
    }

    initSections() {
        this.sections = [];
        this.sectionSymlinks = [];
        this.sectionsContainerEl.querySelectorAll(
            "[data-controller='XprezSection'], [data-controller='XprezSectionSymlink']"
        ).forEach(this.initSection.bind(this));
    }

    initSection(el) {
        const controller = this.mountChild(el);
        if (controller instanceof XprezSectionSymlink) {
            this.sectionSymlinks.push(controller);
        } else {
            this.sections.push(controller);
        }
        return controller;
    }

    updateView() {
        this.el.dataset.view = this.viewSelectEl.value;
    }

    getModules() {
        return this.sections.flatMap(section => section.modules);
    }

    getPopovers() {
        const sectionPopovers = this.sections.flatMap(section => section.popover);
        const modulePopovers = this.getModules().flatMap(module => module.popover);
        return [...sectionPopovers, ...modulePopovers];
    }

    setPlacementToInputs() {
        this.sectionsContainerEl.querySelectorAll(
            "[data-controller='XprezSection'], [data-controller='XprezSectionSymlink']"
        ).forEach((sectionEl, sectionIndex) => {
            sectionEl.querySelector(`input[name="${sectionEl.dataset.prefix}-position"]`).value = sectionIndex;
        });

        this.sections.forEach(section => {
            const sectionId = section.el.querySelector('input[name="section-id"]').value;
            Array.from(section.gridEl.children).forEach((moduleEl, moduleIndex) => {
                moduleEl.querySelector(`input[name="${moduleEl.dataset.prefix}-position"]`).value = moduleIndex;
                moduleEl.querySelector(`input[name="${moduleEl.dataset.prefix}-section"]`).value = sectionId;
            });
        });
    }

    initSectionsSortable() {
        this.sectionsSortable = new XprezSortable(this.sectionsContainerEl, {
            handle: '[data-draggable-section-handle]',
            onEnd: () => this.setPlacementToInputs()
        });
    }
}
