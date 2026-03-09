(function () {
    "use strict";

    const DEFAULT_TIME = 3000;
    const DEFAULT_DELAY = 10;

    function formatWithCommas(str) {
        let s = str;
        while (/(\d+)(\d{3})/.test(s)) {
            s = s.replace(/(\d+)(\d{3})/, "$1,$2");
        }
        return s;
    }

    function buildSteps(num, { time, delay, isFloat, decimalPlaces, isComma }) {
        const divisions = time / delay;
        const steps = [];
        for (let i = 1; i <= divisions; i++) {
            let val = (num / divisions) * i;
            if (isFloat) {
                val = parseFloat(val.toFixed(decimalPlaces));
            } else {
                val = parseInt(val, 10);
            }
            let display = String(val);
            if (isComma) display = formatWithCommas(display);
            steps.push(display);
        }
        return steps;
    }

    class NumbersItem {
        constructor(containerEl, options = {}) {
            this.containerEl = containerEl;
            this.counterEl = containerEl.querySelector("[data-numbers-counter]");
            this.time = options.time ?? DEFAULT_TIME;
            this.delay = options.delay ?? DEFAULT_DELAY;
        }

        setMinWidth() {
            const w = this.counterEl.getBoundingClientRect().width;
            this.counterEl.style.minWidth = `${w}px`;
        }

        runCounter() {
            const raw = this.counterEl.textContent;
            const isComma = /[0-9]+,[0-9]+/.test(raw);
            const numStr = raw.replace(/,/g, "");
            const isFloat = /^[0-9]+\.[0-9]+$/.test(numStr);
            const decimalPlaces = isFloat
                ? (numStr.split(".")[1] || []).length
                : 0;
            const num = isFloat ? parseFloat(numStr) : parseInt(numStr, 10);

            const steps = buildSteps(num, {
                time: this.time,
                delay: this.delay,
                isFloat,
                decimalPlaces,
                isComma,
            });

            this.containerEl.classList.add("active");
            this.counterEl.textContent = "0";
            let index = 0;
            const tick = () => {
                if (index < steps.length) {
                    this.counterEl.textContent = steps[index];
                    index += 1;
                    setTimeout(tick, this.delay);
                }
            };
            setTimeout(tick, this.delay);
        }
    }

    class NumbersModule {
        constructor(rootEl, options = {}) {
            this.rootEl = rootEl;
            this.time = options.time ?? DEFAULT_TIME;
            this.delay = options.delay ?? DEFAULT_DELAY;
            this.items = [];
            this.observer = null;
        }

        init() {
            const itemEls = this.rootEl.querySelectorAll("[data-numbers-item]");
            const options = { time: this.time, delay: this.delay };
            this.items = Array.from(itemEls).map(
                (el) => new NumbersItem(el, options)
            );
            this.items.forEach((item) => item.setMinWidth());
            this.observeCounters();
        }

        observeCounters() {
            const counterEls = this.items.map((item) => item.counterEl);
            if (!counterEls.length) return;

            this.observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach((entry) => {
                        if (!entry.isIntersecting) return;
                        this.observer.unobserve(entry.target);
                        const item = this.items.find(
                            (i) => i.counterEl === entry.target
                        );
                        item.runCounter();
                    });
                },
            );
            counterEls.forEach((el) => this.observer.observe(el));
        }
    }

    function init() {
        document.querySelectorAll(".xprez-numbers").forEach((root) => {
            new NumbersModule(root).init();
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
