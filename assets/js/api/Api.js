export default class Api {
    constructor(options) {
        this._baseUrl = options.baseUrl;
        this._headers = options.headers;
    }

    // Получение годовых корневых планов
    getAnnualPlans() {
        return fetch(`${this._baseUrl}/rational-plans/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // получение годового плана с дочерними годовыми планами
    getPlanWithChildren(planId) {
        return fetch(`${this._baseUrl}/rational-plans/${planId}/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // Получение квартальных планов для годового плана
    getQuarterlyPlans(annualPlanId) {
        return fetch(`${this._baseUrl}/plans/quarterly/${annualPlanId}/`, {
            headers: this._headers,
        })
        .then(response => response.json());
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
        return fetch(`${this._baseUrl}/leaks/${id}/`, {
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

    // Получение дочерних объектов оборудования
    getDepartmentChildren(parentId) {
        return fetch(`${this._baseUrl}/department-search/?parent_id=${parentId}`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // Получение дочерних объектов оборудования
    getEquipmentChildren(parentId, structureEnable) {
        return fetch(`${this._baseUrl}/equipment-search/?parent_id=${parentId}&filter_structure=${structureEnable}`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // загрузка РП с сервера
    getProposals() {
        return fetch(`${this._baseUrl}/rational/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // загрузка одного РП с сервера
    getProposalItem(id) {
        return fetch(`${this._baseUrl}/rational/${id}`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    // добавление нового РП
    addNewProposal(proposal) {
        return fetch(`${this._baseUrl}/rational/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify({
                name: proposal.name,
                link: proposal.link
            })
        })
        .then(this._checkResponse);
    }

    // удаление РП
    deleteProposal(id) {
        return fetch(`${this._baseUrl}/rational/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        .then(this._checkResponse);
    }

    // изменить РП
    changeProposal(form, id) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/rational/${id}/`, {
            method: 'PATCH',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }


    // добавление нового файла РП
    addProposalFile(form) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/rational-docs/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    // удаление файла РП
    deleteProposalFile(id) {
        return fetch(`${this._baseUrl}/rational-docs/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        // .then(this._checkResponse);
    }

    // добавление нового РП
    addNewStatus(form) {
        return fetch(`${this._baseUrl}/statuses/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(this._checkResponse);
    }

    getPipelines() {
        return fetch(`${this._baseUrl}/pipelines/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    changePipeState(stateData) {
        return fetch(`${this._baseUrl}/pipe-states/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify({stateData})
        })
        .then(this._checkResponse);
    }

    changeNodeState(stateData) {
        return fetch(`${this._baseUrl}/node-states/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify({stateData})
        })
        .then(this._checkResponse);
    }

    getPipeItem(id) {
        return fetch(`${this._baseUrl}/pipes/${id}/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    getNodeDetails(nodeId) {
        return fetch(`${this._baseUrl}/nodes/${nodeId}/`, {
            headers: this._headers,
        })
        .then(this._checkResponse);
    }

    getNotifications(url) {
        return fetch(this._baseUrl + url, {
            headers: this._headers,
            credentials: 'include'
        })
        .then(response => response.json());
    }

    postNotification(url, body) {
        return fetch(this._baseUrl + url, {
            method: 'POST',
            headers: this._headers,
            credentials: 'include',
            body: JSON.stringify(body)
        })
        .then(this._checkResponse);
    }


    // добавление новой файла pipe
    addPipeFile(form) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/pipe-docs/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    // удаление файла pipe
    deletePipeFile(id) {
        return fetch(`${this._baseUrl}/pipe-docs/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        // .then(this._checkResponse);
    }

    getTubes(pipe_id) {
        return fetch(`${this._baseUrl}/pipes/${pipe_id}/tubes/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }
    // _checkResponse(res) {
    //     if (res.ok) {
    //         return res.json();
    //     }
    //     return Promise.reject(`Ошибка ${res.status}`);
    // }
}
