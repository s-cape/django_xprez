(function () {
    "use strict";

    function initAccordion(rootEl) {
        rootEl.querySelectorAll("[data-accordion-trigger]").forEach(function (trigger) {
            trigger.addEventListener("click", function () {
                var item = trigger.closest(".xprez-accordion__item");
                var isOpen = item.classList.toggle("is-open");
                trigger.setAttribute("aria-expanded", isOpen ? "true" : "false");
            });
        });
    }

    function init() {
        document.querySelectorAll(".xprez-accordion").forEach(initAccordion);
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
