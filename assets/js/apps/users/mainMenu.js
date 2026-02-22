import * as config from '../../config/config.js';
import * as constant from '../../utils/constants.js';
import Api from '../../api/Api.js';
import UserInfo from '../../components/UserInfo.js';
import NotificationManager from '../../components/NotificationManager.js';
import Section from '../../components/Section.js';
import { getApi } from '../../getApi.js';
import { initUser } from '../../userInfo.js';
import { renderLoading } from '../../loadingScreen.js';

// создание объекта api
const api = getApi();

const notificationSection = new Section(
  {
    renderer: (item) => {
      const card = notificationCard(item, handleMarkAsReadClick);
      notificationSection.setItem(card);
    },
  },
  '.notifications-container'
);

function handleMarkAsReadClick(id, element) {
  const button = element.querySelector('.notification-read-btn');
  button.disabled = true;
  button.textContent = '...';

  api
    .markAsRead(id)
    .then(() => {
      element.classList.remove('notification_unread');
      button.textContent = 'Отмечено';
    })
    .catch((err) => {
      console.error('Ошибка при отметке как прочитано:', err);
      button.disabled = false;
      button.textContent = 'Повторить';
    });
}

function notificationCard(item, handleMarkAsReadClick) {
  const notification = new NotificationManager(
    item,
    '.notification-template',
    handleMarkAsReadClick
  );
  return notification.renderNotification();
}

initUser()
  .then(() => {
    // Пользователь загружен, теперь загружаем pipeline
    return api.getNotifications('/notifications/');
  })
  .then((msgs) => {
    notificationSection.clear();
    notificationSection.renderItems(msgs);
  })
  .catch((err) => {
    console.log('Ошибка инициализации:', err);
  })
  .finally(() => renderLoading(true));
