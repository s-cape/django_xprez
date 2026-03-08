export const WithSignals = (Base) =>
    class extends Base {
        constructor(...args) {
            super(...args);
            this.initSignals();
        }

        initSignals() {
            this._listeners = {};
        }

        on(event, fn) {
            if (!this._listeners[event]) this._listeners[event] = [];
            this._listeners[event].push(fn);
        }

        off(event, fn) {
            if (!this._listeners[event]) return;
            this._listeners[event] = this._listeners[event].filter((f) => f !== fn);
        }

        emit(event) {
            (this._listeners[event] || []).forEach((fn) => fn());
        }
    };
