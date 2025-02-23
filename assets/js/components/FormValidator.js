export default class FormValidator {
    constructor(config, formElement) {
        this._formSelector = config.formSelector;
        this._inputSelector = config.inputSelector;
        this._submitButtonSelector = config.submitButtonSelector;
        this._disactiveButtonClass = config.disactiveButtonClass;
        this._inputErrorClass = config.inputErrorClass;
        this._errorClass = config.errorClass;
        this._formElement = formElement;
        this._buttonElement = this._formElement.querySelector(this._submitButtonSelector);
        this._inputList = Array.from(this._formElement.querySelectorAll(config.inputSelector));
    }


    // метод установки слушателя на все инпуты формы
    _setEventListeners() {
        this._toggleButtonState();
        this._inputList.forEach((inputElement) => {
            inputElement.addEventListener('input', () => {
                this._checkInputValidity(inputElement);
                this._toggleButtonState();
            });
        });
    }

    // метод переключения активности кнопки
    _toggleButtonState() {
        if (this._hasInvalidInput()) {
            this._disableButton();
        }
        else {
            this._enableButton();
        }
    }

    // метод проверки валидности всех инпутов
    _hasInvalidInput() {
        return this._inputList.some((inputElement) => {
            return !inputElement.validity.valid;
        });
    }

    // метод для отображения ошибки инпута формы
    _showInputError(inputElement, errorMessage) {
        const errorElement = this._formElement.querySelector(`#${inputElement.id}-error`);
        inputElement.classList.add(this._inputErrorClass);
        errorElement.textContent = errorMessage;
        errorElement.classList.add(this._errorClass);
    }

    // метод для скрытия ошибки инпута формы
    _hideInputError(inputElement) {
        const errorElement = this._formElement.querySelector(`#${inputElement.id}-error`);
        inputElement.classList.remove(this._inputErrorClass);
        errorElement.classList.remove(this._errorClass);
        errorElement.textContent = '';
    }

    // метод проверки валидности поля формы
    _checkInputValidity(inputElement) {
        if (!inputElement.validity.valid) {
            this._showInputError(inputElement, inputElement.validationMessage);
        } else {
            this._hideInputError(inputElement);
        }
    }

    _disableButton() {
        this._buttonElement.classList.add(this._disactiveButtonClass);
        this._buttonElement.disabled = true;
    }

    _enableButton() {
        this._buttonElement.classList.remove(this._disactiveButtonClass);
        this._buttonElement.disabled = false;
    }

    // сброс сообщений валидации и стиля полей
    resetValidation() {
        this._inputList.forEach((input) => {
            this._hideInputError(input);
        })
        this._toggleButtonState();
    }

    enableValidation() {
        this._formElement.addEventListener('submit', (evt) => {
            evt.preventDefault();
        });
        this._setEventListeners();
    }
}
