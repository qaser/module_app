import * as config from './config/config.js';
import * as constant from './utils/constants.js';
import Api from './api/Api.js';
import UserInfo from './components/UserInfo.js';
import FormFilter from './components/FormFilter.js';
import Tooltip from '../js/components/Tooltip.js';
import AppMenu from '../js/components/AppMenu.js';
import PipelineVisualizer from '../js/components/PipelineVisualizer.js';
import PipelineContextMenu from '../js/components/PipelineContextMenu.js';
import PopupWithForm from './components/PopupWithForm.js';

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

const contextMenu = new PipelineContextMenu();

const popupWithFormPipeChangeState = new PopupWithForm(
    '#popup-pipe-statechange',
    '#form-pipe-statechange',
    'Сменить состояние участка МГ',
    (data) => {
        submitFormPipeChangeState(data);
    },
);

const popupWithFormNodeChangeState = new PopupWithForm(
    '#popup-node-statechange',
    '#form-node-statechange',
    'Сменить состояние кранового узла',
    (data) => {
        submitFormNodeChangeState(data);
    },
);

const pipelineScheme = new PipelineVisualizer(
    'scheme',
    contextMenu,
    popupWithFormPipeChangeState,
    popupWithFormNodeChangeState,
    {}
);


function renderLoading(isLoading) {
  if (isLoading) {
      constant.loadingScreen.classList.add('loader_disactive');
  }
}

// функция отправки данных о ТО, введенных в форму
function submitFormPipeChangeState(data) {
    const newState = {
        name: data.name,
        prod_date: data.date,
        valve: valveId
      };
    popupWithFormService.renderLoading(true);
    api.addNewService(newState)
        .then(() => {
            popupWithFormPipeChangeState.close();
            location.reload()
        })
      .catch((err) => {
            console.log(`Ошибка: ${err}`);
      })
      .finally(() => popupWithFormPipeChangeState.renderLoading(false));
  }

// new Tooltip();
new AppMenu();

popupWithFormPipeChangeState.setEventListeners();
popupWithFormNodeChangeState.setEventListeners();


Promise.all([api.getMyProfile(), api.getPipelines()])
    .then(([userData, pipelines]) => {
        newUserInfo.setUserInfo(userData);
        pipelineScheme.render(pipelines);
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading(true));
