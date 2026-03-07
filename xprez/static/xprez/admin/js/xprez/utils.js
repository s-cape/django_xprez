export function xprezGetCsrfToken() {
    const cookie = document.cookie
        .split(";")
        .map((c) => c.trim())
        .find((c) => c.startsWith("csrftoken="));
    return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}

export function xprezExecuteScripts(el) {
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

export function setFilePreviewImage(imgEl, file) {
    if (imgEl.dataset.previewObjectUrl) {
        URL.revokeObjectURL(imgEl.dataset.previewObjectUrl);
    }
    const url = URL.createObjectURL(file);
    imgEl.dataset.previewObjectUrl = url;
    imgEl.src = url;
}

export function clearFilePreviewImage(imgEl) {
    if (imgEl.dataset.previewObjectUrl) {
        URL.revokeObjectURL(imgEl.dataset.previewObjectUrl);
        delete imgEl.dataset.previewObjectUrl;
    }
    imgEl.removeAttribute("src");
}
