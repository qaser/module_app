export default class StatusManager {
    constructor(statusesData, containerSelector) {
        this.statuses = statusesData.map(status => this._createStatus(status));
        this.container = document.querySelector(containerSelector);
    }

    _createStatus({ id, date_changed, status, owner, note }) {
        return {
            id,
            dateChanged: date_changed,
            status,
            owner: owner ? owner.lastname_and_initials : 'Неизвестно',
            note: note || 'Без примечаний',
            color: this._getStatusColor(status)
        };
    }

    _getStatusColor(status) {
        const colors = {
            'Зарегистрировано': '#E3B778',
            'Повторная заявка': '#7FAF7D',
            'На доработке': '#6D9B9F',
            'Принято': '#5E9D5E',
            'Отклонено': '#C87B7B',
            'Используется': '#8E789B'
        };
        return colors[status] || '#555555';
    }

    _renderStatus(status, index) {
        return `
            <div class="status-card" data-status="${status.status}" style="border-color: ${status.color}">
                <div class="status-stripe" style="background-color: ${status.color}"></div>
                <div class="status-content">
                    <div class="status-header">
                        <strong class="status-name">${status.status}</strong>
                    </div>
                    <div class="status-body">
                        <p class="status-note">${status.note}</p>
                    </div>
                    <div class="status-footer">
                        <span class="status-date">${status.dateChanged}</span>
                        <span class="status-owner">${status.owner}</span>
                    </div>
                </div>
            </div>
        `;
    }

    _addActiveClassToLastCard() {
        const cards = this.container.querySelectorAll('.status-card');
        if (cards.length > 0) {
            const lastCard = cards[cards.length - 1];
            lastCard.classList.add('status-card_active');
        }
    }

    render() {
        if (this.container) {
            this.container.innerHTML = this.statuses.map((status, index) => this._renderStatus(status, index)).join('');
            this._addActiveClassToLastCard();
        }
    }
}
