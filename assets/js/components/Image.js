export default class Image {
    constructor(image, imageSelector, handleImageClick, handleImageDeleteClick) {
        this._image = image;
        this._imageSelector = imageSelector;
        this._handleImageClick = handleImageClick;
        this._handleImageDeleteClick = handleImageDeleteClick;
    }

    _getTemplate() {
        const imageElement = document
            .querySelector(this._imageSelector)
            .content
            .querySelector('.card__image-container')
            .cloneNode(true);
        return imageElement;
    }


    _setEventListeners() {
        const image = this._elementImage;
        image.addEventListener('click', (evt) => {
            evt.stopPropagation();
            this._handleImageClick(this._image.name, this._image.image);
        });
        this._element.addEventListener('click', (evt) => {
            this._handleImageDeleteClick(evt, image.parentElement.id);
        });
    }

    renderImage() {
        this._element = this._getTemplate();
        this._element.id = `image-${this._image.id}`;
        this._elementImage = this._element.querySelector('.card__image');
        // this._elementBasket = this._element.querySelector('.card__basket');
        this._elementImage.src = this._image.image;
        this._elementImage.alt = this._image.name;
        this._setEventListeners();
        return this._element;
    }
}
