export default class FormHandler {
    constructor(formSelector, inputsCardSelector, inputSelector, submitBtnSelector, submitForm) {
        this._form = document.querySelector(formSelector);
        this._inputsCard = document.querySelector(inputsCardSelector);
        this._submitForm = submitForm;
        this._submitButton = this._form.querySelector(submitBtnSelector);
        this._formInputs = Array.from(this._inputsCard.querySelectorAll(inputSelector));
        this._formValues = {};
    }

    _getInputValues() {
        this._formInputs.forEach((input) => {
            if (input.type == 'file') {
                this._formValues[input.id] = input.files;
            }
            else {
                this._formValues[input.id] = input.value
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
    }
}
