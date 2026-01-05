export default class DiagnosticItem {
    constructor(data) {
        this._card = document.querySelector(data.card);
        this._title = this._card.querySelector('.main__title');
        this._values = this._card.querySelectorAll('.card__value');
        this._tube_count = document.getElementById('tube_count');
        this._unit_count = document.getElementById('unit_count');
        this._bend_count = document.getElementById('bend_count');
        this._anomaly_count = document.getElementById('anomaly_count');
        this._defects_count = document.getElementById('defects_count');
        this._tubes_link_btn = document.getElementById('tubes_link_btn');
        this._tube_units_link_btn = document.getElementById('tube_units_link_btn');
        this._bends_link_btn = document.getElementById('bends_link_btn');
        this._anomaly_link_btn = document.getElementById('anomaly_link_btn');
        this._defects_link_btn = document.getElementById('defects_link_btn');
    }

    renderItem(diagnostic) {
        document.getElementById('diagnostic_num').textContent = ` МГ "${diagnostic.pipeline}" ${diagnostic.length}`;
        this._values.forEach(el => {
            if (el.id === 'start_date' || el.id === 'end_date') {
                if (diagnostic[el.id]) {
                    const [y, m, d] = diagnostic[el.id].split('-');
                    el.textContent = `${d}.${m}.${y} г.`;
                } else {
                    el.textContent = '-';
                }
            } else {
                const value = diagnostic[el.id];
                el.textContent = value ?? '-';
            }
        });
        this._tube_count.textContent = diagnostic.tube_count;
        this._unit_count.textContent = diagnostic.unit_count;
        this._bend_count.textContent = diagnostic.bend_count;
        this._anomaly_count.textContent = diagnostic.anomaly_count;
        this._defects_count.textContent = diagnostic.defects_count;
        this._tubes_link_btn.onclick = () => {
            window.location.href = `tubes/`;
        };
        this._tube_units_link_btn.onclick = () => {
            window.location.href = `tube-units/`;
        };
        this._bends_link_btn.onclick = () => {
            window.location.href = `bends/`;
        };
        this._anomaly_link_btn.onclick = () => {
            window.location.href = `anomalies/`;
        };
        this._defects_link_btn.onclick = () => {
            window.location.href = `defects/`;
        };
    }
}
