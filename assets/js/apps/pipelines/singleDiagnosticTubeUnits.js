import * as config from '../../config/config.js';
import * as constant from '../../utils/constants.js';
import Api from '../../api/Api.js';
import UserInfo from '../../components/UserInfo.js';
import Table from '../../components/Table.js';
import FormFilter from '../../components/FormFilter.js';

const pipeId = document.querySelector('.main__title').id;

// создание объекта api
const api = new Api({
  baseUrl: config.apiConfig.url,
  headers: {
    // 'Content-Type': 'application/json',
    'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
  },
});

// создание объекта с данными пользователя
const newUserInfo = new UserInfo({
  name: '.header__username',
  job: '.header__user-proff',
});

// создание объекта таблицы со строками ссылками
const newTable = new Table({ table: '.table__body' });

function renderLoading(isLoading) {
  if (isLoading) {
    constant.loadingScreen.classList.add('loader_disactive');
  }
}

newTable.init();

api
  .getMyProfile()
  .then((userData) => {
    newUserInfo.setUserInfo(userData);
  })
  .catch((err) => {
    console.log(err);
  })
  .finally(() => renderLoading(true));
