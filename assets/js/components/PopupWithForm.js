import Popup from './Popup.js';

export default class PopupWithForm extends Popup {
    constructor(popupSelector, formSelector, title, submitForm) {
        super(popupSelector);
        this._form = this._popup.querySelector(formSelector);
        this._submitForm = submitForm;
        this._submitButton = this._form.querySelector('.form-popup__button');
        this._formHeader = this._form.querySelector('.form-popup__header');
        this._formHeader.textContent = title;
        this._formInputs = Array.from(this._popup.querySelectorAll('.form-popup__input'));
        this._buttonText = this._submitButton.textContent;
        this._formValues = {};
    }

    renderLoading(isLoading, loadingMessage='Сохранение...') {
        if (isLoading) {
            this._submitButton.textContent = loadingMessage;
        } else {
            this._submitButton.textContent = this._buttonText;
        }
    }

    _getInputValues() {
        this._formInputs.forEach((input) => {
            if (input.type == 'file') {
                this._formValues[input.name] = input.files;
            }
            else {
                this._formValues[input.name] = input.value
            }
        });
        return this._formValues;
    }

    _handleSubmitForm(evt) {
        evt.preventDefault();
        this._submitForm(this._getInputValues());
    }

    setEventListeners() {
        this._form.addEventListener('submit', (evt) => {
            this._handleSubmitForm(evt);
        });
        super.setEventListeners();
    }

    close() {
        this._form.reset();
        super.close();
    }
}
