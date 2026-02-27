import { XprezFieldController } from './fields.js';
import { setFilePreviewImage, clearFilePreviewImage } from './utils.js';

export class XprezFileInputFieldController extends XprezFieldController {
    constructor(parent, fieldEl) {
        super(parent, fieldEl);
        this.containerEl = fieldEl.querySelector("[data-component='xprez-file-input']");
        if (!this.containerEl) return;

        this.imgEl = this.containerEl.querySelector("[data-component='xprez-file-input-img']");
        this.filenameEl = this.containerEl.querySelector("[data-component='xprez-file-input-filename']");
        this.addBtnEl = fieldEl.querySelector("[data-component='xprez-file-input-add-btn']");
        this.replaceBtnEl = this.containerEl.querySelector(
            "[data-component='xprez-file-input-replace-btn']"
        );
        this.deleteTriggerEl = this.containerEl.querySelector(
            "[data-component='xprez-file-input-delete-trigger']"
        );
        this.clearInputEl = this.deleteTriggerEl
            ? this.deleteTriggerEl.querySelector("input[type='checkbox']")
            : null;
        this.undeleteEl = this.containerEl.querySelector(
            "[data-component='xprez-file-input-undelete']"
        );

        // On load with a saved file the input is already inside replaceBtnEl (from template).
        // On load with no file the input is inside addBtnEl (from template).

        if (this.deleteTriggerEl) {
            this.deleteTriggerEl.addEventListener("click", () => this.delete());
        }
        if (this.undeleteEl) {
            this.undeleteEl.addEventListener("click", () => this.undelete());
        }
    }

    _onInputChange() {
        super._onInputChange();
        const file = this.inputEl.files[0];
        if (file) this._setPreview(file);
    }

    _setPreview(file) {
        if (this.filenameEl) {
            this.filenameEl.textContent = file.name;
        }
        if (file.type.startsWith("image/")) {
            setFilePreviewImage(this.imgEl, file);
            if (this.imgEl) {
                this.imgEl.removeAttribute("data-hidden");
            }
            if (this.filenameEl) {
                this.filenameEl.setAttribute("data-hidden", "");
            }
        } else {
            clearFilePreviewImage(this.imgEl);
            if (this.imgEl) {
                this.imgEl.setAttribute("data-hidden", "");
            }
            if (this.filenameEl) {
                this.filenameEl.removeAttribute("data-hidden");
            }
        }
        this.replaceBtnEl.append(this.inputEl);
        this.containerEl.removeAttribute("data-hidden");
        this.addBtnEl.setAttribute("data-hidden", "");
    }

    _clearPreview() {
        this.inputEl.value = "";
        this._previousValue = "";
        clearFilePreviewImage(this.imgEl);
        this.imgEl.removeAttribute("data-hidden");
        this.filenameEl.setAttribute("data-hidden", "");
        this.addBtnEl.append(this.inputEl);
        this.containerEl.setAttribute("data-hidden", "");
        this.addBtnEl.removeAttribute("data-hidden");
    }

    delete() {
        if ("hasSavedFile" in this.containerEl.dataset) {
            this.containerEl.dataset.mode = "delete";
            if (this.clearInputEl) {
                this.clearInputEl.checked = true;
            }
        } else {
            this._clearPreview();
        }
    }

    undelete() {
        this.containerEl.dataset.mode = "";
        if (this.clearInputEl) {
            this.clearInputEl.checked = false;
        }
    }
}
