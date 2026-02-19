export function getCsrfToken() {
    const cookie = document.cookie
        .split(";")
        .map((c) => c.trim())
        .find((c) => c.startsWith("csrftoken="));
    return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}

export function executeScripts(el) {
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
