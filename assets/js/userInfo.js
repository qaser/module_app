import { getApi } from './getApi.js';
import UserInfo from './components/UserInfo.js';

// Создаем Promise для отслеживания загрузки пользователя
let userDataPromise = null;

// Создаем API инстанс
const api = getApi();

// Создаем объект с данными пользователя
const userInfo = new UserInfo({
  name: '.header__username',
  job: '.header__user-proff',
});

function initUser() {
  if (!userDataPromise) {
    userDataPromise = api
      .getMyProfile()
      .then((userData) => {
        userInfo.setUserInfo(userData);
        return userData;
      })
      .catch((error) => {
        console.error('Ошибка загрузки пользователя:', error);
        userDataPromise = null; // Сбрасываем Promise при ошибке
        throw error;
      });
  }
  return userDataPromise;
}

export { initUser };
