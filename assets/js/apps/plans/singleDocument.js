import * as config from '../../config/config.js';
import * as constant from '../../utils/constants.js';
import Api from '../../api/Api.js';
import UserInfo from '../../components/UserInfo.js';
import Tooltip from '../../../js/components/Tooltip.js';
import AppMenu from '../../../js/components/AppMenu.js';
import FormValidator from '../../components/FormValidator.js';
import PopupWithForm from '../../components/PopupWithForm.js';
import PopupWithConfirm from '../../components/PopupWithConfirm.js';


const category = document.querySelector('.content').id;
const formValidators = {};
const docId = document.querySelector('.main__title').id;
const actionButtons = document.querySelectorAll('.event-card__button[data-action]');

const addNewEventBtn = document.querySelector('#addNewEventBtn');
const deleteDocBtn = document.querySelector('#deleteDocBtn');

const depsContainer = document.getElementById('departments-container');
const hiddenInput = document.getElementById('departments');
const depButtons = depsContainer.querySelectorAll('.form-popup__tag-btn');
const errorSpan = document.getElementById('departments-error');

// словарь с селекторами и классами форм, использую при валидации форм
const formConfig = {
    formSelector: '.form-popup',
    inputSelector: '.form-popup__input',
    submitButtonSelector: '.form-popup__button',
    disactiveButtonClass: 'form-popup__button_disactive',
    inputErrorClass: 'form-popup__input_invalid',
    errorClass: 'form-popup__input-error_active',
}

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

const popupWithFormAddEvent = new PopupWithForm(
    '#popup-new-event',
    '#form-new-event',
    'Добавить новое мероприятие',
    (data) => {
        submitFormNewEvent(data);
    },
);

const popupWithFormMarkEvent = new PopupWithForm(
    '#popup-mark-event',
    '#form-mark-event',
    'Отметить выполнение',
    (data) => {
        submitFormMarkEvent(data);
    },
);

const popupWithConfirmComplete = new PopupWithConfirm(
    '#popup-confirm-complete',
    '#form-complete',
    submitConfirmComplete
);

const popupWithConfirmArchive = new PopupWithConfirm(
    '#popup-confirm-archive',
    '#form-archive',
    submitConfirmArchive
);

const popupWithConfirmUnarchive = new PopupWithConfirm(
    '#popup-confirm-unarchive',
    '#form-unarchive',
    submitConfirmUnarchive
);

const popupWithDocConfirmDelete = new PopupWithConfirm(
    '#popup-confirm-delete',
    '#form-delete',
    submitConfirmDelete
);


function renderLoading(isLoading) {
  if (isLoading) {
      constant.loadingScreen.classList.add('loader_disactive');
  }
}


// Функция для показа/скрытия полей в зависимости от выбранного типа расписания
function handleScheduleTypeChange() {
  const scheduleTypeSelect = document.getElementById('schedule_type');
  const allScheduleFields = document.querySelectorAll('[schedule_type]');
  if (!scheduleTypeSelect) return;
  // Функция для скрытия всех полей
  function hideAllFields() {
    allScheduleFields.forEach(field => {
      field.classList.remove('form-popup__field_active');
    });
  }
  // Функция для показа полей нужного типа
  function showFieldsByType(type) {
    const fieldsToShow = document.querySelectorAll(`[schedule_type="${type}"]`);
    fieldsToShow.forEach(field => {
      field.classList.add('form-popup__field_active');
    });
  }
  // Обработчик изменения выбора
  function updateFieldsVisibility() {
    const selectedType = scheduleTypeSelect.value;
    // Скрываем все поля
    hideAllFields();
    // Показываем поля для выбранного типа
    if (selectedType && selectedType !== 'continuous') {
      showFieldsByType(selectedType);
    }
  }
  // Инициализация при загрузке
  updateFieldsVisibility();
  // Слушаем изменения в выпадающем списке
  scheduleTypeSelect.addEventListener('change', updateFieldsVisibility);
  return {
    updateFieldsVisibility,
    hideAllFields,
    showFieldsByType
  };
}

// Функция для валидации полей в зависимости от типа расписания
function validateScheduleFields(data) {
  const scheduleType = data.schedule_type;
  const errors = {};
  // Проверка для типа 'once' (фиксированная дата)
  if (scheduleType === 'once') {
    if (!data.due_date) {
      errors.due_date = 'Укажите срок выполнения';
    } else {
      const dueDate = new Date(data.due_date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

    //   if (dueDate < today) {
    //     errors.due_date = 'Дата не может быть в прошлом';
    //   }
    }
  }
  // Проверка для типа 'periodic' (периодическое)
  if (scheduleType === 'periodic') {
    if (!data.period_unit) {
      errors.period_unit = 'Выберите периодичность';
    }
    if (!data.period_interval || data.period_interval < 1) {
      errors.period_interval = 'Интервал должен быть положительным числом';
    }
    if (!data.start_date) {
      errors.start_date = 'Укажите дату начала периода';
    }
  }
  // Проверка для типа 'relative' (относительное)
  if (scheduleType === 'relative') {
    if (!data.relative_base) {
      errors.relative_base = 'Выберите вариант базовой даты';
    }
    if (!data.relative_position) {
      errors.relative_position = 'Выберите позицию';
    }
    if (!data.relative_day || isNaN(data.relative_day) || data.relative_day < 0) {
      errors.relative_day = 'Укажите корректное количество дней';
    }
  }
  return errors;
}


// Обновленная функция submitFormNewEvent
function submitFormNewEvent(data) {
    // Собираем ID выбранных подразделений
    const depsContainer = document.getElementById('departments-container');
    const errorSpan = document.getElementById('departments-error');
    const hiddenInput = document.getElementById('departments');
    const selectedDepartmentIds = Array.from(depsContainer.querySelectorAll('.form-popup__tag-btn[data-selected="true"]'))
        .map(btn => btn.dataset.value);
    // Проверяем, выбрано ли хотя бы одно подразделение
    if (selectedDepartmentIds.length === 0) {
        errorSpan.textContent = 'Выберите хотя бы одно подразделение';
        hiddenInput.setCustomValidity('Выберите хотя бы одно подразделение');
        errorSpan.classList.add('form-popup__input-error_active');
        return Promise.reject(new Error('Не выбраны подразделения'));
    } else {
        hiddenInput.setCustomValidity('');
        hiddenInput.value = selectedDepartmentIds.join(',');
        errorSpan.classList.remove('form-popup__input-error_active');
    }
    // Валидация полей в зависимости от типа расписания
    const scheduleErrors = validateScheduleFields(data);
    // Если есть ошибки валидации, показываем их
    if (Object.keys(scheduleErrors).length > 0) {
        Object.entries(scheduleErrors).forEach(([field, message]) => {
        const errorElement = document.getElementById(`${field}-error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.classList.add('form-popup__input-error_active');
        }
        });
        return Promise.reject(new Error('Ошибка валидации полей расписания'));
    }
    // Убираем все ошибки валидации
    document.querySelectorAll('.form-popup__input-error_active').forEach(el => {
        el.classList.remove('form-popup__input-error_active');
        el.textContent = '';
    });
    // Формируем данные для отправки
    const formData = {
        document: docId,
        ...data,
        departments: selectedDepartmentIds,
    };
    console.log(formData);
    api.createEvent(formData)
        .then((event) => {
            // Успешно создано — обновляем список или добавляем в DOM
            console.log('Мероприятие успешно добавлено:', event);
            popupWithFormAddEvent.close(); // закрываем попап
            location.reload();
            // Здесь можно вызвать обновление списка мероприятий
            // Например: addActivityToPage(activity);
        })
        .catch((err) => {
            console.error('Ошибка при добавлении мероприятия:', err);
            // Показываем ошибку на форме при необходимости
            errorSpan.textContent = 'Не удалось добавить мероприятие. Попробуйте позже.';
            throw err;
        });
}


// Функция для инициализации формы при открытии попапа
function initializeEventForm() {
  // Инициализируем управление видимостью полей
  const scheduleManager = handleScheduleTypeChange();
  // Сбрасываем ошибки при открытии формы
  document.querySelectorAll('.form-popup__input-error').forEach(el => {
    el.textContent = '';
    el.classList.remove('form-popup__input-error_active');
  });
  // Сбрасываем выбранные подразделения
  const depsButtons = document.querySelectorAll('.form-popup__tag-btn');
  depsButtons.forEach(btn => {
    btn.dataset.selected = "false";
    btn.classList.remove('form-popup__tag-btn_selected');
  });

  // Обновляем видимость полей
  if (scheduleManager) {
    scheduleManager.updateFieldsVisibility();
  }
}


function submitFormMarkEvent(data) {
    let eventId = popupWithFormMarkEvent.getExtraData()['eventId'];
    const { status, actual_completion_date, comment } = data;
    api.markEvent(eventId, { status, actual_completion_date, comment })
        .then(() => {
            popupWithFormMarkEvent.close();
            // Обновляем страницу или карточку мероприятия
            location.reload(); // или можно обновить через HTMX / fetch
        })
        .catch(err => {
            console.error('Ошибка при отметке выполнения:', err);
            if (err.errors) {
                showFormErrors(popupWithFormMarkEvent, err.errors);
            } else {
                console.error('Ошибка при маркировке мероприятия:', err);
            }
        });
}


function submitConfirmDelete() {
    api.deleteDoc(docId)
        .then(() => {
            popupWithDocConfirmDelete.close();
            location.href = `/plans/${category}/`;
        })
        .catch(err => {
            console.error('Ошибка при удалении:', err);
        });
}


function submitConfirmComplete() {
    let eventId = popupWithConfirmComplete.getExtraData()['eventId'];
    api.completeEvent(eventId)
        .then(() => {
            popupWithConfirmComplete.close();
            location.reload();
        })
        .catch(err => {
            console.error('Ошибка при завершении мероприятия:', err);
        });
}


function submitConfirmArchive() {
    let eventId = popupWithConfirmArchive.getExtraData()['eventId'];
    api.changeEvent(eventId)
        .then(() => {
            popupWithConfirmArchive.close();
            location.reload();
        })
        .catch(err => {
            console.error('Ошибка при архивации:', err);
        });
}


function submitConfirmUnarchive() {
    let eventId = popupWithConfirmUnarchive.getExtraData()['eventId'];
    api.changeEvent(eventId)
        .then(() => {
            popupWithConfirmUnarchive.close();
            location.reload();
        })
        .catch(err => {
            console.error('Ошибка при разархивации:', err);
        });
}

if (addNewEventBtn) {
    addNewEventBtn.addEventListener('click', () => {
        // const action = button.dataset.action;
        // const eventId = button.dataset.eventId;
        // popupWithFormAddActivity.setExtraData({ eventId });
        popupWithFormAddEvent.open();
        initializeEventForm()
    });
}

if (deleteDocBtn) {
    deleteDocBtn.addEventListener('click', () => {
        popupWithDocConfirmDelete.open();
    });
}


actionButtons.forEach(button => {
    button.addEventListener('click', () => {
        const action = button.dataset.action;
        const eventId = button.dataset.instanceId;
        console.log(action, eventId);

        if (action === 'mark') {
            popupWithFormMarkEvent.setExtraData({ eventId });
            popupWithFormMarkEvent.open();
        } else if (action === 'complete') {
            popupWithConfirmComplete.setExtraData({ eventId });
            popupWithConfirmComplete.open();
        } else if (action === 'archive') {
            popupWithConfirmArchive.setExtraData({ eventId });
            popupWithConfirmArchive.open();
        } else if (action === 'unarchive') {
            popupWithConfirmUnarchive.setExtraData({ eventId });
            popupWithConfirmUnarchive.open();
        }
    });
});

depButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const id = btn.dataset.value;
        const isSelected = btn.dataset.selected === 'true';
        if (isSelected) {
            btn.dataset.selected = 'false';
            btn.setAttribute('aria-pressed', 'false');
        } else {
            btn.dataset.selected = 'true';
            btn.setAttribute('aria-pressed', 'true');
        }
    });
});


new Tooltip();
new AppMenu();

handleScheduleTypeChange();
enableValidation(formConfig);

popupWithFormMarkEvent.setEventListeners();
popupWithConfirmArchive.setEventListeners();
popupWithConfirmUnarchive.setEventListeners();
popupWithFormAddEvent.setEventListeners();
popupWithDocConfirmDelete.setEventListeners();
popupWithConfirmComplete.setEventListeners();


api.getMyProfile()
    .then((userData) => {
        newUserInfo.setUserInfo(userData);
    })
    .catch(err => {
        console.log(`Ошибка: ${err}`);
    })
    .finally(() => renderLoading(true));
