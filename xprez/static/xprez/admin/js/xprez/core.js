import { XprezSection } from './sections.js';
import { XprezAdderContainerEnd } from './adders.js';
import { XprezSortable } from './sortable.js';

export class Xprez {
    constructor() {
        this.el = document.querySelector("[data-component='xprez']");
        this.defaults = JSON.parse(this.el.dataset.defaults || '{}');
        this.sectionsContainerEl = this.el.querySelector("[data-component='xprez-sections-container']");
        this.viewSelectEl = this.el.querySelector("[data-component='xprez-view-select']");
        this.viewSelectEl.addEventListener("change", this.updateView.bind(this));
        this.sections = [];
        this.el.querySelectorAll("[data-component='xprez-section']").forEach(this.initSection.bind(this));

        this.updateView();
        this.adder = new XprezAdderContainerEnd(this, this.el.querySelector("[data-component='xprez-adder-container-end']"));
        this.initAllSectionsCollapser();
        this.initSectionsSortable();

        // this.sections[0].popover.show();
    }

    initSection(sectionEl) {
        const section = new XprezSection(this, sectionEl);
        this.sections.push(section);
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
        this.sectionsContainerEl.querySelectorAll("[data-component='xprez-section']").forEach(
            (sectionEl, sectionIndex) => {
                const sectionPositionInputEl = sectionEl.querySelector(`input[name="${sectionEl.dataset.prefix}-position"]`);
                sectionPositionInputEl.value = sectionIndex;

                const sectionId = sectionEl.querySelector('input[name="section-id"]').value;

                sectionEl.querySelectorAll("[data-component='xprez-module']").forEach(
                    (moduleEl, moduleIndex) => {
                        const modulePositionInputEl = moduleEl.querySelector(`input[name="${moduleEl.dataset.prefix}-position"]`);
                        modulePositionInputEl.value = moduleIndex;

                        const moduleSectionInputEl = moduleEl.querySelector(`input[name="${moduleEl.dataset.prefix}-section"]`);
                        moduleSectionInputEl.value = sectionId;
                    }
                );
            }
        );
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
