import { XprezSection } from './section.js';
import { XprezAddContainerEnd } from './adders.js';
import { XprezSortable } from './sortable.js';

export class Xprez {
    constructor() {
        this.el = document.querySelector("[data-component='xprez']");
        this.sectionsContainerEl = this.el.querySelector("[data-component='xprez-sections-container']");
        this.viewSelectEl = this.el.querySelector("[data-component='xprez-view-select']");
        this.viewSelectEl.addEventListener("change", this.updateView.bind(this));
        this.sections = [];
        this.el.querySelectorAll("[data-component='xprez-section']").forEach(this.initSection.bind(this));

        this.updateView();
        this.add = new XprezAddContainerEnd(this, this.el.querySelector("[data-component='xprez-add-container-end']"));
        this.initAllSectionsCollapser();
        this.initSectionsSortable();

        // TODO open first section, just for development
        // this.sections[0].popover.show();
    }

    initSection(sectionEl) {
        const section = new XprezSection(this, sectionEl);
        this.sections.push(section);
    }

    updateView() {
        this.el.dataset.view = this.viewSelectEl.value;
    }

    getContents() {
        return this.sections.flatMap(section => section.contents);
    }

    getPopovers() {
        const sectionPopovers = this.sections.flatMap(section => section.popover);
        const contentPopovers = this.getContents().flatMap(content => content.popover);
        return [...sectionPopovers, ...contentPopovers];
    }

    setPlacementToInputs() {
        this.sectionsContainerEl.querySelectorAll("[data-component='xprez-section']").forEach(
            (sectionEl, sectionIndex) => {
                const sectionPositionInputEl = sectionEl.querySelector(`input[name="${sectionEl.dataset.prefix}-position"]`);
                sectionPositionInputEl.value = sectionIndex;

                const sectionId = sectionEl.querySelector('input[name="section-id"]').value;

                sectionEl.querySelectorAll("[data-component='xprez-content']").forEach(
                    (contentEl, contentIndex) => {
                        const contentPositionInputEl = contentEl.querySelector(`input[name="${contentEl.dataset.prefix}-position"]`);
                        contentPositionInputEl.value = contentIndex;

                        const contentSectionInputEl = contentEl.querySelector(`input[name="${contentEl.dataset.prefix}-section"]`);
                        contentSectionInputEl.value = sectionId;
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

