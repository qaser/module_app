import * as config from '../../config/config.js';
import * as constant from '../../utils/constants.js';
import Api from '../../api/Api.js';
import UserInfo from '../../components/UserInfo.js';
import Table from '../../components/Table.js';
import FormFilter from '../../components/FormFilter.js';
import Tooltip from '../../components/Tooltip.js';
import AppMenu from '../../components/AppMenu.js';
import PollingClient from '../../api/PollingClient.js';
// import SinglePipeVisualizer from '../js/components/SinglePipeVisualizer.js'


const pipeId = document.querySelector('.main__title').id;

// создание объекта api
const api = new Api({
    baseUrl: config.apiConfig.url,
    headers: {
        // 'Content-Type': 'application/json',
        'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value
    },
});

// создание объекта с данными пользователя
const newUserInfo = new UserInfo({
    name: '.header__username',
    job: '.header__user-proff',
});

// создание объекта таблицы со строками ссылками
const newTable = new Table({table: '.table__body'});

const pollingClient = new PollingClient({
    endpoint: '/api/notifications/unread/'
});


function renderLoading(isLoading) {
  if (isLoading) {
      constant.loadingScreen.classList.add('loader_disactive');
  }
}

new Tooltip();
new AppMenu();
newTable.init();


// Promise.all([api.getMyProfile(), api.getTubes(pipeId)])
//     .then(([userData, tubes]) => {
//         pollingClient.start();
//         newUserInfo.setUserInfo(userData);
//         pipeInstance.renderItem(pipe);
//         const pipeVisualizer = new SinglePipeVisualizer(tubes, "scheme");
//         pipeVisualizer.render();
//     })
//     .catch(err => {
//         console.log(err);
//     })
//     .finally(() => renderLoading(true));


api.getMyProfile()
    .then(userData => {
        pollingClient.start();
        newUserInfo.setUserInfo(userData);
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading(true));
