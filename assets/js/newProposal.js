import * as config from './config/config.js';
import * as constant from './utils/constants.js';
import Api from './api/Api.js';
import UserInfo from './components/UserInfo.js';
import FormFilter from './components/FormFilter.js';
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


function renderLoading(isLoading) {
  if (isLoading) {
      constant.loadingScreen.classList.add('loader_disactive');
  }
}

new Tooltip();
new AppMenu();

api.getMyProfile()
    .then((userData) => {
        newUserInfo.setUserInfo(userData);
        new FormFilter(
            api.getDepartmentChildren.bind(api),
            'filter_submit',
            'id_department',
            'department',
            'form__input',
        );
        const targetField = document.querySelector('#id_department')
        targetField.setAttribute('data-tooltip', constant.tooltipFormField)
    })
    .catch(err => {
        console.log(`Ошибка: ${err}`);
    })
    .finally(() => renderLoading(true));
