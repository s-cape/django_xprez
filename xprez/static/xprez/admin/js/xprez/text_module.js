import { XprezModule } from './modules.js';
import { XprezTextMediaDeleter } from './deleters.js';
import { setFilePreviewImage, clearFilePreviewImage } from './utils.js';

export class XprezTextModule extends XprezModule {
    constructor(section, moduleEl) {
        super(section, moduleEl);
        this.textMediaEl = this.el.querySelector("[data-component='xprez-text-media']");
        this.mediaDeleter = new XprezTextMediaDeleter(this);
        this.initMediaPreview();
    }

    initMediaPreview() {
        const inputName = this.textMediaEl.dataset.mediaInputName;
        this.mediaFileInput = this.el.querySelector(`input[name="${inputName}"]`);
        this.mediaImgEl = this.textMediaEl.querySelector("[data-text-media-img]");
        this.mediaFileInput.addEventListener("change", () => {
            const file = this.mediaFileInput.files[0];
            if (!file) {
                return;
            }
            this._setPreview(file);
        });
    }

    _setPreview(file) {
        setFilePreviewImage(this.mediaImgEl, file);
        this.textMediaEl.removeAttribute("data-hidden");
    }

    _clearPreview() {
        this.mediaFileInput.value = "";
        clearFilePreviewImage(this.mediaImgEl);
    }
}
