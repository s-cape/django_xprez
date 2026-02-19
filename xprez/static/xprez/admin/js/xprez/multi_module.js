import { XprezModule } from './modules.js';
import { XprezSortable } from './sortable.js';
import { XprezMultiModuleItemDeleter } from './deleters.js';
import { executeScripts, getCsrfToken } from './utils.js';

export class XprezMultiModuleBase extends XprezModule {
    constructor(section, moduleEl) {
        super(section, moduleEl);
        this.itemsContainer = this.el.querySelector(
            "[data-component='xprez-multi-module-items']"
        );
        if (!this.itemsContainer) return;

        this.initSortable();
        this.initItemDeleters();
    }

    initSortable() {
        const hasHandles = this.itemsContainer.querySelector(
            '.js-item-handle'
        ) !== null;
        this.sortable = new XprezSortable(this.itemsContainer, {
            handle: hasHandles ? '.js-item-handle' : undefined,
            draggable: '.js-item, [data-item-pk]',
        });
    }

    createItemDeleter(itemEl) {
        const trigger = itemEl.querySelector(
            "[data-component='xprez-multi-module-item-delete']"
        );
        const prefix = trigger
            ? trigger.dataset.targetPrefix
            : `item-${itemEl.dataset.itemPk || ''}`;
        return new XprezMultiModuleItemDeleter({ el: itemEl, prefix });
    }

    initItemDeleters() {
        this.itemsContainer
            .querySelectorAll('.js-item, [data-item-pk]')
            .forEach((itemEl) => this.createItemDeleter(itemEl));
    }

    initItemDeleteButtons(itemEl) {
        this.createItemDeleter(itemEl);
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
                        this.initItemDeleteButtons(newEl);
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
                        this.initItemDeleteButtons(newEl);
                        executeScripts(newEl);
                    }
                    this.initSortable();
                })
                .catch(error => console.error('Error uploading file:', error));
        }
    }
}
