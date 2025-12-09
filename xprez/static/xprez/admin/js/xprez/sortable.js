export class XprezSortable {
    constructor(element, config = {}) {
        this.element = element;
        this.config = config;
        this.dropPrevention = {
            selector: 'input, textarea, select, [contenteditable], [class*="ck-"]',
            events: ['dragenter', 'dragover', 'drop'],
            handler: this.preventNativeDrop.bind(this)
        };

        this.sortable = this.createSortable();
    }

    preventNativeDrop(e) {
        const { selector } = this.dropPrevention;
        if (e.target.matches(selector) || e.target.closest(selector)) {
            e.preventDefault();
            e.stopPropagation();
        }
    }

    enableDropPrevention() {
        this.dropPrevention.events.forEach(event => {
            document.addEventListener(event, this.dropPrevention.handler, true);
        });
    }

    disableDropPrevention() {
        this.dropPrevention.events.forEach(event => {
            document.removeEventListener(event, this.dropPrevention.handler, true);
        });
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

