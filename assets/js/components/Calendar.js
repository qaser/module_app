export default class Calendar {
    constructor(selector, handleServiceClick, handleEmptyServiceClick) {
        this._calendar = document.querySelector(selector);
        this._handleServiceClick = handleServiceClick;
        this._handleEmptyServiceClick = handleEmptyServiceClick;
    }

    _getArrayServices() {
        this._services = this._calendar.querySelectorAll('[id]');
        this._arr = Array.from(this._services);
        return this._arr;
    }

    // функция определения id нажатого ТО (может быть несколько id)
    _getServiceIds(item) {
        const idsRaw = item.id;
        return idsRaw.split('|');
    }

    _setEventListeners() {
        this._arrServices = this._getArrayServices();
        this._arrServices.forEach((item) => {
            if (item.id !== 'empty') {
                item.addEventListener('click', () => {
                    const ids = this._getServiceIds(item);
                    this._handleServiceClick(ids);
                })
            }
            else {
                item.addEventListener('click', (evt) => {
                    this._handleEmptyServiceClick(evt);
                })
            }
        });
    }

    // генерация ссылок
    generateLinks() {
        this._setEventListeners();
    }
}
