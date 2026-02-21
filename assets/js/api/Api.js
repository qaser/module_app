export default class Api {
    constructor(options) {
        this._baseUrl = options.baseUrl;
        this._headers = options.headers;
    }

    _checkResponse(res) {
        if (!res.ok) {
            return res.json().then(err => {
                console.error('Ошибка API:', err);
                throw new Error(`${res.status} ${res.statusText}: ${JSON.stringify(err)}`);
            }).catch(e => {
                // Если не JSON (например, HTML)
                throw new Error(`${res.status} ${res.statusText}`);
            });
        }
        return res.json();
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


    //----------------------------------------------------------------------//
    // Приложение tpa

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


    //----------------------------------------------------------------------//
    // Приложение Equipment

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


    //----------------------------------------------------------------------//
    // Приложение Rational

    getAnnualPlans() {
        return fetch(`${this._baseUrl}/rational-plans/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    getPlanWithChildren(planId) {
        return fetch(`${this._baseUrl}/rational-plans/${planId}/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    getQuarterlyPlans(annualPlanId) {
        return fetch(`${this._baseUrl}/plans/quarterly/${annualPlanId}/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    getProposals() {
        return fetch(`${this._baseUrl}/rational/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    getProposalItem(id) {
        return fetch(`${this._baseUrl}/rational/${id}`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

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

    deleteProposal(id) {
        return fetch(`${this._baseUrl}/rational/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        .then(this._checkResponse);
    }

    changeProposal(form, id) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/rational/${id}/`, {
            method: 'PATCH',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    addProposalFile(form) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/rational-docs/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    deleteProposalFile(id) {
        return fetch(`${this._baseUrl}/rational-docs/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        // .then(this._checkResponse);
    }

    addNewStatus(form) {
        return fetch(`${this._baseUrl}/statuses/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(this._checkResponse);
    }


    //----------------------------------------------------------------------//
    // Приложение Notifications

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


    //----------------------------------------------------------------------//
    // Приложение Pipelines

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

    editPipeLimit(limitData) {
        return fetch(`${this._baseUrl}/pipe-limits/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify({limitData})
        })
        .then(this._checkResponse);
    }

    endPipeLimit(limitData) {
        return fetch(`${this._baseUrl}/pipe-limits/${limitData.id}/`, {
            method: 'PATCH',
            headers: this._headers,
            body: JSON.stringify({limitData})
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

    addPipeFile(form) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/pipe-docs/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    deletePipeFile(id) {
        return fetch(`${this._baseUrl}/pipe-docs/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        // .then(this._checkResponse);
    }

    addTubeFile(form) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/tube-docs/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    deleteTubeFile(id) {
        return fetch(`${this._baseUrl}/tube-docs/${id}/`, {
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

    getTubeItem(id) {
        return fetch(`${this._baseUrl}/tubes/${id}/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    getDiagnostics() {
        return fetch(`${this._baseUrl}/diagnostics/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    getDiagnosticItem(id) {
        return fetch(`${this._baseUrl}/diagnostics/${id}/`, {
            headers: this._headers,
        })
        .then(response => response.json());
    }

    addDiagnosticFile(form) {
        // delete this._headers['Content-Type']
        return fetch(`${this._baseUrl}/diagnostic-docs/`, {
            method: 'POST',
            headers: this._headers,
            body: form
        })
        .then(response => response.json());
    }

    deleteDiagnosticFile(id) {
        return fetch(`${this._baseUrl}/diagnostic-docs/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
        // .then(this._checkResponse);
    }


    //---------------------------------------------------//
    // Приложение Plans

    createDoc(data) {
        return fetch(`${this._baseUrl}/plans/docs/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify(data),
        }).then(this._checkResponse);
    }

    deleteDoc(id) {
        return fetch(`${this._baseUrl}/plans/docs/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
    }

    createEvent(data) {
        return fetch(`${this._baseUrl}/plans/events/`, {
            method: 'POST',
            headers: this._headers,
            body: JSON.stringify(data),
        }).then(this._checkResponse);
    }

    changeEvent(id) {
        return fetch(`${this._baseUrl}/plans/instances/${id}/`, {
            method: 'DELETE',
            headers: this._headers,
        })
    }

    markEvent(id, data) {
        return fetch(`${this._baseUrl}/plans/instances/${id}/mark/`, {
            method: 'PATCH',
            headers: this._headers,
            body: JSON.stringify(data),
        }).then(this._checkResponse);
    }

    completeEvent(id) {
        return fetch(`${this._baseUrl}/plans/instances/${id}/complete/`, {
            method: 'PATCH',
            headers: this._headers,
            // body: JSON.stringify(data),
        })
    }
}
