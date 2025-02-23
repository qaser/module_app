export default class ServiceItem {
    constructor(data) {
        this._table = document.querySelector(data.table);
    }

    renderItem(services) {
        console.log(services);
    }
}
