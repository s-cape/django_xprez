import { xprezExecuteScripts, xprezGetCsrfToken } from './utils.js';
import { XprezClipboardList } from './clipboard.js';

export class XprezAdderBase {
    constructor(xprez, el) {
        this.xprez = xprez;
        this.el = el;
        this._addingCount = 0;
        this.bindEvents();
    }

    bindEvents() {}

    setAddingStart() {
        this._addingCount++;
        this.el.setAttribute('data-adder-adding', '');
    }

    setAddingEnd() {
        this._addingCount--;
        if (this._addingCount <= 0) {
            this._addingCount = 0;
            this.el.removeAttribute('data-adder-adding');
        }
    }

    add(url) {
        this.setAddingStart();
        return fetch(url)
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    console.log("TODO: show error message");
                    throw new Error(`Server returned ${response.status}: ${response.statusText}`);
                }
            })
            .then(items => items.forEach(({ html }) => this.addFromHtml(html)))
            .catch(error => {
                console.error('Error adding:', error);
            })
            .finally(() => this.setAddingEnd());
    }

    addFromHtml(html) {
        const newEl = new DOMParser().parseFromString(html, 'text/html').body.firstElementChild;
        if (newEl) this.processNewElement(newEl);
    }

    processNewElement(newEl) {
        this.placeNewElement(newEl);
        this.initNewElement(newEl);
        xprezExecuteScripts(newEl);
    }

    placeNewElement(el) {}
    initNewElement(el) {}
}

export class XprezAdderItemsBase extends XprezAdderBase {
    bindEvents() {
        this.el.querySelectorAll("[data-component='xprez-add-item']").forEach(
            itemEl => itemEl.addEventListener("click", () => this.add(itemEl.dataset.url))
        );
    }

    processNewElement(newEl) {
        super.processNewElement(newEl);
        this.xprez.setPlacementToInputs();
    }
}

export class XprezDuplicateAdder extends XprezAdderItemsBase {
    constructor(xprez, el, copyMenu) {
        super(xprez, el);
        this.copyMenu = copyMenu;
    }

    bindEvents() {
        this.el.addEventListener('click', (e) => {
            e.stopPropagation();
            this.copyMenu.el.removeAttribute('data-open');
            this.add(this.el.dataset.url);
        });
    }

    placeNewElement(el) { this.copyMenu.parent.el.insertAdjacentElement('afterend', el); }
}

export class XprezSectionDuplicateAdder extends XprezDuplicateAdder {
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezModuleDuplicateAdder extends XprezDuplicateAdder {
    initNewElement(el) { this.copyMenu.parent.section.initModule(el); }
}

export class XprezAdderSelectBase extends XprezAdderBase {
    bindEvents() {
        this.selectEl = this.el.querySelector("select");
        this.options = this.selectEl.querySelectorAll("option");
        this.selectEl.addEventListener("change", this.onSelectChange.bind(this));
    }

    onSelectChange() {
        if (!this.selectEl.value) return;

        const selectedOption = this.selectEl.options[this.selectEl.selectedIndex];
        this.handleSelection(selectedOption);
        this.selectEl.value = "";
    }

    handleSelection(selectedOption) {
        this.add(selectedOption.dataset.url);
    }
}

export class XprezContentAdderBase extends XprezAdderItemsBase {
    constructor(xprez, el) {
        super(xprez, el);
        this.clipboardList = new XprezClipboardList(this);
    }
}

export class XprezSectionAdderContainerEnd extends XprezContentAdderBase {
    placeNewElement(el) { this.xprez.sectionsContainerEl.appendChild(el); }
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezContentAdderSectionBase extends XprezContentAdderBase {
    constructor(xprez, el, section) {
        super(xprez, el);
        this.section = section;
        this.setTriggerEl();
        this.triggerEl.addEventListener("click", this.toggle.bind(this));
    }

    setTriggerEl() {}

    add(url) {
        super.add(url);
        this.hide();
    }

    isOpen() { return !this.el.hasAttribute("data-hidden"); }
    show() { this.el.removeAttribute("data-hidden"); }
    hide() { this.el.setAttribute("data-hidden", ""); }
    toggle() { this.isOpen() ? this.hide() : this.show(); }
}

export class XprezSectionAdderSectionBefore extends XprezContentAdderSectionBase {
    setTriggerEl() {
        this.triggerEl = this.section.el.querySelector("[data-component='xprez-adder-section-before-trigger']");
    }
    placeNewElement(el) { this.section.el.before(el); }
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezModuleAdderSectionEnd extends XprezContentAdderSectionBase {
    setTriggerEl() {
        this.triggerEl = this.section.el.querySelector("[data-component='xprez-adder-section-end-trigger']");
    }
    placeNewElement(el) { this.section.gridEl.appendChild(el); }
    initNewElement(el) { this.section.initModule(el); }
}

export class XprezConfigAdderBase extends XprezAdderSelectBase {
    constructor(xprez, parent, componentName) {
        super(xprez, parent.el.querySelector(`[data-component='${componentName}']`));
        this.parent = parent;
        this.setOptionsDisabledState();
    }

    addBreakpoint(breakpoint) {
        const existingConfig = this.parent.configs.find(
            c => c.cssBreakpoint() === breakpoint
        );
        if (existingConfig) {
            if (existingConfig.isDeleted()) {
                existingConfig.deleter.undelete();
                this.setOptionsDisabledState();
            }
            return Promise.resolve();
        }
        const option = [...this.options].find(o => parseInt(o.value) === breakpoint);
        if (!option?.dataset.url) return Promise.resolve();
        return this.add(option.dataset.url);
    }

    handleSelection(selectedOption) {
        this.addBreakpoint(parseInt(selectedOption.value));
    }

    setOptionsDisabledState() {
        const existingBreakpoints = this.parent.configs
            .filter(config => !config.isDeleted())
            .map(config => config.cssBreakpoint());

        for (const option of this.options) {
            if (existingBreakpoints.includes(parseInt(option.value))) {
                option.setAttribute("disabled", "");
            } else {
                option.removeAttribute("disabled");
            }
        }
    }

    placeNewElement(newEl) {
        const newBreakpoint = parseInt(newEl.dataset.cssBreakpoint);
        for (const config of this.parent.configs) {
            if (newBreakpoint < config.cssBreakpoint()) {
                config.el.before(newEl);
                return;
            }
        }
        this.parent.configsContainerEl.appendChild(newEl);
    }

    initNewElement(newEl) {
        const config = this.parent.initConfig(newEl);
        config.copyValuesFromPreviousConfig();
        this.setOptionsDisabledState();
    }
}

export class XprezSectionConfigAdder extends XprezConfigAdderBase {
    constructor(xprez, section) {
        super(xprez, section, "xprez-adder-section-config");
        this.section = section;
    }
}

export class XprezModuleConfigAdder extends XprezConfigAdderBase {
    constructor(xprez, module) {
        super(xprez, module, "xprez-adder-module-config");
        this.module = module;
    }
}

export class XprezMultiModuleAdderBase extends XprezAdderBase {
    constructor(xprez, el, module) {
        super(xprez, el);
        this.module = module;
    }

    placeNewElement(el) {
        this.module.itemsContainer.appendChild(el);
        this.module.setItemPositionsToInputs();
    }
    initNewElement(el) { this.module.initItem(el); }
}

export class XprezMultiModuleAdder extends XprezMultiModuleAdderBase {
    bindEvents() {
        this.el.querySelectorAll("[data-component='xprez-add-item']").forEach(
            itemEl => itemEl.addEventListener('click', () => this.add(itemEl.dataset.url))
        );
    }
}

export class XprezUploadMultiModuleAdder extends XprezMultiModuleAdderBase {
    bindEvents() {
        const dropzone = this.el.querySelector("[data-component='xprez-multi-module-dropzone']");
        if (!dropzone) return;

        const fileInput = dropzone.querySelector("[data-component='xprez-multi-module-file-input']");
        const url = dropzone.dataset.uploadUrl;
        if (!fileInput || !url) return;

        dropzone.addEventListener('click', (e) => {
            if (e.target !== fileInput) fileInput.click();
        });
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('xprez-admin-adder__inner--dragover');
        });
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('xprez-admin-adder__inner--dragover');
        });
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('xprez-admin-adder__inner--dragover');
            this.uploadFiles(url, e.dataTransfer.files);
        });
        fileInput.addEventListener('change', () => {
            this.uploadFiles(url, fileInput.files);
            fileInput.value = '';
        });
    }

    uploadFiles(url, files) {
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            this.setAddingStart();
            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': xprezGetCsrfToken() },
                body: formData,
            })
                .then(response => {
                    if (!response.ok) throw new Error(`Upload error ${response.status}`);
                    return response.text();
                })
                .then((html) => this.addFromHtml(html))
                .catch((error) => console.error('Error uploading file:', error))
                .finally(() => this.setAddingEnd());
        }
    }
}
