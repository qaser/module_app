export default class FileManager {
    constructor(file, fileSelector, handleFileDeleteClick) {
        this._file = file;
        this._fileSelector = fileSelector;
        this._handleFileDeleteClick = handleFileDeleteClick;
    }

    _getTemplate() {
        const fileElement = document
            .querySelector(this._fileSelector)
            .content
            .querySelector('.card__line')
            .cloneNode(true);
        return fileElement;
    }


    _setEventListeners() {
        const file = this._elementUrl;
        this._elementDelete.addEventListener('click', (evt) => {
            this._handleFileDeleteClick(evt, file.parentElement.id);
        });
    }

    renderFile() {
        this._element = this._getTemplate();
        this._element.id = `file-${this._file.id}`;
        this._elementUrl = this._element.querySelector('.card__value_ext');
        this._elementDelete = this._element.querySelector('.card__delete');
        this._elementUrl.href = this._file.doc;
        this._elementUrl.textContent = `${this._file.name} 🔗`;
        this._setEventListeners();
        return this._element;
    }
}
