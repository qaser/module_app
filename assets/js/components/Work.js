export default class Work {
    constructor(work, workSelector, handleWorkClick, handlePhotoGalleryClick) {
        this._work = work;
        this._id = work.id;
        this._description = work.work.description;
        this._done = work.done;
        this._faults = work.faults;
        this._files = work.files;
        this._workSelector = workSelector;
        this._handleWorkClick = handleWorkClick;
        this._handlePhotoGalleryClick = handlePhotoGalleryClick;
    }

    _getTemplate() {
        const template = document
            .querySelector(this._workSelector)
            .content
            .querySelector('.report__work')
            .cloneNode(true);
        return template;
    }

    _representDone(ans) {
        if (String(ans) === 'true') {
            return 'Выполнено';
        }
        return 'Не выполнено';
    }

    _checkFilesAvailable() {
        if (this._files.length > 0) {
            this._layoutFiles.classList.add('report__photo_active')
        }
    }

    _representDescription(string) {
        return string[0].toUpperCase() + string.slice(1);
    }

    _setEventListeners() {
        const icon = this._layout.querySelector('.report__photo');
        icon.addEventListener('click', (evt) => {
            evt.stopPropagation();
            this._handlePhotoGalleryClick(this._files);
        });
        this._layout.addEventListener('click', () => {
            this._handleWorkClick(this._work);
        });
    }

    generateWork() {
        this._layout = this._getTemplate();
        this._layoutDescription = this._layout.querySelector('#description');
        this._layoutDone = this._layout.querySelector('#done');
        this._layoutFaults = this._layout.querySelector('#faults');
        this._layoutFiles = this._layout.querySelector('#files');
        this._layoutDescription.textContent = this._representDescription(this._description);
        this._layoutDone.textContent = this._representDone(this._done);
        this._layoutFaults.textContent = this._faults;
        this._layout.id = 'w' + this._id;
        this._setEventListeners();
        this._checkFilesAvailable();
        return this._layout;
    }
}
