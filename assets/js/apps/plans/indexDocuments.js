import * as config from '../../config/config.js';
import { getApi } from '../../getApi.js';
import { initUser } from '../..//userInfo.js';
import { renderLoading } from '../../loadingScreen.js';
import Table from '../../components/Table.js';
import FormValidator from '../../components/FormValidator.js';
import PopupWithForm from '../../components/PopupWithForm.js';

const doc_type = document.querySelector('.content');
const category = doc_type.id; // "orders"
const doc_category = doc_type.dataset; // { category: "order" }
const doc_category_value = doc_type.dataset.category; // "order"

const formValidators = {};
const addNewDocBtn = document.querySelector('#addNewDocBtn');
const showAllEventsBtn = document.querySelector('#showAllEventsBtn');

// словарь с селекторами и классами форм, использую при валидации форм
const formConfig = {
  formSelector: '.form-popup',
  inputSelector: '.form-popup__input',
  submitButtonSelector: '.form-popup__button',
  disactiveButtonClass: 'form-popup__button_disactive',
  inputErrorClass: 'form-popup__input_invalid',
  errorClass: 'form-popup__input-error_active',
};

const api = getApi();

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

// создание объекта таблицы со строками ссылками
const newTable = new Table({ table: '.table__body' });

const popupWithFormNewDoc = new PopupWithForm(
  '#popup-add-doc',
  '#form-add-doc',
  'Добавить новый документ',
  (data) => {
    submitFormNewDoc(data);
  }
);

function submitFormNewDoc(data) {
  data.category = doc_category.category;
  console.log(data.category);

  api
    .createDoc(data)
    .then(() => {
      popupWithFormNewDoc.close();
      location.reload();
    })
    .catch((err) => {
      console.error('Ошибка при создании нового документа:', err);
    });
}

enableValidation(formConfig);
if (addNewDocBtn) {
  addNewDocBtn.addEventListener('click', () => {
    popupWithFormNewDoc.open();
  });
}
showAllEventsBtn.addEventListener('click', () => {
  location.href = `/plans/${category}/events/`;
});

newTable.init();
popupWithFormNewDoc.setEventListeners();

initUser()
  .catch((err) => {
    console.log(`Ошибка: ${err}`);
  })
  .finally(() => renderLoading(true));
