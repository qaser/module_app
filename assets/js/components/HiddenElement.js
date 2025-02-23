export default class HiddenElement {
    constructor(selector) {
        this._element = this._getElement(selector);
    }

    _getElement(selector) {
        return document.querySelector(selector);
    }

    rawElem() {
        return this._element
    }

    hide() {
        this._element.classList.add('hidden');
    }

    show() {
        this._element.classList.remove('hidden');
    }

    toggle() {
        this._element.classList.toggle('hidden');
    }
}
