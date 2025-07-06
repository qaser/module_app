import * as config from '../js/config/config.js';
import * as constant from '../js/utils/constants.js';
import Api from '../js/api/Api.js';
import UserInfo from '../js/components/UserInfo.js';
import PipeItem from './components/PipeItem.js';
import Image from './components/Image.js';
import Section from '../js/components/Section.js';
import PopupWithImage from '../js/components/PopupWithImage.js';
import PopupWithForm from './components/PopupWithForm.js';
import FormHandler from './components/FormHandler.js';
import Tooltip from '../js/components/Tooltip.js';
import FormValidator from '../js/components/FormValidator.js';
import FileManager from './components/FileManager.js';
import HiddenElement from './components/HiddenElement.js';
import AppMenu from '../js/components/AppMenu.js';


const pipeId = document.querySelector('.card').id;
let isUploadButtonAdded = false;
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


const cardWithFiles = new HiddenElement('#cardFiles')
// const btnFileAdd = new HiddenElement('.card__button_add')


// экземпляр карточки c файлами
// const fileInstance = new Section({
//     renderer: (item) => {
//         const newFile = filesCard(item);
//         fileInstance.setItem(newFile);
//     },
// },
// '.card__files');


// создание объекта с данными пользователя
const newUserInfo = new UserInfo({
    name: '.header__username',
    job: '.header__user-proff',
});


// создание объекта с данными о ТПА
const pipeInstance = new PipeItem({
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


// функция отправки данных о новом файле, введенных в форму
function submitFormNewFile(data) {
    let formData = new FormData();
    formData.append('name', data.name);
    formData.append('pipe_id', pipeId);
    // собираем объект из файлов
    if (data.files.length > 0) {
        Object.entries(data.files).map((file) => {
            formData.append('doc', file[1]);
        });
    }
    popupWithFormNewFile.renderLoading(true);
    api.addPipeFile(formData)
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


// function filesCard(item) {
//     const file = new FileManager(
//         item,
//         '.file-template',
//         handleFileDeleteClick
//     );
//     const instance = file.renderFile();
//     return instance;
// }


// function handleFileDeleteClick(evt, fileId) {
//     const id = fileId.replace(/\D/g, '')
//     // renderLoading()
//     api.deletePipeFile(id)
//         .then((res) => {
//             if (res.status == 204) {
//                 elementDelete(fileId, filesContainer);
//                 haveFiles -= 1
//             }
//         })
//         // .finally(() => renderLoading());
// };


// function elementDelete(id, container) {
//     const elem = container.querySelector(`#${id}`)
//     elem.remove()
// }


// function filesClassDeleteToggle() {
//     const btnsFileDelete = document.querySelectorAll('.card__delete')
//     btnsFileDelete.forEach((btn) => {
//         btn.classList.toggle('hidden')
//     })
// }


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

Promise.all([api.getMyProfile(), api.getPipeItem(pipeId)])
    .then(([userData, pipe]) => {
        newUserInfo.setUserInfo(userData);
        pipeInstance.renderItem(pipe);
        // if (pipe.files.length > 0) {
        //     haveFiles = pipe.files.length;
        //     cardWithFiles.show();
        //     fileInstance.renderItems(pipe.files);
        // } else {
        //     cardWithFiles.hide();
        // }
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading());
