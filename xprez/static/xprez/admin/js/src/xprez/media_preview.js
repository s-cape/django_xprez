export const WithMediaPreview = (Base) => class extends Base {
    static _setPreviewSrc(el, file) {
        if (el.dataset.previewObjectUrl) {
            URL.revokeObjectURL(el.dataset.previewObjectUrl);
        }
        const url = URL.createObjectURL(file);
        el.dataset.previewObjectUrl = url;
        el.src = url;
        if (el.tagName === "VIDEO") { el.load(); }
    }

    static _clearPreviewSrc(el) {
        if (el.dataset.previewObjectUrl) {
            URL.revokeObjectURL(el.dataset.previewObjectUrl);
            delete el.dataset.previewObjectUrl;
        }
        el.removeAttribute("src");
        if (el.tagName === "VIDEO") { el.load(); }
    }

    _initMediaPreviewEls(containerEl) {
        this.mediaPreviewEls = [...containerEl.querySelectorAll("[data-media-preview]")];
        this.mediaPreviewFallbackEl = containerEl.querySelector("[data-media-preview='fallback']");
    }

    _applyMediaPreview(file) {
        let matched = false;
        this.mediaPreviewEls.forEach((el) => {
            if (el.dataset.mediaPreview === "fallback") {
                return;
            }
            if (file.type.startsWith(el.dataset.mediaPreview + "/")) {
                this.constructor._setPreviewSrc(el, file);
                el.removeAttribute("data-hidden");
                matched = true;
            } else {
                this.constructor._clearPreviewSrc(el);
                el.setAttribute("data-hidden", "");
            }
        });
        if (this.mediaPreviewFallbackEl) {
            if (matched) {
                this.mediaPreviewFallbackEl.setAttribute("data-hidden", "");
            } else {
                this.mediaPreviewFallbackEl.removeAttribute("data-hidden");
            }
        }
        return matched;
    }

    _clearMediaPreview() {
        this.mediaPreviewEls.forEach((el) => {
            if (el.dataset.mediaPreview === "fallback") {
                el.setAttribute("data-hidden", "");
            } else {
                this.constructor._clearPreviewSrc(el);
                el.removeAttribute("data-hidden");
            }
        });
    }
};
