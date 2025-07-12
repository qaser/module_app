import * as config from './config/config.js';
import * as constant from './utils/constants.js';
import Api from './api/Api.js';
import UserInfo from './components/UserInfo.js';
import NotificationManager from './components/NotificationManager.js';
import Section from '../js/components/Section.js';

// import FormFilter from './components/FormFilter.js';
import Tooltip from '../js/components/Tooltip.js';
import AppMenu from '../js/components/AppMenu.js';

// создание объекта api
const api = new Api({
    baseUrl: config.apiConfig.url,
    headers:{
        'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
        'Content-Type': 'application/json',
        // authorization: constant.apiConfig.token,
    }
});

// создание объекта с данными пользователя
const newUserInfo = new UserInfo({
    name: '.header__username',
    job: '.header__user-proff',
});


const notificationSection = new Section({
    renderer: (item) => {
        const card = notificationCard(item, handleMarkAsReadClick);
        notificationSection.setItem(card);
    }
}, '.notifications-container');


function renderLoading(isLoading) {
  if (isLoading) {
      constant.loadingScreen.classList.add('loader_disactive');
  }
}

function handleMarkAsReadClick(id, element) {
    const button = element.querySelector('.notification-read-btn');
    button.disabled = true;
    button.textContent = '...';

    api.markAsRead(id)
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


new Tooltip();
new AppMenu();


Promise.all([api.getMyProfile(), api.getNotifications('/notifications/')])
    .then(([userData, msgs]) => {
        newUserInfo.setUserInfo(userData);
        notificationSection.clear();
        notificationSection.renderItems(msgs);
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading(true));
