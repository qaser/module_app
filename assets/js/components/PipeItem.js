export default class PipeItem {
    constructor(data) {
        this._card = document.querySelector(data.card);
        this._title = this._card.querySelector('.main__title');
        this._values = this._card.querySelectorAll('.card__value');
        this._state = document.getElementById('state_type_display');
        this._limit = document.getElementById('pressure_limit');
        this._repair_start_date = document.getElementById('repair_start_date');
        this._repair_end_date = document.getElementById('repair_end_date');
        this._diagnostics_start_date = document.getElementById('diagnostics_start_date');
        this._diagnostics_end_date = document.getElementById('diagnostics_end_date');
        this._repair_link_btn = document.getElementById('repair_link_btn');
        this._diagnostics_link_btn = document.getElementById('diagnostics_link_btn');
    }

    renderItem(pipe) {
        pipe.start_point = pipe.start_point.toFixed(1);
        pipe.end_point = pipe.end_point.toFixed(1);
        pipe.exploit_year = pipe.exploit_year ? pipe.exploit_year : '-';
        const start_point = pipe.start_point;
        const end_point = pipe.end_point;
        const pipeline = pipe.pipeline;
        pipe.departments = pipe.departments.map(d => d.name).join(' / ');

        this._title.textContent = `Участок ${start_point}-${end_point} км. газопровода "${pipeline}"`;
        this._values.forEach((item) => {
            item.textContent = pipe[item.id];
        });

        if (pipe.state != null) {
            this._state.textContent = pipe.state.state_type_display;
        } else {
            this._state.textContent = 'Неизвестно';
        }

        if (pipe.limit && pipe.limit.pressure_limit != null) {
            this._limit.textContent = `${pipe.limit.pressure_limit} кгс/см²`;
        } else {
            this._limit.textContent = 'Ограничение отсутствует';
        }

        if (pipe.last_repair && pipe.last_repair.start_date) {
            this._repair_start_date.textContent = pipe.last_repair.start_date;
            this._repair_end_date.textContent = pipe.last_repair.end_date || '-';
            this._repair_link_btn.classList.remove('hidden');
            this._repair_link_btn.onclick = () => {
                window.location.href = `/repairs/${pipe.last_repair.id}/`;
            };
        } else {
            this._repair_start_date.textContent = '-';
            this._repair_end_date.textContent = '-';
            this._repair_link_btn.onclick = null;
        }

        if (pipe.last_diagnostics && pipe.last_diagnostics.start_date) {
            this._diagnostics_start_date.textContent = pipe.last_diagnostics.start_date;
            this._diagnostics_end_date.textContent = pipe.last_diagnostics.end_date || '-';
            this._diagnostics_link_btn.classList.remove('hidden');
            this._diagnostics_link_btn.onclick = () => {
                window.location.href = `/diagnostics/${pipe.last_diagnostics.id}/`;
            };
        } else {
            this._diagnostics_start_date.textContent = '-';
            this._diagnostics_end_date.textContent = '-';
            this._diagnostics_link_btn.onclick = null;
        }

    }
}
