export default class NotificationManager {
    constructor(notification, templateSelector, handleMarkAsReadClick) {
        this._notification = notification;
        this._templateSelector = templateSelector;
        this._handleMarkAsReadClick = handleMarkAsReadClick;
    }

    _getTemplate() {
        const notificationElement = document
            .querySelector(this._templateSelector)
            .content
            .querySelector('.notification-item')
            .cloneNode(true);
        return notificationElement;
    }

    _setEventListeners() {
        this._markAsReadButton.addEventListener('click', () => {
            this._handleMarkAsReadClick(this._notification.id, this._element);
        });
    }

    renderNotification() {
        this._element = this._getTemplate();
        this._element.id = `notification-${this._notification.id}`;

        // Иконка модуля
        const marker = this._element.querySelector('.sidebar__icon');
        if (marker && this._notification.app_name) {
            marker.classList.add(`module-color_${this._notification.app_name}`);
        }

        // Индикатор непрочитанного
        const indicator = this._element.querySelector('.notification-indicator');
        if (!this._notification.is_read) {
            this._element.classList.add('notification_unread');
            if (indicator) {
                indicator.style.display = 'block';
            }
        } else {
            if (indicator) {
                indicator.style.display = 'none';
            }
        }

        // Дата создания
        const createdDate = new Date(this._notification.created_at);
        const dateStr = createdDate.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        this._element.querySelector('.notification-date').textContent = dateStr;

        // Автор
        this._element.querySelector('.notification-meta-user').textContent =
            this._notification.user || 'Система';

        // Текст сообщения
        this._element.querySelector('.notification-message').textContent =
            this._notification.message || '';

        // Ссылка "Открыть"
        const linkElement = this._element.querySelector('.notification-link');
        const linkIcon = this._element.querySelector('.notification-link-icon');
        if (linkElement) {
            linkElement.href = this._notification.url || '#';
        }

        // Кнопка "Прочитано"
        this._markAsReadButton = this._element.querySelector('.notification-read-btn');

        this._setEventListeners();
        return this._element;
    }
}
