import * as config from './config/config.js';
import * as constant from './utils/constants.js';
import Api from './api/Api.js';
import UserInfo from './components/UserInfo.js';
import LeakItem from './components/LeakItem.js';
import Image from './components/Image.js';
import Section from './components/Section.js';
import PopupWithImage from './components/PopupWithImage.js';
import FormValidator from './components/FormValidator.js';


const leak_id = document.querySelector('.card').id;
// const formValidators = {};

// словарь с селекторами и классами форм, использую при валидации форм
// const formConfig = {
//   formSelector: '.card__form',
//   inputSelector: '.card__input',
//   submitButtonSelector: '.card__button_done',
  // disactiveButtonClass: 'form-popup__button_disactive',
  // inputErrorClass: 'form-popup__input_invalid',
  // errorClass: 'form-popup__input-error_active'
// }

// создание объекта api
const api = new Api({
    baseUrl: config.apiConfig.url,
    headers:{
        'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
        'Content-Type': 'application/json'
    }
});


// экземпляр карточки
const imageInstance = new Section({
    renderer: (item) => {
        const newImage = imagesCard(item);
        imageInstance.setItem(newImage);
    },
},
'.card__images');


// создание объекта с данными пользователя
const newUserInfo = new UserInfo({
    name: '.header__username',
    job: '.header__user-proff',
});


// создание объекта с данными о ТПА
const leakInstance = new LeakItem({
    card: '.main'
})


// создание объектов со всплывающими окнами
const popupImage = new PopupWithImage('#popup-image');


// универсальная функция для валидации форм (доступ по имени формы)
// const enableValidation = (config) => {
//   const formList = Array.from(document.querySelectorAll(config.formSelector));
//   formList.forEach((formElement) => {
//       const validator = new FormValidator(config, formElement);
      // получаем данные из атрибута `name` у формы
//       const formName = formElement.getAttribute('name');
//       formValidators[formName] = validator;
//       validator.enableValidation();
//   });
// };


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


function handleImageDeleteClick(evt, imageId) {
    console.log(imageId);
};


function imagesClassDelete() {
    const imageContainers = document.querySelectorAll('.card__image-container')
    const images = document.querySelectorAll('.card__image')
    imageContainers.forEach((item) => {
        item.classList.toggle('card__image-container_delete')
    })
    images.forEach((item) => {
        item.classList.toggle('card__image_delete')
    })
}


// слушатель кнопки изменения информации об утечке
// функция замены тегов <p> на теги <input>, находится в классе
constant.btnLeakEdit.addEventListener('click', () => {
    // formValidators['add-avatar'].resetValidation();
    // api.getFactories()
    //     .then((factories) => {
    //         imagesClassDelete();
    //         imageInstance.replaceToForm(constant.formAttrs, factories);
    //         constant.btnValveEdit.replaceWith(createFormEditButtons());
    //     })
    imagesClassDelete();
    leakInstance.replaceToForm(constant.formAttrs);
    constant.btnLeakEdit.replaceWith(createFormEditButtons());
});


function createFormEditButtons() {
    const formElem = document.createElement('form');
    const btnFormDone = document.createElement('button');
    const btnFormCancel = document.createElement('button');
    formElem.setAttribute('class', 'card__form');
    formElem.setAttribute('name', 'leak-edit');
    btnFormDone.setAttribute('class', 'button card__button card__button_done');
    btnFormDone.setAttribute('type', 'submit');
    btnFormCancel.setAttribute('class', 'button card__button card__button_cancel');
    btnFormCancel.setAttribute('type', 'reset');
    formElem.appendChild(btnFormDone);
    formElem.appendChild(btnFormCancel);
    btnFormCancel.addEventListener('click', () => {
        leakInstance.replaceToTable();
        imagesClassDelete();
        formElem.replaceWith(constant.btnLeakEdit);
    })
    return formElem;
}


function renderLoading(isLoading) {
    if (isLoading) {
        constant.loadingScreen.classList.add('loader_disactive');
    }
}

// enableValidation(formConfig);
popupImage.setEventListeners();

// промис (заполнение данных пользователя) и (функция загрузки ТПА с сервера)
Promise.all([api.getMyProfile(), api.getLeakItem(leak_id)])
    .then(([userData, leak]) => {
        newUserInfo.setUserInfo(userData);
        leakInstance.renderItem(leak);
        imageInstance.renderItems(leak.images);
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading(true));
