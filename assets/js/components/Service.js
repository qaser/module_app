export default class Service {
    constructor(service, serviceSelector, handleServiceBasketClick, handleServiceNewWorkClick) {
        this._id = service.id;
        this._title = service.service_type.name;
        this._date = service.prod_date;
        this._serviceSelector = serviceSelector;
        this._handleServiceBasketClick = handleServiceBasketClick;
        this._handleServiceNewWorkClick = handleServiceNewWorkClick;
    }

    _getTemplate() {
        const template = document
            .querySelector(this._serviceSelector)
            .content
            .querySelector('.service__item')
            .cloneNode(true);
        return template;
    }

    _setEventListeners() {
        this._layoutBasket.addEventListener('click', (evt) => {
            this._handleServiceBasketClick(evt, this._id, this._layout);
        });
        this._layoutNewWork.addEventListener('click', () => {
            this._handleServiceNewWorkClick(this._id);
        });
    }

    generateService() {
        this._layout = this._getTemplate();
        this._layoutTitle = this._layout.querySelector('.service__title');
        this._layoutReport = this._layout.querySelector('.report');
        this._layoutReport.id = `report-${this._id}`;
        this._layout.id = 's' + this._id;
        this._layoutTitle.textContent = `${this._title} от ${this._date}г.`;
        this._layoutBasket = this._layout.querySelector('.service__button_basket');
        this._layoutNewWork = this._layout.querySelector('.service__button_add');
        this._setEventListeners();
        return this._layout;
    }
}
