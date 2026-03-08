import { xprezExecuteScripts, xprezGetCsrfToken } from './utils.js';
import { XprezClipboardList } from './clipboard.js';
import { XprezControllerBase } from './controller_base.js';

export class XprezAdderBase extends XprezControllerBase {
    constructor(parent, el) {
        super(parent, el);
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
        this.el.querySelectorAll("[data-xprez-add-item]").forEach(
            itemEl => itemEl.addEventListener("click", () => this.add(itemEl.dataset.url))
        );
    }

    processNewElement(newEl) {
        super.processNewElement(newEl);
        this.xprez.setPlacementToInputs();
    }
}

export class XprezDuplicateAdder extends XprezAdderItemsBase {
    bindEvents() {
        this.el.addEventListener('click', (e) => {
            e.stopPropagation();
            this.parent.el.removeAttribute('data-open');
            this.add(this.el.dataset.url);
        });
    }

    placeNewElement(el) { this.parent.parent.el.insertAdjacentElement('afterend', el); }
}

export class XprezSectionDuplicateAdder extends XprezDuplicateAdder {
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezModuleDuplicateAdder extends XprezDuplicateAdder {
    initNewElement(el) { this.parent.parent.section.initModule(el); }
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
    constructor(parent, el) {
        super(parent, el);
        this.clipboardList = this.mountChild(
            this.el.querySelector('[data-controller="XprezClipboardList"]')
        );
    }
}

export class XprezSectionAdderContainerEnd extends XprezContentAdderBase {
    placeNewElement(el) { this.xprez.sectionsContainerEl.appendChild(el); }
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezContentAdderSectionBase extends XprezContentAdderBase {
    constructor(parent, el) {
        super(parent, el);
        this.section = this.parent;
        this.setTriggerEl();
        if (this.triggerEl) {
            this.triggerEl.addEventListener("click", this.toggle.bind(this));
        }
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
        this.triggerEl = this.section.el.querySelector("[data-xprez-adder-section-before-trigger]");
    }
    placeNewElement(el) { this.section.el.before(el); }
    initNewElement(el) { this.xprez.initSection(el); }
}

export class XprezModuleAdderSectionEnd extends XprezContentAdderSectionBase {
    setTriggerEl() {
        this.triggerEl = this.section.el.querySelector("[data-xprez-adder-section-end-trigger]");
    }
    placeNewElement(el) { this.section.gridEl.appendChild(el); }
    initNewElement(el) { this.section.initModule(el); }
}

export class XprezConfigAdderBase extends XprezAdderSelectBase {
    constructor(parent, el) {
        super(parent, el);
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

export class XprezSectionConfigAdder extends XprezConfigAdderBase {}

export class XprezModuleConfigAdder extends XprezConfigAdderBase {}

export class XprezMultiModuleAdderBase extends XprezAdderBase {
    constructor(parent, el) {
        super(parent, el);
        this.module = this.parent;
    }

    placeNewElement(el) {
        this.module.itemsContainer.appendChild(el);
        this.module.setItemPositionsToInputs();
    }
    initNewElement(el) { this.module.initItem(el); }
}

export class XprezMultiModuleAdder extends XprezMultiModuleAdderBase {
    bindEvents() {
        this.el.querySelectorAll("[data-xprez-add-item]").forEach(
            itemEl => itemEl.addEventListener('click', () => this.add(itemEl.dataset.url))
        );
    }
}

export class XprezUploadMultiModuleAdder extends XprezMultiModuleAdderBase {
    bindEvents() {
        const dropzone = this.el.querySelector("[data-xprez-multi-module-dropzone]");
        if (!dropzone) return;

        const fileInput = dropzone.querySelector("[data-xprez-multi-module-file-input]");
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
