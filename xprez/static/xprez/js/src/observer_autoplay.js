(function () {
    "use strict";

    class ObserverAutoplay {
        constructor(el) {
            this.el = el;
        }

        init() {
            this.observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (entry.isIntersecting) {
                            this.el.play();
                        } else {
                            this.el.pause();
                        }
                    });
                },
                { threshold: 0.1 }
            );
            this.observer.observe(this.el);
        }
    }

    function init() {
        document.querySelectorAll("[data-observer-autoplay]").forEach((el) => {
            new ObserverAutoplay(el).init();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
