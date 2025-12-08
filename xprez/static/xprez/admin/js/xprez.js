(function() {
    const SORTABLE_BASE_CONFIG = {
        animation: 150,
        filter: 'input, textarea, select, [contenteditable]',
        preventOnFilter: false,
        onMove: (evt) => {
            return !evt.related.closest('input, textarea, select, [contenteditable="true"]');
        }
    };

    class Xprez {
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
            new Sortable(this.sectionsContainerEl, {
                ...SORTABLE_BASE_CONFIG,
                handle: '[data-draggable-section-handle]',
                onEnd: () => this.setPlacementToInputs()
            });
        }
    }

    class XprezAddBase {
        constructor(xprez, el) {
            this.xprez = xprez;
            this.el = el;

            this.el.querySelectorAll("[data-component='xprez-add-item']").forEach(
                this.initItem.bind(this)
            );
        }

        initItem(itemEl) {
            itemEl.addEventListener("click", this.add.bind(this, itemEl));
        }

        add(itemEl) {
            fetch(itemEl.dataset.url)
                .then(response => {
                    if (response.ok) {
                        return response.text();
                    } else {
                        console.log("TODO: show error message");
                        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                    }
                })
                .then(html => {
                    const newEl = new DOMParser().parseFromString(html, 'text/html').body.firstElementChild;
                    this.placeNewElement(newEl);
                    this.initNewElement(newEl);
                    executeScripts(newEl);
                    this.xprez.setPlacementToInputs();
                })
                .catch(error => {
                    console.error('Error adding content:', error);
                });
        }

        placeNewElement(el) {}
        initNewElement(el) {}
    }

    class XprezAddContainerEnd extends XprezAddBase {
        placeNewElement(el) { this.xprez.sectionsContainerEl.appendChild(el); }
        initNewElement(el) { this.xprez.initSection(el); }
    }

    class XprezAddSectionBase extends XprezAddBase {
        constructor(xprez, el, section) {
            super(xprez, el);
            this.section = section;
            this.setTriggerEl();
            this.triggerEl.addEventListener("click", this.toggle.bind(this));
        }
        setTriggerEl() {}
        add(itemEl) {
            super.add(itemEl);
            this.hide();
        }
        isVisible() { return !this.el.hasAttribute("data-hidden"); }
        show() { this.el.removeAttribute("data-hidden"); }
        hide() { this.el.setAttribute("data-hidden", ""); }
        toggle() { this.isVisible() ? this.hide() : this.show(); }
    }

    class XprezAddSectionBefore extends XprezAddSectionBase {
        setTriggerEl() { this.triggerEl = this.section.el.querySelector("[data-component='xprez-add-section-before-trigger']"); }
        placeNewElement(el) { this.section.el.before(el); }
        initNewElement(el) { this.xprez.initSection(el); }
    }

    class XprezAddSectionEnd extends XprezAddSectionBase {
        setTriggerEl() { this.triggerEl = this.section.el.querySelector("[data-component='xprez-add-section-end-trigger']"); }
        placeNewElement(el) { this.section.gridEl.appendChild(el); }
        initNewElement(el) { this.section.initContent(el); }
    }

    class XprezSection {
        constructor(xprez, sectionEl) {
            this.xprez = xprez;
            this.el = sectionEl;
            this.gridEl = this.el.querySelector("[data-component='xprez-section-grid']");
            this.initContents();
            this.popover = new XprezSectionPopover(this);
            this.addSectionBefore = new XprezAddSectionBefore(this.xprez, this.el.querySelector("[data-component='xprez-add-section-before']"), this);
            this.addSectionEnd = new XprezAddSectionEnd(this.xprez, this.el.querySelector("[data-component='xprez-add-section-end']"), this);
            this.deleter = new XprezSectionDeleter(this);

            this.initCollapser();
            this.initConfigs();
            this.initContentsSortable();
        }

        id() { return this.el.querySelector("[name='section-id']").value; }

        initContents() {
            this.contents = [];
            this.el.querySelectorAll("[data-component='xprez-content']").forEach(
                this.initContent.bind(this)
            );
        }
        initContent(contentEl) {
            const ControllerClass = window[contentEl.dataset.jsControllerClass];
            if (!ControllerClass) {
                console.error(`Controller class ${contentEl.dataset.jsControllerClass} not found`);
                return;
            }
            const content = new ControllerClass(this, contentEl);
            this.contents.push(content);
        }

        initConfigs() {
            this.configs = [];
            this.el.querySelectorAll("[data-component='xprez-section-config']").forEach(
                this.initConfig.bind(this)
            );
        }
        initConfig(configEl) {
            this.configs.push(new XprezSectionConfig(this, configEl));
        }

        initCollapser() {
            this.collapserEl = this.el.querySelector("[data-component='xprez-section-collapser']");
            this.collapserEl.addEventListener("click", this.toggleCollapse.bind(this));
        }
        isCollapsed() { return this.el.hasAttribute("data-collapsed"); }
        collapse() { this.el.setAttribute("data-collapsed", ""); }
        expand() { this.el.removeAttribute("data-collapsed"); }
        toggleCollapse() { this.isCollapsed() ? this.expand() : this.collapse(); }

        initContentsSortable() {
            new Sortable(this.gridEl, {
                ...SORTABLE_BASE_CONFIG,
                group: 'xprez-contents',
                handle: '[data-draggable-content-handle]',
                onEnd: () => this.xprez.setPlacementToInputs()
            });
        }
    }

   class XprezContent {
        constructor(section, contentEl) {
            this.section = section;
            this.el = contentEl;
            this.popover = new XprezContentPopover(this);
            this.deleter = new XprezContentDeleter(this);
        }
    }

    class XprezDeleterBase {
        constructor(obj) {
            this.obj = obj;
            this.initElements();
            if (this.triggerEl) {
                this.triggerEl.addEventListener("click", this.delete.bind(this));
            }
            if (this.undoEl) {
                this.undoEl.addEventListener("click", this.undo.bind(this));
            }
        }
        initElements() { throw new Error("Not implemented"); }
        delete() { this.obj.el.dataset.mode = "delete"; this.inputEl.checked = true; }
        undo() { this.obj.el.dataset.mode = ""; this.inputEl.checked = false; }
    }

    class XprezSectionDeleter extends XprezDeleterBase {
        initElements() {
            this.triggerEl = this.obj.el.querySelector("[data-component='xprez-section-delete-trigger']");
            this.inputEl = this.triggerEl.querySelector("input");
            this.undoEl = this.obj.el.querySelector("[data-component='xprez-section-delete-undo']");
        }
    }

    class XprezContentDeleter extends XprezDeleterBase {
        initElements() {
            this.triggerEl = this.obj.el.querySelector("[data-component='xprez-content-delete-trigger']");
            this.inputEl = this.triggerEl.querySelector("input");
            this.undoEl = this.obj.el.querySelector("[data-component='xprez-content-delete-undo']");
        }
    }

    class XprezPopoverBase {
        constructor(...args) {
            this.bindElements(...args);
            this.bindEvents();
            this.openOnErrors();
        }

        bindEvents() {
            document.addEventListener("click", (e) => {
                if (this.isOpen() && (!e.target.closest("[popover]"))) {
                    this.hide();
                } else if (!this.isOpen() && this.triggerEl.contains(e.target)) {
                    this.show();
                }
            });
        }

        hasErrors() { return this.el.querySelector("[data-has-errors]"); }
        openOnErrors() {
            if (this.hasErrors()) {
                this.show();
            }
        }

        isOpen() { return this.el.matches(":popover-open"); }
        show() { this.el.showPopover(); }
        hide() { this.el.hidePopover(); }
    }

    class XprezSectionPopover extends XprezPopoverBase {
        bindElements(section) {
            this.section = section;
            this.el = this.section.el.querySelector("[data-component='xprez-section-popover']");
            this.triggerEl = this.section.el.querySelector("[data-component='xprez-section-popover-trigger']");
        }
        show() {
            this.section.xprez.getPopovers().filter(popover => popover !== this).forEach(popover => popover.hide());
            super.show();
            this.section.el.dataset.mode = "edit";
        }
        hide() {
            super.hide();
            this.section.el.dataset.mode = "";
        }
    }

    class XprezContentPopover extends XprezPopoverBase {
        bindElements(content) {
            this.content = content;
            this.el = this.content.el.querySelector("[data-component='xprez-content-popover']");
            this.triggerEl = this.content.el.querySelector("[data-component='xprez-content-popover-trigger']");
        }
        show() {
            super.show();
            this.content.el.dataset.mode = "edit";
        }
        hide() {
            super.hide();
            this.content.el.dataset.mode = "";
        }
    }

    class XprezConfigBase {
        constructor(el) {
            this.el = el;
        }
    }

    class XprezSectionConfig extends XprezConfigBase {
        constructor(section, ...args) {
            super(...args);
            this.section = section;
        }
    }

    class XprezContentConfig extends XprezConfigBase {
        constructor(content, ...args) {
            super(...args);
            this.content = content;
        }
    }

    function executeScripts(el) {
        el.querySelectorAll("script").forEach(script => {
            const newScript = document.createElement("script");
            if (script.src) {
                newScript.src = script.src;
                newScript.async = script.async;
                document.body.appendChild(newScript);
            } else {
                newScript.textContent = script.textContent;
                document.body.appendChild(newScript);
            }
        });
    }

    window.Xprez = Xprez;
    window.XprezContent = XprezContent;
})();
