import { XprezFieldController } from './fields.js';
import { WithMediaPreview } from './media_preview.js';

export class XprezFileInputFieldController extends WithMediaPreview(XprezFieldController) {
    constructor(parent, fieldEl) {
        super(parent, fieldEl);
        this.containerEl = fieldEl.querySelector("[data-xprez-file-input]");
        if (!this.containerEl) return;

        this._initMediaPreviewEls(this.containerEl);
        this._storeInitialPreview();
        this.addBtnEl = fieldEl.querySelector("[data-xprez-file-input-add-btn]");
        this.replaceBtnEl = this.containerEl.querySelector(
            "[data-xprez-file-input-replace-btn]"
        );
        this.deleteTriggerEl = this.containerEl.querySelector(
            "[data-xprez-file-input-delete-trigger]"
        );
        this.clearInputEl = this.deleteTriggerEl
            ? this.deleteTriggerEl.querySelector("input[type='checkbox']")
            : null;
        this.undeleteEl = this.containerEl.querySelector(
            "[data-xprez-file-input-undelete]"
        );

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
        this._applyMediaPreview(file);
        if (this.mediaPreviewFallbackEl) {
            this.mediaPreviewFallbackEl.textContent = file.name;
        }
        this.containerEl.removeAttribute("data-hidden");
        this.addBtnEl.setAttribute("data-hidden", "");
    }

    _resetToEmpty() {
        this.setValue("");
        this._clearMediaPreview();
        this.containerEl.setAttribute("data-hidden", "");
        this.addBtnEl.removeAttribute("data-hidden");
    }

    _storeInitialPreview() {
        this.mediaPreviewEls.forEach((el) => {
            if (el.dataset.mediaPreview === "fallback") {
                this._initialFallbackText = el.textContent;
                this._initialFallbackHidden = el.hasAttribute("data-hidden");
            } else {
                this._initialImgSrc = el.getAttribute("src");
                this._initialImgHidden = el.hasAttribute("data-hidden");
            }
        });
    }

    _restoreInitialPreview() {
        this.mediaPreviewEls.forEach((el) => {
            if (el.dataset.mediaPreview === "fallback") {
                el.textContent = this._initialFallbackText;
                el.toggleAttribute("data-hidden", this._initialFallbackHidden);
            } else {
                if (this._initialImgSrc !== null) {
                    el.setAttribute("src", this._initialImgSrc);
                } else {
                    el.removeAttribute("src");
                }
                el.toggleAttribute("data-hidden", this._initialImgHidden);
            }
        });
    }

    delete() {
        if ("hasSavedFile" in this.containerEl.dataset) {
            this.setValue("");
            this._restoreInitialPreview();
            this.containerEl.dataset.mode = "delete";
            if (this.clearInputEl) {
                this.clearInputEl.checked = true;
            }
        } else {
            this._resetToEmpty();
        }
    }

    undelete() {
        this.containerEl.dataset.mode = "";
        if (this.clearInputEl) {
            this.clearInputEl.checked = false;
        }
    }
}
