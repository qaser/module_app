import Popup from './Popup.js';

export default class PopupWithImages extends Popup {
    constructor(popupSelector) {
        super(popupSelector);
        this._container = this._popup.querySelector('.images');
        this._panel = this._container.querySelector('.images__panel');
        this._switch = this._container.querySelector('.images__switch');
        this._imageTitle = this._container.querySelector('.images__title');
        this._imageElement = '<img src="" alt="" class="images__item">';
        this._videoElement = '<video src="" class="images__item">';
        this._videoDisplay = '<video src="" class="images__display" controls>';
        this._imageDisplay = '<img src="" alt="" class="images__display">';
    }

    _insertImagesInPanel(files) {
        this._panel.innerHTML = '';
        files.forEach((file) => {
            if (file.file_type == 'video') {
                this._panel.insertAdjacentHTML('afterbegin', this._videoElement);
                let img = this._panel.querySelector('.images__item');
                img.src = file.file;
                img.addEventListener('click', () => {
                    this._setDisplay(file);
                })
            }
            else {
                this._panel.insertAdjacentHTML('afterbegin', this._imageElement);
                let img = this._panel.querySelector('.images__item');
                img.src = file.file;
                img.alt = file.name;
                img.addEventListener('click', () => {
                    this._setDisplay(file);
                })
            }
        })
    }

    _setDisplay(file) {
        this._switch.innerHTML = '';
        if (file.file_type == 'video') {
            this._switch.insertAdjacentHTML('afterbegin', this._videoDisplay);
            let video =  this._switch.querySelector('.images__display');
            video.src = file.file;
            this._imageTitle.textContent = file.name;
        }
        else {
            this._switch.insertAdjacentHTML('afterbegin', this._imageDisplay);
            let img =  this._switch.querySelector('.images__display');
            img.src = file.file;
            img.alt = file.name;
            this._imageTitle.textContent = file.name;
        }
    }

    open(files) {
        this._setDisplay(files[0])
        this._insertImagesInPanel(files);
        super.open();
    }
}
