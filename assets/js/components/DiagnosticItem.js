export default class DiagnosticItem {
    constructor(data) {
        this._card = document.querySelector(data.card);
        this._title = this._card.querySelector('.main__title');
        this._values = this._card.querySelectorAll('.card__value');
    }

    renderItem(diagnostic) {
        document.getElementById('diagnostic_num').textContent = `${diagnostic}`;
        this._values.forEach(el => {
            const value = diagnostic[el.id];
            el.textContent = value ?? '-';
        });
    }

}
