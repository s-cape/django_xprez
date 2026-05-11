const PREVENT_NATIVE_DROP_SELECTOR =
    'input, textarea, select, [contenteditable], [class*="ck-"]';

const DRAG_EVENTS = ['dragenter', 'dragover', 'drop'];

export class XprezSortable {
    blockedElements = [];

    constructor(element, config = {}) {
        this.element = element;
        this.config = config;
        this.sortable = this.createSortable();
    }

    preventNativeDrop = (e) => {
        if (
            e.target.matches(PREVENT_NATIVE_DROP_SELECTOR) ||
            e.target.closest(PREVENT_NATIVE_DROP_SELECTOR)
        ) {
            e.preventDefault();
            if (e.dataTransfer) e.dataTransfer.dropEffect = 'none';
        }
    };

    enableDropPrevention() {
        DRAG_EVENTS.forEach((event) =>
            document.addEventListener(event, this.preventNativeDrop, true)
        );
        this.element.querySelectorAll(PREVENT_NATIVE_DROP_SELECTOR).forEach((el) => {
            const savedPointerEvents = el.style.pointerEvents;
            el.style.pointerEvents = 'none';
            this.blockedElements.push({ el, savedPointerEvents });
        });
    }

    disableDropPrevention() {
        DRAG_EVENTS.forEach((event) =>
            document.removeEventListener(event, this.preventNativeDrop, true)
        );
        this.blockedElements.forEach(({ el, savedPointerEvents }) => {
            el.style.pointerEvents = savedPointerEvents;
        });
        this.blockedElements = [];
    }

    createSortable() {
        const { onStart, onEnd, ...rest } = this.config;

        return new Sortable(this.element, {
            animation: 150,
            onStart: (evt) => {
                this.enableDropPrevention();
                if (onStart) onStart(evt);
            },
            onEnd: (evt) => {
                this.disableDropPrevention();
                if (onEnd) onEnd(evt);
            },
            ...rest
        });
    }
}
