import { XprezModule } from './modules.js';
import { XprezTextMediaDeleter } from './deleters.js';
import { WithMediaPreview } from './media_preview.js';

export class XprezTextModule extends WithMediaPreview(XprezModule) {
    constructor(section, moduleEl) {
        super(section, moduleEl);
        this.textMediaEl = this.el.querySelector("[data-xprez-text-media]");
        this.mediaDeleter = new XprezTextMediaDeleter(this);
        this.initMediaPreview();
    }

    initMediaPreview() {
        const inputName = this.textMediaEl.dataset.mediaInputName;
        this.mediaFileInput = this.el.querySelector(`input[name="${inputName}"]`);
        this._initMediaPreviewEls(this.textMediaEl);
        this.mediaFileInput.addEventListener("change", () => {
            const file = this.mediaFileInput.files[0];
            if (!file) {
                return;
            }
            this._applyMediaPreview(file);
            this.textMediaEl.removeAttribute("data-hidden");
        });
    }

}
