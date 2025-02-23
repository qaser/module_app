export default class Popup {
  constructor(popupSelector) {
    this._popup = document.querySelector(popupSelector);
    this._closeButton = this._popup.querySelector('.popup__button-close');
    this._handleEscapeClose = this._handleEscapeClose.bind(this);
    this._handleOverlayClose = this._handleOverlayClose.bind(this);
  }

  open() {
    this._popup.classList.add('popup_opened');
    document.addEventListener('keydown', this._handleEscapeClose);
    document.addEventListener('click', this._handleOverlayClose);
  }

  close() {
    this._popup.classList.remove('popup_opened');
    document.removeEventListener('keydown', this._handleEscapeClose);
    document.removeEventListener('click', this._handleOverlayClose);
  }

  _handleEscapeClose(evt) {
    if (evt.key === 'Escape') {
      this.close();
    };
  };

  _handleOverlayClose(evt) {
    if (evt.target === this._popup) {
      this.close();
    };
  };

  setEventListeners() {
    this._closeButton.addEventListener('click', () => {
      this.close();
    });
  }
}
