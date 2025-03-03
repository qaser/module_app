import * as config from '../js/config/config.js';
import * as constant from '../js/utils/constants.js';
import Api from '../js/api/Api.js';
import UserInfo from '../js/components/UserInfo.js';
import ProposalItem from './components/ProposalItem.js';
import Section from '../js/components/Section.js';
import PopupWithForm from './components/PopupWithForm.js';
import FormHandler from './components/FormHandler.js';
import Tooltip from '../js/components/Tooltip.js';
import FormValidator from '../js/components/FormValidator.js';
import FileManager from './components/FileManager.js';
import HiddenElement from './components/HiddenElement.js';
import AppMenu from '../js/components/AppMenu.js';
import StatusManager from '../js/components/StatusManager.js';


const proposalId = document.querySelector('.card').id;
const noteTextarea = document.querySelector('#note');
let isUploadButtonAdded = false;
let haveFiles = 0;
const filesContainer = document.querySelector('.card__files'); // контейнер с файлами
const formValidators = {};

// словарь с селекторами и классами форм, использую при валидации форм
const formProposalConfig = {
  formSelector: '.card__field',
  inputSelector: '.card__input',
  submitButtonSelector: '.card__button_done',
  disactiveButtonClass: 'form-popup__button_disactive',
  inputErrorClass: 'form-popup__input_invalid',
  errorClass: 'form-popup__input-error_active'
}

const formFileConfig = {
    formSelector: '.form-popup',
    inputSelector: '.form-popup__input',
    submitButtonSelector: '.form-popup__button',
    disactiveButtonClass: 'form-popup__button_disactive',
    inputErrorClass: 'form-popup__input_invalid',
    errorClass: 'form-popup__input-error_active'
}

// создание объекта api
const api = new Api({
    baseUrl: config.apiConfig.url,
    headers: {
        // 'Content-Type': 'application/json',
        'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value
    },
});


const cardWithFiles = new HiddenElement('#cardFiles')
const btnFileAdd = new HiddenElement('.card__button_add')


// экземпляр карточки c файлами
const fileInstance = new Section({
    renderer: (item) => {
        const newFile = filesCard(item);
        fileInstance.setItem(newFile);
    },
},
'.card__files');


// создание объекта с данными пользователя
const newUserInfo = new UserInfo({
    name: '.header__username',
    job: '.header__user-proff',
});


// создание объекта с данными
const proposalInstance = new ProposalItem({
    card: '.main'
})


const popupWithFormNewFile = new PopupWithForm(
    '#popup-file',
    '#form-newfile',
    'Добавить новый документ',
    (data) => {
        submitFormNewFile(data);
    },
);

const popupWithStatus = new PopupWithForm(
    '#popup-status',
    '#form-status',
    'Сменить статус РП',
    (data) => {
        submitFormChangeStatus(data);
    },
);


// добавление в селектор формы изменения статуса выбора вида статуса
function createStatusOptions(possibleStatuses) {
    const select = document.querySelector('#status');
    select.innerHTML = ''; // Очищаем старые значения
    possibleStatuses.forEach((i) => {
        const option = document.createElement('option');
        option.value = i.code;
        option.textContent = i.label;
        select.appendChild(option);
    });
}


function submitFormChangeStatus(data) {
    let formData = new FormData();
    formData.append('note', data.note);
    formData.append('proposal_id', proposalId);
    formData.append('new_status', data.status);
    api.addNewStatus(formData)
        .then(() => {
            popupWithStatus.close();
            location.reload();
        })
        .catch((err) => {
            console.error(`Ошибка смены статуса: ${err}`);
        });
}


// функция отправки данных о новом файле, введенных в форму
function submitFormNewFile(data) {
    let formData = new FormData();
    formData.append('name', data.name);
    formData.append('proposal_id', proposalId);
    // собираем объект из файлов
    if (data.files.length > 0) {
        Object.entries(data.files).map((file) => {
            formData.append('doc', file[1]);
        });
    }
    popupWithFormNewFile.renderLoading(true);
    api.addValveFile(formData)
        .then((file) => {
            fileInstance.renderItems([file]);
            const fileCard = document.querySelector(`#file-${file.id}`);
            const btnFileDelete = fileCard.querySelector('.card__delete');
            btnFileDelete.classList.remove('hidden');
            haveFiles += 1;
            popupWithFormNewFile.close();
        })
        .catch((err) => {
            console.log(`Ошибка: ${err}`);
        })
        .finally(() => popupWithFormNewFile.renderLoading(false));
}


// функция отправки данных, введенных в форму
function submitFormEditProposal(data) {
    let formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
        if (Array.isArray(value)) {
            value.forEach(item => formData.append(key, item));
        } else {
            formData.append(key, value);
        }
    });
    // renderLoading()
    api.changeProposal(formData, proposalId)
        .then((proposal) => {
            const formElem = document.querySelector('.card__form');
            proposalInstance.renderItem(valve);
            proposalInstance.replaceToTable();
            formElem.replaceWith(constant.btnEdit);
            btnFileAdd.hide()
            filesClassDeleteToggle()
            if (haveFiles == 0) {
                cardWithFiles.hide();
            }
        })
        .catch((err) => {
            console.log(`Ошибка: ${err}`);
        })
        // .finally(() => renderLoading());
  }


function filesCard(item) {
    const file = new FileManager(
        item,
        '.file-template',
        handleFileDeleteClick
    );
    const instance = file.renderFile();
    return instance;
}


function handleFileDeleteClick(evt, fileId) {
    const id = fileId.replace(/\D/g, '')
    // renderLoading()
    api.deleteValveFile(id)
        .then((res) => {
            if (res.status == 204) {
                elementDelete(fileId, filesContainer);
                haveFiles -= 1
            }
        })
        // .finally(() => renderLoading());
};


function elementDelete(id, container) {
    const elem = container.querySelector(`#${id}`)
    elem.remove()
}


function filesClassDeleteToggle() {
    const btnsFileDelete = document.querySelectorAll('.card__delete')
    btnsFileDelete.forEach((btn) => {
        btn.classList.toggle('hidden')
    })
}


// слушатель кнопки изменения информации об РП
// функция замены тегов <p> на теги <input>, находится в классе
constant.btnEdit.addEventListener('click', () => {
    // formValidators['add-avatar'].resetValidation();
    proposalInstance.replaceToForm(constant.formAttrs);
    constant.btnEdit.replaceWith(createFormEditButtons());
    const formEditProposal = new FormHandler(
        '.card__form',
        '#valve_info',
        '.card__input',
        '.button card__button card__button_done',
        (data) => {submitFormEditProposal(data)},
    );
    formEditProposal.setEventListeners();
});


function createFormEditButtons() {
    // преобразование карточки в форму + добавить кнопки Отправить, Отменить
    const formElem = document.createElement('form');
    const btnFormDone = document.createElement('button');
    const btnFormCancel = document.createElement('button');
    formElem.setAttribute('class', 'card__form');
    formElem.setAttribute('name', 'valve-edit');
    btnFormDone.setAttribute('class', 'button card__button card__button_done');
    btnFormDone.setAttribute('type', 'submit');
    btnFormDone.setAttribute('data-tooltip', 'Сохранить изменения');
    btnFormCancel.setAttribute('class', 'button card__button card__button_cancel');
    btnFormCancel.setAttribute('data-tooltip', 'Отменить изменения');
    btnFormCancel.setAttribute('type', 'reset');
    formElem.appendChild(btnFormDone);
    formElem.appendChild(btnFormCancel);
    // enableValidation(formValveConfig);
    btnFormCancel.addEventListener('click', () => {
        proposalInstance.replaceToTable();
        formElem.replaceWith(constant.btnEdit);
        filesClassDeleteToggle();
        if (haveFiles == 0) {
            cardWithFiles.hide();
        }
        btnFileAdd.hide();
    })
    filesClassDeleteToggle();
    cardWithFiles.show();
    btnFileAdd.show();
    btnFileAdd.rawElem().addEventListener('click', () => {
        popupWithFormNewFile.open();
    })
    return formElem;
}


// универсальная функция для валидации форм (доступ по имени формы)
const enableValidation = (config) => {
    const formList = Array.from(document.querySelectorAll(config.formSelector));
    formList.forEach((formElement) => {
        const validator = new FormValidator(config, formElement);
      //   получаем данные из атрибута `name` у формы
        const formName = formElement.getAttribute('name');
        formValidators[formName] = validator;
        validator.enableValidation();
    });
};


function setEventToCard(popup, possibleStatuses) {
    const activeCard = document.querySelector('.status-card_active');
    if (activeCard) {
        activeCard.addEventListener('click', () => {
            createStatusOptions(possibleStatuses); // Загружаем доступные статусы
            popup.open(); // Открываем popup
        });
    }
}


function renderLoading() {
    constant.loadingScreen.classList.toggle('loader_disactive');
};

enableValidation(formFileConfig);
popupWithFormNewFile.setEventListeners();
popupWithStatus.setEventListeners();
new Tooltip();
new AppMenu();

// промис (заполнение данных пользователя) и (функция загрузки РП с сервера)
Promise.all([api.getMyProfile(), api.getProposalItem(proposalId)])
    .then(([userData, proposal]) => {
        newUserInfo.setUserInfo(userData);
        proposalInstance.renderItem(proposal);
        if (proposal.files.length > 0) {
            haveFiles = proposal.files.length;
            cardWithFiles.show();
            fileInstance.renderItems(proposal.files);
        } else {
            cardWithFiles.hide();
        }
        const statusManager = new StatusManager(proposal.statuses, '.status_container');
        statusManager.render();
        const lastStatus = proposal.statuses[proposal.statuses.length - 1]
        if (lastStatus.possible_statuses.length > 0) {
            setEventToCard(popupWithStatus, lastStatus.possible_statuses);
        }
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading());
