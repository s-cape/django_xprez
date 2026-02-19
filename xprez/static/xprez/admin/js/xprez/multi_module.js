import { XprezModule } from './modules.js';
import { XprezSortable } from './sortable.js';
import { XprezMultiModuleItemDeleter } from './deleters.js';
import { executeScripts, getCsrfToken } from './utils.js';

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
}

export class XprezMultiModule extends XprezMultiModuleBase {
    constructor(section, moduleEl) {
        super(section, moduleEl);
        this.initAddButton();
    }

    initAddButton() {
        const adder = this.el.querySelector("[data-component='xprez-multi-module-add']");
        if (!adder) return;

        const url = adder.dataset.addUrl;
        const button = adder.querySelector('button');
        if (!button || !url) return;

        button.addEventListener('click', () => {
            fetch(url)
                .then(response => {
                    if (!response.ok) throw new Error(`Server error ${response.status}`);
                    return response.text();
                })
                .then(html => {
                    const temp = document.createElement('div');
                    temp.innerHTML = html;
                    while (temp.firstElementChild) {
                        const newEl = temp.firstElementChild;
                        this.itemsContainer.appendChild(newEl);
                        this.initItem(newEl);
                        executeScripts(newEl);
                    }
                    this.initSortable();
                })
                .catch(error => console.error('Error adding item:', error));
        });
    }
}

export class XprezUploadMultiModule extends XprezMultiModuleBase {
    constructor(section, moduleEl) {
        super(section, moduleEl);
        this.initUpload();
    }

    initUpload() {
        const uploadArea = this.el.querySelector("[data-component='xprez-multi-module-upload']");
        if (!uploadArea) return;

        const fileInput = uploadArea.querySelector("[data-component='xprez-multi-module-file-input']");
        const url = uploadArea.dataset.uploadUrl;
        if (!fileInput || !url) return;

        uploadArea.addEventListener('click', (e) => {
            if (e.target !== fileInput) fileInput.click();
        });

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('xprez-upload-area--dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('xprez-upload-area--dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('xprez-upload-area--dragover');
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

            fetch(url, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
                body: formData,
            })
                .then(response => {
                    if (!response.ok) throw new Error(`Upload error ${response.status}`);
                    return response.text();
                })
                .then(html => {
                    const temp = document.createElement('div');
                    temp.innerHTML = html;
                    while (temp.firstElementChild) {
                        const newEl = temp.firstElementChild;
                        this.itemsContainer.appendChild(newEl);
                        this.initItem(newEl);
                        executeScripts(newEl);
                    }
                    this.initSortable();
                })
                .catch(error => console.error('Error uploading file:', error));
        }
    }
}
