export default class Section {
    constructor({renderer}, containerSelector) {
        this._renderer = renderer;
        this._container = document.querySelector(containerSelector);
    }

    setItem(element) {
        this._container.append(element);
    }

    // метод для добавления нового элемента в начало контейнера
    setItemFront(element) {
        this._container.prepend(element);
    }

    replaceItem(element) {
        console.log(element);
        targetElem = this._container.getElementById(element.id);
        targetElem.replaceWith(element);
    }

    clear() {
        this._container.innerHTML = '';
    }

    renderItems(elements) {
        // this.clear();
        elements.forEach(item => {
            this._renderer(item);
        });
    }
}
