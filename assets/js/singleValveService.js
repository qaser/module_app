import * as config from '../js/config/config.js';
import * as constant from '../js/utils/constants.js';
import Api from '../js/api/Api.js';
import UserInfo from '../js/components/UserInfo.js';
import Calendar from './components/Calendar.js';
import Service from './components/Service.js';
import Section from './components/Section.js';
import Work from './components/Work.js';
import PopupWithForm from './components/PopupWithForm.js';
import PopupWithConfirm from './components/PopupWithConfirm.js';
import FormValidator from '../js/components/FormValidator.js';
import PopupWithImages from './components/PopupWithImages.js';

let serviceId;
let workId;
let workPlanned;
const formValidators = {};
const xhr = new XMLHttpRequest();
const valveId = document.querySelector('.calendar').id;
const token = document.getElementsByName('csrfmiddlewaretoken')[0].value;
const descriptionInput = document.getElementById('editwork-description');
const doneInput = document.getElementById('editwork-done');
const faultsInput = document.getElementById('editwork-faults');
const filesInput = document.getElementById('editwork-files');
const sizeText = document.getElementById('uploadForm_Size');
const statusText = document.getElementById('uploadForm_Status');
const progressBar = document.getElementById('progressBar');
const sizeEditText = document.getElementById('uploadFormEdit_Size');
const statusEditText = document.getElementById('uploadFormEdit_Status');
const progressEditBar = document.getElementById('progressBarEdit');

// словарь с селекторами и классами форм, использую при валидации форм
const formConfig = {
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
    headers:{
        'X-CSRFToken': token,
        'Content-Type': 'application/json',
    }
});

// создание объекта с данными пользователя
const newUserInfo = new UserInfo({
    name: '.header__username',
    job: '.header__user-proff',
});

// создание объекта с данными о ТО
const calendar = new Calendar(
    '.calendar__item',
    handleServiceClick,
    handleEmptyServiceClick
);

const serviceRender = new Section({
    renderer: (item) => {
        const newService = createService(item);
        serviceRender.setItem(newService);
    },
}, '.service');

const popupWithFormService = new PopupWithForm(
    '#popup-newservice',
    '#form-newservice',
    'Добавить запись о ТОиР',
    (data) => {
        submitFormService(data);
    },
);

const popupWithConfirmForm = new PopupWithConfirm(
    '#popup-confirm-delete',
    '#form-delete',
    submitConfirmForm
);

const popupWithFormNewWork = new PopupWithForm(
    '#popup-newwork',
    '#form-newwork',
    'Добавить дополнительную работу',
    (data) => {
        submitFormNewWork(data);
    },
);

const popupWithFormEditWork = new PopupWithForm(
    '#popup-editwork',
    '#form-editwork',
    'Внести изменения в работу',
    (data) => {
        submitFormEditWork(data);
    },
);

const popupImages = new PopupWithImages('#popup-images');

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


function submitFormEditWork(data) {
    let formData = new FormData();
    formData.append("description", data.description);
    formData.append("done", data.done == 'Выполнено' ? true : false);
    formData.append("faults", data.faults == '' ? 'Замечаний нет' : data.faults);
    formData.append("work", workId);
    formData.append("planned", workPlanned);
    // собираем объект из файлов
    if (data.files.length > 0) {
        Object.entries(data.files).map((file) => {
            formData.append(`file_${file[0]}`, file[1]);
        });
    }
    popupWithFormNewWork.renderLoading(true);
    patchWorkRequest(formData, workId)
        .then((work) => {
            const element = createWork(work);
            popupWithFormNewWork.close();
            let targetElem = document.getElementById(element.id);
            targetElem.replaceWith(element);
            popupWithFormEditWork.close();
        })
        .catch((err) => {
            console.log(`Ошибка: ${err}`);
        })
        .finally(() => popupWithFormNewWork.renderLoading(false));
}


function fileListItems (files) {
    let filesData = new DataTransfer();
    files.forEach((file) => {
        filesData.items.add(new File([file], file.name));
    })
    let fileList = filesData.files;
    return fileList;
}


function fillWorkInputs(work) {
    descriptionInput.value = work.work.description;
    if (work.work.planned == true) {
        descriptionInput.setAttribute('disabled', '');
    }
    else {
        descriptionInput.removeAttribute('disabled');
    }
    doneInput.value = work.done == true ? 'Выполнено' : 'Не выполнено';
    faultsInput.value = work.faults;
    // filesInput.value = [];
    // if (work.files.length > 0) {
    //     filesInput.files = fileListItems(work.files);
    // }
}


function handleWorkClick(work) {
    workId = work.id;
    workPlanned = work.work.planned;
    formValidators['new-work'].resetValidation();
    fillWorkInputs(work);
    sizeEditText.textContent = '';
    statusEditText.textContent = '';
    popupWithFormEditWork.open();
};


// функция отправки данных после подтверждения
function submitConfirmForm(serviceId, element) {
    api.deleteService(serviceId)
        .then(() => {
            element.remove();
            element = null;
            popupWithConfirmForm.close();
            // здесь нужно добавить изменение в календаре
            // а пока перезагружаю страницу
            location.reload()
        })
        .catch((err) => {
            console.log(`Ошибка: ${err}`);
        })
  }


// функция отправки данных о ТО, введенных в форму
function submitFormService(data) {
    const newItem = {
        name: data.name,
        prod_date: data.date,
        valve: valveId
      };
    popupWithFormService.renderLoading(true);
    api.addNewService(newItem)
        .then((service) => {
            // const newService = createService(service);
            popupWithFormService.close();
            // здесь нужно добавить изменение в календаре
            // а пока перезагружаю страницу
            location.reload()
        })
      .catch((err) => {
            console.log(`Ошибка: ${err}`);
      })
      .finally(() => popupWithFormService.renderLoading(false));
  }


function handleEmptyServiceClick(evt) {
    const date = evt.target.attributes.name.value;
    if (date.length == 9) {
        const correctDate = date.slice(0, 5) + '0' + date.slice(5);
        setActualDateInField(correctDate);
    }
    else {
        setActualDateInField(date);
    };
    popupWithFormService.open();
}


// установка актуальной даты в поле формы
function setActualDateInField(date) {
    const dateField = document.querySelector('#service-date');
    dateField.value = date;
}


function handleServiceClick(list_ids) {
    serviceRender.clear();
    renderLoading(false)
    list_ids.forEach((id) => {
        api.getServiceItem(id)
            .then((service) => {
                const newService = createService(service);
                serviceRender.setItemFront(newService);
                const workInstance = new Section({
                    renderer: (work) => {
                    const newWork = createWork(work);
                    workInstance.setItem(newWork);
                    },
                },
                '.report');
                workInstance.renderItems(service.works);
            })
            .finally(() => {renderLoading(true)})
    })
}


function createWork(item) {
    const work = new Work(
        item,
        '.work-template',
        handleWorkClick,
        handlePhotoGalleryClick,
    );
    const instance = work.generateWork();
    return instance;
}


function handlePhotoGalleryClick(files) {
    popupImages.open(files);
}


function handleServiceBasketClick(evt, serviceId, element) {
    popupWithConfirmForm.open(serviceId, element);
};


function handleServiceNewWorkClick(id) {
    serviceId = id
    formValidators['new-work'].resetValidation()
    sizeText.textContent = '';
    statusText.textContent = '';
    popupWithFormNewWork.open();
};


function postWorkRequest(formData) {
    return new Promise(function(resolve, reject) {
        xhr.open('POST', `${config.apiConfig.url}/works/`, true);
        xhr.setRequestHeader('X-CSRFToken', token);
        xhr.responseType = 'json';
        xhr.upload.addEventListener('progress', progressHandler, false);
        xhr.addEventListener('load', loadHandler, false);
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.response);
            } else {
                reject(xhr.statusText);
            }
        };
        xhr.onerror = () => reject(xhr.statusText);
        xhr.send(formData);
    });
}

function patchWorkRequest(formData, id) {
    return new Promise(function(resolve, reject) {
        xhr.open('PATCH', `${config.apiConfig.url}/works/${id}/`, true);
        xhr.setRequestHeader('X-CSRFToken', token);
        xhr.responseType = 'json';
        xhr.upload.addEventListener('progress', progressEditHandler, false);
        xhr.addEventListener('load', loadEditHandler, false);
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.response);
            } else {
                reject(xhr.statusText);
            }
        };
        xhr.onerror = () => reject(xhr.statusText);
        xhr.send(formData);
    });
}


function progressHandler(event) {
    // считаем размер загруженного и процент от полного размера
    const loadedMb = (event.loaded/constant.BYTES_IN_MB).toFixed(1)
    const totalSizeMb = (event.total/constant.BYTES_IN_MB).toFixed(1)
    const percentLoaded = Math.round((event.loaded / event.total) * 100)
    progressBar.value = percentLoaded
    sizeText.textContent = `${loadedMb} из ${totalSizeMb} МБ`
    statusText.textContent = `Загружено ${percentLoaded}% | `
}


function loadHandler() {
    progressBar.value = 0
}


function progressEditHandler(event) {
    // считаем размер загруженного и процент от полного размера
    const loadedMb = (event.loaded/constant.BYTES_IN_MB).toFixed(1)
    const totalSizeMb = (event.total/constant.BYTES_IN_MB).toFixed(1)
    const percentLoaded = Math.round((event.loaded / event.total) * 100)
    progressEditBar.value = percentLoaded
    sizeEditText.textContent = `${loadedMb} из ${totalSizeMb} МБ`
    statusEditText.textContent = `Загружено ${percentLoaded}% | `
}

function loadEditHandler() {
    progressEditBar.value = 0
}


// функция отправки данных о новой работе, введенной в форму
function submitFormNewWork(data) {
    let formData = new FormData();
    formData.append("description", data.description);
    formData.append("done", data.done == 'Выполнено' ? true : false);
    formData.append("faults", data.faults == '' ? 'Замечаний нет' : data.faults);
    formData.append("service", serviceId);
    // собираем объект из файлов
    if (data.files.length > 0) {
        Object.entries(data.files).map((file) => {
            formData.append(`file_${file[0]}`, file[1]);
        });
    }
    popupWithFormNewWork.renderLoading(true);
    postWorkRequest(formData)
        .then((work) => {
            const item = createWork(work);
            const workInstance = new Section({
                renderer: () => {
                    workInstance.setItem(item);
                },
            },
            `#report-${serviceId}`);  // ищем таблицу ТО по id
            popupWithFormNewWork.close();
            workInstance.setItem(item);
        })
        .catch((err) => {
            console.log(`Ошибка: ${err}`);
        })
        .finally(() => popupWithFormNewWork.renderLoading(false));
}


function createService(item) {
    const service = new Service(
        item,
        '.service-template',
        handleServiceBasketClick,
        handleServiceNewWorkClick,
    );
    const instance = service.generateService();
    return instance;
}

// добавление в селектор формы нового ТО выбора вида ТО
function createServiceTypeOptions() {
    const select = document.querySelector('#service-name');
    api.getServiceTypes()
        .then((items) => {
            items.forEach((i) => {
                const option = document.createElement('option');
                option.value = i.name;
                option.innerHTML = i.name;
                select.appendChild(option);
            });
        })
        .catch((err) => {
            console.log(`Ошибка: ${err.status}`);
          });
}

function renderLoading(isLoading) {
    if (isLoading) {
        constant.loadingScreen.classList.add('loader_disactive');
    } else {
        constant.loadingScreen.classList.remove('loader_disactive');
    }
}


enableValidation(formConfig);
createServiceTypeOptions();
popupImages.setEventListeners();
popupWithFormService.setEventListeners();
popupWithFormNewWork.setEventListeners();
popupWithFormEditWork.setEventListeners();
popupWithConfirmForm.setEventListeners();
calendar.generateLinks();
api.getMyProfile()
    .then((userData) => {
        newUserInfo.setUserInfo(userData);
    })
    .catch(err => {
        console.log(`Ошибка: ${err.status}`);
    })
    .finally(() => renderLoading(true));
