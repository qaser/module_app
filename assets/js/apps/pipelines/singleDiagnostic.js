import * as config from '../../config/config.js';
import * as constant from '../../utils/constants.js';
import Api from '../../api/Api.js';
import UserInfo from '../../components/UserInfo.js';
import DiagnosticItem from '../../components/DiagnosticItem.js';
import Section from '../../components/Section.js';
import PopupWithForm from '../../components/PopupWithForm.js';
import Tooltip from '../../components/Tooltip.js';
import FormValidator from '../../components/FormValidator.js';
import FileManager from '../../components/FileManager.js';
import HiddenElement from '../../components/HiddenElement.js';
import AppMenu from '../../components/AppMenu.js';
import PollingClient from '../../api/PollingClient.js';


const diagnosticId = document.querySelector('.card').id;
let haveFiles = 0;
const filesContainer = document.querySelector('.card__files'); // контейнер с файлами
const formValidators = {};

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


const cardWithFiles = new HiddenElement('#card_files')
const btnFileAdd = new HiddenElement('.card__button_add')
const emptyFilesBanner = new HiddenElement('#empty_files')

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


// создание объекта с данными о diagnostic
const diagnosticInstance = new DiagnosticItem({
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

const pollingClient = new PollingClient({
    endpoint: '/api/notifications/unread/'
});


// функция отправки данных о новом файле, введенных в форму
function submitFormNewFile(data) {
    let formData = new FormData();
    formData.append('name', data.name);
    formData.append('diagnostic_id', diagnosticId);
    // собираем объект из файлов
    if (data.files.length > 0) {
        Object.entries(data.files).map((file) => {
            formData.append('doc', file[1]);
        });
    }
    popupWithFormNewFile.renderLoading(true);
    api.addDiagnosticFile(formData)
        .then((file) => {
            fileInstance.renderItems([file]);
            const fileCard = document.querySelector(`#file-${file.id}`);
            const btnFileDelete = fileCard.querySelector('.card__delete');
            btnFileDelete.classList.remove('hidden');
            emptyFilesBanner.hide();
            haveFiles += 1;
            popupWithFormNewFile.close();
        })
        .catch((err) => {
            console.log(`Ошибка: ${err}`);
        })
        .finally(() => popupWithFormNewFile.renderLoading(false));
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
    renderLoading()
    api.deleteDiagnosticFile(id)
        .then((res) => {
            if (res.status == 204) {
                elementDelete(fileId, filesContainer);
                haveFiles -= 1
                if (haveFiles == 0) {
                    emptyFilesBanner.show();
                }
            }
        })
        .finally(() => renderLoading());
};


function elementDelete(id, container) {
    const elem = container.querySelector(`#${id}`)
    elem.remove()
}


function filesClassDeleteVisible() {
    const btnsFileDelete = document.querySelectorAll('.card__delete')
    btnsFileDelete.forEach((btn) => {
        btn.classList.remove('hidden')
    })
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


function renderLoading() {
    constant.loadingScreen.classList.toggle('loader_disactive');
}


enableValidation(formFileConfig);
popupWithFormNewFile.setEventListeners();
new Tooltip();
new AppMenu();

Promise.all([api.getMyProfile(), api.getDiagnosticItem(diagnosticId)])
    .then(([userData, diagnostic]) => {
        pollingClient.start();
        newUserInfo.setUserInfo(userData);
        diagnosticInstance.renderItem(diagnostic);
        if (diagnostic.files.length > 0) {
            haveFiles = diagnostic.files.length;
            fileInstance.renderItems(diagnostic.files);
            emptyFilesBanner.hide();
        }
        if (userData.role == 'admin' || userData.role == 'manager') {
            btnFileAdd.show();
            filesClassDeleteVisible();
            btnFileAdd.rawElem().addEventListener('click', () => {
                popupWithFormNewFile.open();
            })
        }
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading(true));
