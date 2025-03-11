export default class PermissionChecker {
    constructor(currentUser, object, elementSelector, appSelector) {
        this._currentUser = currentUser;
        this._object = object;
        this._elementSelector = elementSelector;
        this._appSelector = appSelector;
        this.init();
    }

    init() {
        const hasEditPermission = this._checkEditPermission();
        const isStatusRestricted = this._checkStatusRestriction();
        const shouldShowElement = (hasEditPermission.isAuthor && !isStatusRestricted) || hasEditPermission.hasAppAccess;
        this._toggleDomElement(shouldShowElement);
    }

    _checkEditPermission() {
        const authors = Array.isArray(this._object.authors) ? this._object.authors : [this._object.authors];
        const isAuthor = authors.some(author => author.id === this._currentUser.id);
        const currentApp = document.querySelector(this._appSelector).getAttribute('app-name');
        const hasAppAccess = this._currentUser.apps.includes(currentApp);
        return { isAuthor, hasAppAccess };
    }

    _checkStatusRestriction() {
        if (!this._object.statuses || !Array.isArray(this._object.statuses)) {
            return false;
        }

        const restrictedStatuses = ['apply', 'accept', 'reject', 'recheck'];
        return this._object.statuses.some(status => {
            return status.current_status && restrictedStatuses.includes(status.current_status.status.code);
        });
    }

    _toggleDomElement(shouldShowElement) {
        const domElement = document.querySelector(this._elementSelector);
        if (domElement) {
            if (shouldShowElement) {
                domElement.classList.remove('hidden');
            } else {
                domElement.classList.add('hidden');
            }
        }
    }
}
