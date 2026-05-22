import { XprezSectionSymlink, XprezContainerSymlink } from './sections.js';
import { XprezSortable } from './sortable.js';
import { XprezSyncManager } from './sync.js';
import { XprezControllerBase } from './controller_base.js';
import { WithSignals } from './signals.js';

export class Xprez extends WithSignals(XprezControllerBase) {
    static KEY = "xprez";
    constructor() {
        super(null, document.querySelector("[data-controller='Xprez']"));
        this.ready = false;
        this.sectionsContainerEl = this.el.querySelector("[data-xprez-sections-container]");
        this.viewSelectEl = this.el.querySelector("[data-xprez-view-select]");
        this.viewSelectEl.addEventListener("change", this.updateView.bind(this));
        this.sync = new XprezSyncManager(this);
        this.initSections();
        this.updateView();
        this.adder = this.mountChild(
            this.el.querySelector("[data-controller='XprezSectionAdderContainerEnd']"),
            {allowNull: true}
        );
        this.allSectionsCollapseExpand = this.mountChild(
            this.el.querySelector("[data-controller='XprezAllSectionsCollapseExpand']"),
            {allowNull: true}
        );
        this.clipboardClipContainer = this.mountChild(
            this.el.querySelector("[data-controller='XprezClipboardClipContainer']"),
            {allowNull: true}
        );
        this.initSectionsSortable();
        this.ready = true;
        this.emit("ready");
    }

    initSections() {
        this.sections = [];
        this.sectionSymlinks = [];
        this.sectionsContainerEl.querySelectorAll(
            "[data-controller='XprezSection'], [data-controller='XprezSectionSymlink'], [data-controller='XprezContainerSymlink']"
        ).forEach(this.initSection.bind(this));
    }

    initSection(el) {
        const controller = this.mountChild(el);
        if (
            controller instanceof XprezSectionSymlink
            || controller instanceof XprezContainerSymlink
        ) {
            this.sectionSymlinks.push(controller);
        } else {
            this.sections.push(controller);
        }
        if (this.ready) { this.emit("section-rows-changed"); }
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
            "[data-controller='XprezSection'], [data-controller='XprezSectionSymlink'], [data-controller='XprezContainerSymlink']"
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

    /* Levels: debug, info, success, warning, error. */
    message(level, message) {
        /* TODO: Implement message display. */
        alert(`${String(level)}: ${message}`);
    }

    /** Log error to console and show it via message("error", ...). */
    reportError(error, context) {
        if (context) {
            console.error(context, error);
        } else {
            console.error(error);
        }
        this.message("error", error?.message || "Something went wrong.");
    }
}
