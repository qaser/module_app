export default class Api {
    constructor(options) {
        this._baseUrl = options.baseUrl;
        this._headers = options.headers;
    }

    // загрузка данных пользователя
    getMyProfile() {
        return fetch(`${this._baseUrl}/users/me/`, {
            headers: this._headers,
        })
        .then(response => response.json())
    }

    // редактирование данных пользователя
    editMyProfile(user) {
        return fetch(`${this._baseUrl}/users/me/`, {
            method: 'PATCH',
            headers: this._headers,
            body: JSON.stringify({
                name: user.name,
                job: user.job
            })
        })
        .then(this._checkResponse);
    }

    // загрузка утечек с сервера
    getLeaks() {
        return fetch(`${this._baseUrl}/leaks/`, {
            headers: this._headers,
        })
        .then(this._checkResponse);
    }

    // загрузка одной утечки с сервера
    getLeakItem(id) {
        return fetch(`${this._baseUrl}/leaks/${id}`, {
            headers: this._headers,
        })
        .then(response => response.json())
    }

    // добавление новой утечки
    addNewLeak(valve) {
        return fetch(`${this._baseUrl}/leaks/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify({
                name: leak.name,
                link: leak.link
            })
        })
        .then(this._checkResponse);
    }

    // удаление утечки
    deleteLeak(id) {
        return fetch(`${this._baseUrl}/leaks/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        .then(this._checkResponse);
    }

    // изменить утечку
    changeLeak(link) {
        return fetch(`${this._baseUrl}/leaks/${id}/`, {
            method: 'PATCH',
            headers: this._headers,
            body: JSON.stringify({
                body: form
            })
        })
        .then(this._checkResponse);
    }

    // загрузка ТПА с сервера
    getValves() {
        return fetch(`${this._baseUrl}/valves/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // загрузка одного ТПА с сервера
    getValveItem(id) {
        return fetch(`${this._baseUrl}/valves/${id}`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // добавление новой ТПА
    addNewValve(valve) {
        return fetch(`${this._baseUrl}/valves/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify({
                name: valve.name,
                link: valve.link
            })
        })
        .then(this._checkResponse);
    }

    // удаление ТПА
    deleteValve(id) {
        return fetch(`${this._baseUrl}/valves/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        .then(this._checkResponse);
    }

    // изменить ТПА
    changeValve(form, id) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/valves/${id}/`, {
            method: 'PATCH',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    // добавление новой фотографии ТПА
    addValveImage(form) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/valve-images/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    // удаление фотографии ТПА
    deleteValveImage(id) {
        return fetch(`${this._baseUrl}/valve-images/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        // .then(this._checkResponse);
    }

    // добавление новой файла ТПА
    addValveFile(form) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/valve-docs/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    // удаление файла ТПА
    deleteValveFile(id) {
        return fetch(`${this._baseUrl}/valve-docs/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        // .then(this._checkResponse);
    }

    // загрузка всех ТО с сервера
    getServices() {
        return fetch(`${this._baseUrl}/services/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // загрузка одного ТО с сервера по id
    getServiceItem(id) {
        return fetch(`${this._baseUrl}/services/${id}`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // добавление нового ТО
    addNewService(service) {
        return fetch(`${this._baseUrl}/services/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify({
                name: service.name,
                prod_date: service.prod_date,
                valve: service.valve
            })
        })
        .then(this._checkResponse);
    }

    // удаление ТО
    deleteService(id) {
        return fetch(`${this._baseUrl}/services/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        .then(this._checkResponse);
    }

    // загрузка списка видов ТО с сервера
    getServiceTypes() {
        return fetch(`${this._baseUrl}/service-types/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // загрузка списка производителей с сервера
    getFactories() {
        return fetch(`${this._baseUrl}/factories/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // добавление новой работы
    addNewWork(form) {
        delete this._headers['Content-Type']  // удаляем из заголовка тип контента в запросе
        return fetch(`${this._baseUrl}/works/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(this._checkResponse);
    }

    // _checkResponse(res) {
    //     if (res.ok) {
    //         return res.json();
    //     }
    //     return Promise.reject(`Ошибка ${res.status}`);
    // }
}
