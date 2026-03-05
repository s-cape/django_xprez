import { XprezSection, XprezSectionSymlink } from './sections.js';
import { XprezSectionAdderContainerEnd } from './adders.js';
import { XprezSortable } from './sortable.js';
import { XprezSyncManager } from './sync.js';

export class Xprez {
    constructor() {
        this.el = document.querySelector("[data-component='xprez']");
        this.sectionsContainerEl = this.el.querySelector("[data-component='xprez-sections-container']");
        this.viewSelectEl = this.el.querySelector("[data-component='xprez-view-select']");
        this.viewSelectEl.addEventListener("change", this.updateView.bind(this));
        this.sync = new XprezSyncManager(this);
        this.initSections();
        this.updateView();
        this.adder = new XprezSectionAdderContainerEnd(this, this.el.querySelector("[data-component='xprez-adder-container-end']"));
        this.initAllSectionsCollapser();
        this.initSectionsSortable();
    }

    initSections() {
        this.sections = [];
        this.sectionSymlinks = [];
        this.sectionsContainerEl.querySelectorAll(
            "[data-component='xprez-section'], [data-component='xprez-section-symlink']"
        ).forEach(this.initSection.bind(this));
    }

    initSection(el) {
        if (el.dataset.component === "xprez-section") {
            const section = new XprezSection(this, el);
            this.sections.push(section);
            return section;
        } else if (el.dataset.component === "xprez-section-symlink") {
            const sectionSymlink = new XprezSectionSymlink(this, el);
            this.sectionSymlinks.push(sectionSymlink);
            return sectionSymlink;
        } else throw new Error(el.dataset.component);
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
            "[data-component='xprez-section'], [data-component='xprez-section-symlink']"
        ).forEach((sectionEl, sectionIndex) => {
            sectionEl.querySelector(`input[name="${sectionEl.dataset.prefix}-position"]`).value = sectionIndex;
        });

        this.sections.forEach(section => {
            const sectionId = section.el.querySelector('input[name="section-id"]').value;
            section.el.querySelectorAll("[data-component='xprez-module']").forEach(
                (moduleEl, moduleIndex) => {
                    moduleEl.querySelector(`input[name="${moduleEl.dataset.prefix}-position"]`).value = moduleIndex;
                    moduleEl.querySelector(`input[name="${moduleEl.dataset.prefix}-section"]`).value = sectionId;
                }
            );
        });
    }

    initAllSectionsCollapser() {
        this.allSectionsCollapserEl = this.el.querySelector("[data-component='xprez-all-sections-collapser']");
        this.allSectionsCollapserEl.addEventListener("click", function() {
            for (const section of Object.values(this.sections)) { section.collapse(); }
        }.bind(this));
    }

    initSectionsSortable() {
        this.sectionsSortable = new XprezSortable(this.sectionsContainerEl, {
            handle: '[data-draggable-section-handle]',
            onEnd: () => this.setPlacementToInputs()
        });
    }
}
