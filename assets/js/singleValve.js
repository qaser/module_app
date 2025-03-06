import * as config from '../js/config/config.js';
import * as constant from '../js/utils/constants.js';
import Api from '../js/api/Api.js';
import UserInfo from '../js/components/UserInfo.js';
import ValveItem from './components/ValveItem.js';
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


const valveId = document.querySelector('.card').id;
let isUploadButtonAdded = false;
let haveFiles = 0;
const imagesContainer = document.querySelector('.card__images'); // контейнер с фото
const filesContainer = document.querySelector('.card__files'); // контейнер с файлами
const formValidators = {};

// словарь с селекторами и классами форм, использую при валидации форм
const formValveConfig = {
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


// экземпляр карточки с фото
const imageInstance = new Section({
    renderer: (item) => {
        const newImage = imagesCard(item);
        imageInstance.setItem(newImage);
    },
},
'.card__images');


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


// создание объекта с данными о ТПА
const valveInstance = new ValveItem({
    card: '.main'
})


// создание объектов со всплывающими окнами
const popupImage = new PopupWithImage('#popup-image');


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
    formData.append('valve_id', valveId);
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


// функция отправки данных об изменении ТПА, введенных в форму
function submitFormEditValve(data) {
    let formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
        if (Array.isArray(value)) {
            value.forEach(item => formData.append(key, item));
        } else {
            formData.append(key, value);
        }
    });
    // renderLoading()
    api.changeValve(formData, valveId)
        .then((valve) => {
            const formElem = document.querySelector('.card__form');
            valveInstance.renderItem(valve);
            valveInstance.replaceToTable();
            imageClassUploadToggle();
            imagesClassDeleteToggle();
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


function handleImageClick(name, link) {
    popupImage.open(name, link);
}


function imagesCard(item) {
    const image = new Image(
        item,
        '.image-template',
        handleImageClick,
        handleImageDeleteClick
    );
    const instance = image.renderImage();
    return instance;
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


function handleImageDeleteClick(evt, imageId) {
    const id = imageId.replace(/\D/g, '')
    // renderLoading()
    api.deleteValveImage(id)
        .then((res) => {
            if (res.status == 204) {
                elementDelete(imageId, imagesContainer);
            }
        })
        // .finally(() => renderLoading());
};


function elementDelete(id, container) {
    const elem = container.querySelector(`#${id}`)
    elem.remove()
}


function imagesClassDeleteToggle() {
    const imageContainers = imagesContainer.querySelectorAll('.card__image-container')
    const images = imagesContainer.querySelectorAll('.card__image')
    imageContainers.forEach((item) => {
        item.classList.toggle('card__image-container_delete')
        if (item.hasAttribute('data-tooltip')) {
            item.removeAttribute('data-tooltip');
        } else {
            item.setAttribute('data-tooltip', 'Удалить фотографию');
        }
    })
    images.forEach((item) => {
        item.classList.toggle('card__image_delete')
    })
}


function imageClassUploadToggle() {
    if (!isUploadButtonAdded) {
        imagesContainer.insertAdjacentHTML('afterbegin', constant.uploadImageTemplate);
        isUploadButtonAdded = true;
        const addImageBtn = document.querySelector('#imageUpload');
        addImageBtn.addEventListener('change', (event) => {
            const file = event.target.files[0]; // Берем первый выбранный файл
            if (file) {
                uploadImage(file);
            }
        });
    } else {
        imagesContainer.removeChild(imagesContainer.firstElementChild);
        isUploadButtonAdded = false;
    }
}


function filesClassDeleteToggle() {
    const btnsFileDelete = document.querySelectorAll('.card__delete')
    btnsFileDelete.forEach((btn) => {
        btn.classList.toggle('hidden')
    })
}


function uploadImage(file) {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('valve_id', valveId);
    // renderLoading()
    api.addValveImage(formData, valveId)
        .then((data) => {
            imageInstance.renderItems([data])
            const newImageContainer = document.querySelector(`#image-${data.id}`);
            const newImage = newImageContainer.querySelector('.card__image')
            newImageContainer.classList.toggle('card__image-container_delete');
            newImage.classList.toggle('card__image_delete')
        })
        // .finally(() => renderLoading());
}


// слушатель кнопки изменения информации о ТПА
// функция замены тегов <p> на теги <input>, находится в классе
constant.btnEdit.addEventListener('click', () => {
    // formValidators['add-avatar'].resetValidation();
    api.getFactories()
        .then((factories) => {
            imagesClassDeleteToggle();
            imageClassUploadToggle();
            valveInstance.replaceToForm(constant.formAttrs, factories);
            constant.btnEdit.replaceWith(createFormEditButtons());
            const formEditValve = new FormHandler(
                '.card__form',
                '#valve_info',
                '.card__input',
                '.button card__button card__button_done',
                (data) => {submitFormEditValve(data)},
            );
            formEditValve.setEventListeners();
        })
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
        valveInstance.replaceToTable();
        imageClassUploadToggle()
        imagesClassDeleteToggle();
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


function renderLoading() {
    constant.loadingScreen.classList.toggle('loader_disactive');
}

enableValidation(formFileConfig);
popupImage.setEventListeners();
popupWithFormNewFile.setEventListeners();
new Tooltip();
new AppMenu();

// промис (заполнение данных пользователя) и (функция загрузки ТПА с сервера)
Promise.all([api.getMyProfile(), api.getValveItem(valveId)])
    .then(([userData, valve]) => {
        newUserInfo.setUserInfo(userData);
        valveInstance.renderItem(valve);
        imageInstance.renderItems(valve.images);
        if (valve.files.length > 0) {
            haveFiles = valve.files.length;
            cardWithFiles.show();
            fileInstance.renderItems(valve.files);
        } else {
            cardWithFiles.hide();
        }
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading());
