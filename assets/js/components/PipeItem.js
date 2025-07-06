export default class PipeItem {
    constructor(data) {
        this._card = document.querySelector(data.card);
        this._title = this._card.querySelector('.main__title');
        this._values = this._card.querySelectorAll('.card__value');
        this._service_type = document.getElementById('service_type');
        this._service_date = document.getElementById('prod_date');
    }

    renderItem(pipe) {
        const start_point = pipe.start_point;
        const end_point = pipe.end_point;
        const pipeline = pipe.pipeline;
        // const type = valve.valve_type;
        // const diam = valve.diameter;
        // const pressure = valve.pressure;
        // const num = valve.tech_number;
        this._title.textContent = `Участок ${start_point}-${end_point} км. газопровода "${pipeline}"`;
        this._values.forEach((item) => {
            item.textContent = pipe[item.id];
        });
        // this._service_type.textContent = valve.latest_service.service_type;
        // this._service_date.textContent = valve.latest_service.prod_date;
    }
}
