(function() {
    class Xprez {
        constructor() { 
            this.el = document.querySelector("[data-component='xprez']");
            this.sectionsContainerEl = this.el.querySelector("[data-component='xprez-sections-container']");
            this.viewSelectEl = this.el.querySelector("[data-component='xprez-view-select']");
            this.viewSelectEl.addEventListener("change", this.updateView.bind(this));
            this.sections = {};
            this.el.querySelectorAll("[data-component='xprez-section']").forEach(
                this.initSection.bind(this)
            );
        
            this.updateView();
            this.addList = new XprezAddListContainerEnd(this, this.el.querySelector("[data-component='xprez-add-list-container-end']"));
            // this.updatePositions();
        }

        initSection(sectionEl) { 
            const section = new XprezSection(this, sectionEl);
            this.sections[sectionEl.dataset.id] = section;
        }

        updateView() {
            this.el.dataset.view = this.viewSelectEl.value;
        }

        getContents() {
            return Object.values(this.sections).flatMap(section => section.contents);
        }

        sayHello() {
            console.log(this.getContents());
        }
    
        setPlacementToData() {
            this.sectionsContainerEl.querySelectorAll("[data-component='xprez-section']").forEach(
                (section, sectionIndex) => {
                    const positionInputEl = section.querySelector(`input[name="${section.dataset.prefix}-position"]`);
                    positionInputEl.value = sectionIndex;
                
                    section.querySelectorAll("[data-component='xprez-content']").forEach(
                        (content, contentIndex) => {
                            const positionInputEl = content.querySelector(`input[name="${content.dataset.prefix}-position"]`);
                            positionInputEl.value = contentIndex;
                        }
                    );
                }
            );
        }
    }

    class XprezAddListBase {
        constructor(xprez, el) {
            this.xprez = xprez;
            this.el = el;
        
            this.el.querySelectorAll("[data-component='xprez-add-item']").forEach(
                this.initItem.bind(this)
            );
        }
            
        initItem(itemEl) {
            itemEl.addEventListener("click", (e) => {
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
                        this.xprez.setPlacementToData();
                    })
                    .catch(error => {
                        console.error('Error adding content:', error);
                    });
            });
        }
    
        placeNewElement(el) {}
        initNewElement(el) {}
    }

    class XprezAddListContainerEnd extends XprezAddListBase {
        placeNewElement(el) {
            this.xprez.sectionsContainerEl.appendChild(el);
        }
        initNewElement(el) {
            this.xprez.initSection(el);
        }
    }

    class XprezSection {
        constructor(xprez, sectionEl) {
            this.xprez = xprez;
            this.el = sectionEl;
            this.contents = {};
            this.el.querySelectorAll("[data-component='xprez-content']").forEach(
                this.initContent.bind(this)
            );
            this.popover = new XprezSectionPopover(this);
        
            // this.xprezAddListBefore = new XprezAddList(this.xprez, this.el.querySelector("[data-component='xprez-add-list-section-before']"));
            // this.xprezAddListEnd = new XprezAddList(this.xprez, this.el.querySelector("[data-component='xprez-add-list-section-end']"));
            // this.el.querySelectorAll("[data-component='xprez-add-content-trigger']").forEach(
            //     this.xprez.initAddContentTrigger.bind(this.xprez)
            // );
        }

        initContent(contentEl) {
            const ControllerClass = window[contentEl.dataset.jsControllerClass];
            if (!ControllerClass) {
                console.error(`Controller class ${contentEl.dataset.jsControllerClass} not found`);
                return;
            }
            const content = new ControllerClass(this, contentEl);
            this.contents[contentEl.querySelector("input[name='content-id']").value] = content;
        }
    }

   class XprezContent {
        constructor(section, contentEl) {
            this.section = section;
            this.el = contentEl;
            this.popover = new XprezContentPopover(this);
        }
    }
    
    class XprezPopoverBase {
        constructor(...args) {
            this.bindElements(...args);
            this.bindEvents();
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
