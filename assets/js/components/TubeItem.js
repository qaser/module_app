export default class TubeItem {
    constructor(data) {
        this._card = document.querySelector(data.card);
        this._title = this._card.querySelector('.main__title');
        this._values = this._card.querySelectorAll('.card__value');
        this._tube_units_info = document.getElementById('tube_units_info');
        this._versions_info = document.getElementById('versions_info');
    }

    _renderTubeUnits(units) {
        this._tube_units_info.innerHTML = units.map(u => `
            <div class="card__line">
                <p class="card__param">${u.unit_type_display}</p>
                <p class="card__value">${u.comment || u.description || '-'}</p>
            </div>
        `).join('');
    }

    // _renderVersions(versions) {
    //     this._versions_info.innerHTML = versions.map(v => `
    //         <div class="card__block">
    //             <p class="card__param">${v.version_type_display} от ${v.date}</p>
    //             <div class="card__line"><p class="card__param">Длина</p><p class="card__value">${v.tube_length} м</p></div>
    //             <div class="card__line"><p class="card__param">Толщина</p><p class="card__value">${v.thickness} мм</p></div>
    //             <div class="card__line"><p class="card__param">Тип</p><p class="card__value">${v.tube_type}</p></div>
    //         </div>
    //     `).join('');
    // }

    renderItem(tube) {
        document.getElementById('tube_num').textContent = `${tube.tube_num} участка ${tube.pipe_name}`;
        this._values.forEach(el => {
            const value = tube[el.id];
            el.textContent = value ?? '-';
        });

        // Источник данных: dd.mm.yyyy
        const sourceEl = document.getElementById('version_type_display');
        if (sourceEl && tube.date) {
            const [y, m, d] = tube.date.split('-');
            sourceEl.textContent = `${tube.version_type_display} от ${d}.${m}.${y}г.`;
        }

        if (tube.tube_units?.length) {
            this._renderTubeUnits(tube.tube_units);
        } else {
            this._tube_units_info.innerHTML = '<div class="card__line"><p class="card__param">Отсутствуют</p>';
        }

        // if (tube.versions?.length > 1) {
        //     this._renderVersions(tube.versions);
        // } else {
        //     this._versions_info.innerHTML = '<p class="card__value">Только текущая версия</p>';
        // }
    }

}
