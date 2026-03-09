(function () {
    "use strict";

    class XprezVideoBase {
        hidePoster(poster, delay) {
            setTimeout(
                function () { poster.style.display = "none"; },
                delay || 0
            );
        }
    }

    class XprezVideoYoutube extends XprezVideoBase {
        play(iframe, poster) {
            if (typeof YT !== "undefined" && YT.Player) {
                new YT.Player(iframe, {
                    events: { onReady: function (e) { e.target.playVideo(); } },
                });
                this.hidePoster(poster, 250);
            }
        }
    }

    class XprezVideoVimeo extends XprezVideoBase {
        play(iframe, poster) {
            if (typeof Vimeo !== "undefined" && Vimeo.Player) {
                new Vimeo.Player(iframe).play();
                this.hidePoster(poster);
            }
        }
    }

    window.XprezVideoBase = XprezVideoBase;
    window.XprezVideoYoutube = XprezVideoYoutube;
    window.XprezVideoVimeo = XprezVideoVimeo;

    function onPosterClick(container, poster) {
        const iframe = container.querySelector("[data-js-controller-class]");
        if (!iframe) return;
        const handlerName = iframe.getAttribute("data-js-controller-class");
        const HandlerClass = handlerName && window[handlerName];
        if (typeof HandlerClass === "function") {
            const handler = new HandlerClass();
            handler.play(iframe, poster);
        }
    }

    function init() {
        document.querySelectorAll("[data-video-with-poster]").forEach(function (container) {
            const poster = container.querySelector("[data-video-poster]");
            if (poster) {
                poster.addEventListener("click", function () {
                    onPosterClick(container, poster);
                });
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
