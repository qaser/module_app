import * as config from './config/config.js';
import * as constant from './utils/constants.js';
import Api from './api/Api.js';
import UserInfo from './components/UserInfo.js';
import FormValidator from '../js/components/FormValidator.js';
import AppMenu from '../js/components/AppMenu.js';
import PipelineVisualizer from '../js/components/PipelineVisualizer.js';
import PipelineContextMenu from '../js/components/PipelineContextMenu.js';
import PopupWithForm from './components/PopupWithForm.js';
import PollingClient from './api/PollingClient.js';


const formValidators = {};

// словарь с селекторами и классами форм, использую при валидации форм
const formConfig = {
    formSelector: '.form-popup',
    inputSelector: '.form-popup__input',
    submitButtonSelector: '.form-popup__button',
    disactiveButtonClass: 'form-popup__button_disactive',
    inputErrorClass: 'form-popup__input_invalid',
    errorClass: 'form-popup__input-error_active'
}

const pollingClient = new PollingClient({
  endpoint: '/api/notifications/unread/'
});

// создание объекта api
const api = new Api({
    baseUrl: config.apiConfig.url,
    headers:{
        'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
        'Content-Type': 'application/json',
        // authorization: constant.apiConfig.token,
    }
});

// универсальная функция для валидации форм (доступ по имени формы)
const enableValidation = (config) => {
    const formList = Array.from(document.querySelectorAll(config.formSelector));
    formList.forEach((formElement) => {
        const validator = new FormValidator(config, formElement);
        // получаем данные из атрибута `name` у формы
        const formName = formElement.getAttribute('name');
        formValidators[formName] = validator;
        validator.enableValidation();
    });
};

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
        submitFormChangeState(data);
    },
);

const popupWithFormPipeLimit = new PopupWithForm(
    '#popup-pipe-limit',
    '#form-pipe-limit',
    'Установить давление ограничения на участке МГ',
    (data) => {
        submitFormLimit(data);
    },
);

const popupWithFormPipeLimitEnd = new PopupWithForm(
    '#popup-pipe-limit-end',
    '#form-pipe-limit-end',
    'Снять ограничение на участке МГ',
    (data) => {
        submitFormLimitEnd(data);
    },
);

const popupWithFormNodeChangeState = new PopupWithForm(
    '#popup-node-statechange',
    '#form-node-statechange',
    'Сменить состояние кранового узла',
    (data) => {
        submitFormChangeState(data);
    },
);

const pipelineScheme = new PipelineVisualizer(
    'scheme',
    contextMenu,
    popupWithFormPipeChangeState,
    popupWithFormNodeChangeState,
    popupWithFormPipeLimit,
    popupWithFormPipeLimitEnd,
    {}
);


function renderLoading(isLoading) {
  if (isLoading) {
      constant.loadingScreen.classList.add('loader_disactive');
  }
}


function submitFormLimit(data) {
    const selected = pipelineScheme.getSelectedElement();
    if (!selected) {
        console.warn('Не выбран элемент для изменения лимита');
        return;
    }
    const newLimit = {
        id: selected.id,
        pressure_limit: data.pressure_limit,
        start_date: data.start_date,
        limit_reason: data.limit_reason,
    };
    api.editPipeLimit(newLimit)
        .then(() => {
            api.getPipelines()
                .then(pipelines => pipelineScheme.render(pipelines))
                .catch(error => console.error('Error refreshing pipeline:', error));
            popupWithFormPipeLimit.close();
        })
        .catch((err) => {
            console.error(`Ошибка: ${err}`);
        })
        .finally(() => popupWithFormPipeLimit.renderLoading(false));
    popupWithFormPipeLimit.renderLoading(true);
}


function submitFormLimitEnd(data) {
    const selected = pipelineScheme.getSelectedElement();
    if (!selected) {
        console.warn('Не выбран элемент для изменения лимита');
        return;
    }
    const endLimit = {
        id: selected.id,
        end_date: data.end_date,
    };
    api.endPipeLimit(endLimit)
        .then(() => {
            api.getPipelines()
                .then(pipelines => pipelineScheme.render(pipelines))
                .catch(error => console.error('Error refreshing pipeline:', error));
            popupWithFormPipeLimitEnd.close();
        })
        .catch((err) => {
            console.error(`Ошибка: ${err}`);
        })
        .finally(() => popupWithFormPipeLimitEnd.renderLoading(false));
    popupWithFormPipeLimitEnd.renderLoading(true);
}


function submitFormChangeState(data) {
    const selected = pipelineScheme.getSelectedElement();
    if (!selected) {
        console.warn('Не выбран элемент для смены состояния');
        return;
    }
    if (selected.type === 'pipe') {
        const newState = {
            id: selected.id,
            state_type: data.state_type,
            start_date: data.start_date,
            description: data.description,
        };
        api.changePipeState(newState)
            .then(() => {
                api.getPipelines()
                    .then(pipelines => pipelineScheme.render(pipelines))
                    .catch(error => console.error('Error refreshing pipeline:', error));
                popupWithFormPipeChangeState.close();
            })
            .catch((err) => {
                console.error(`Ошибка: ${err}`);
            })
            .finally(() => popupWithFormPipeChangeState.renderLoading(false));
        popupWithFormPipeChangeState.renderLoading(true);
    } else if (selected.type === 'node') {
        const newState = {
            id: selected.id,
            state_type: data.state_type,
            description: data.description,
        };
        api.changeNodeState(newState)
            .then(() => {
                api.getPipelines()
                    .then(pipelines => pipelineScheme.render(pipelines))
                    .catch(error => console.error('Error refreshing pipeline:', error));
                popupWithFormNodeChangeState.close();
            })
            .catch((err) => {
                console.error(`Ошибка: ${err}`);
            })
            .finally(() => popupWithFormNodeChangeState.renderLoading(false));
        popupWithFormNodeChangeState.renderLoading(true);
    }
}


new AppMenu();
enableValidation(formConfig);

popupWithFormPipeChangeState.setEventListeners();
popupWithFormNodeChangeState.setEventListeners();
popupWithFormPipeLimit.setEventListeners();
popupWithFormPipeLimitEnd.setEventListeners();


Promise.all([api.getMyProfile(), api.getPipelines()])
    .then(([userData, pipelines]) => {
        newUserInfo.setUserInfo(userData);
        pipelineScheme.render(pipelines);
        pollingClient.start();
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading(true));
