export default class Table {
    constructor(data) {
        this._table = document.querySelector(data.table);
    }

    _getArrayRows() {
        this._rows = this._table.children
        this._arrayRows = Array.from(this._rows);
        return this._arrayRows;
    }

    init() {
        this._arrRows = this._getArrayRows()
        this._arrRows.forEach((row) => {
            row.addEventListener('click', () => {
                document.location.href = row.id + '/'
            })
        })
    }
}
