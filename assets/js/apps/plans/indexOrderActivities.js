import * as config from '../../config/config.js';
import * as constant from '../../utils/constants.js';
import Api from '../../api/Api.js';
import UserInfo from '../../components/UserInfo.js';
import Tooltip from '../../../js/components/Tooltip.js';
import AppMenu from '../../../js/components/AppMenu.js';
import FormValidator from '../../components/FormValidator.js';
import PopupWithForm from '../../components/PopupWithForm.js';
import PopupWithConfirm from '../../components/PopupWithConfirm.js';


const actionButtons = document.querySelectorAll('.activity-card__button[data-action]');


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

const popupWithFormAddActivity = new PopupWithForm(
    '#popup-new-activity',
    '#form-new-activity',
    'Добавить новое мероприятие',
    (data) => {
        submitFormNewActivity(data);
    },
);

const popupWithFormMarkActivity = new PopupWithForm(
    '#popup-mark-activity',
    '#form-mark-activity',
    'Отметить выполнение',
    (data) => {
        submitFormMarkActivity(data);
    },
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

const popupWithConfirmDelete = new PopupWithConfirm(
    '#popup-confirm-delete',
    '#form-delete',
    submitConfirmDelete
);


function renderLoading(isLoading) {
  if (isLoading) {
      constant.loadingScreen.classList.add('loader_disactive');
  }
}


function setupDeadlineTypeListener() {
    deadlineTypeSelect.addEventListener('change', function () {
        if (this.value === 'date') {
            deadlineDateInput.disabled = false;
            deadlineDateInput.required = true;
        } else if (this.value === 'permanent') {
            deadlineDateInput.disabled = true;
            deadlineDateInput.required = false;
            deadlineDateInput.value = ''; // сбрасываем значение
        }
    });

    // Инициализация при открытии попапа (на случай, если значение уже выбрано)
    const event = new Event('change');
    deadlineTypeSelect.dispatchEvent(event);
}


function submitFormNewActivity(data) {
    // Собираем ID выбранных подразделений из кнопок
    const selectedDepartmentIds = Array.from(depsContainer.querySelectorAll('.form-popup__tag-btn[data-selected="true"]'))
        .map(btn => btn.dataset.value);

    // Проверяем, выбрано ли хотя бы одно подразделение
    if (selectedDepartmentIds.length === 0) {
        errorSpan.textContent = 'Выберите хотя бы одно подразделение';
        hiddenInput.setCustomValidity('Выберите хотя бы одно подразделение');

        // Добавляем активный класс для отображения ошибки
        errorSpan.classList.add('form-popup__input-error_active');

        return Promise.reject(new Error('Не выбраны подразделения'));
    } else {
        hiddenInput.setCustomValidity('');
        hiddenInput.value = selectedDepartmentIds.join(',');

        // Убираем класс ошибки, если всё в порядке
        errorSpan.classList.remove('form-popup__input-error_active');
    }
    const deadline_date = data.deadline_type === 'date' && data.deadline_date
        ? data.deadline_date
        : null;
    data.deadline_date = deadline_date
    // Формируем данные для отправки
    const formData = {
        order: orderId,
        ...data,
        departments: selectedDepartmentIds, // массив чисел или строк
    };

    // Отправляем запрос
    api.createOrderActivity(formData)
        .then((activity) => {
            // Успешно создано — обновляем список или добавляем в DOM
            console.log('Мероприятие успешно добавлено:', activity);
            popupWithFormAddActivity.close(); // закрываем попап
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


function submitFormMarkActivity(data) {
    let activityId = popupWithFormMarkActivity.getExtraData()['activityId'];
    const { status, actual_completion_date, comment } = data;
    api.markOrderActivity(activityId, { status, actual_completion_date, comment })
        .then(() => {
            popupWithFormMarkActivity.close();
            // Обновляем страницу или карточку мероприятия
            location.reload(); // или можно обновить через HTMX / fetch
        })
        .catch(err => {
            console.error('Ошибка при отметке выполнения:', err);
            if (err.errors) {
                showFormErrors(popupWithFormMarkActivity, err.errors);
            } else {
                console.error('Ошибка при маркировке мероприятия:', err);
            }
        });
}


function submitConfirmDelete() {
    api.deleteOrder(orderId)
        .then(() => {
            popupWithConfirmDelete.close();
            location.href = '/plans/orders/';
        })
        .catch(err => {
            console.error('Ошибка при удалении приказа:', err);
        });
}


function submitConfirmArchive() {
    let activityId = popupWithConfirmArchive.getExtraData()['activityId'];
    api.changeOrderActivity(activityId)
        .then(() => {
            popupWithConfirmArchive.close();
            location.reload();
        })
        .catch(err => {
            console.error('Ошибка при архивации:', err);
        });
}


function submitConfirmUnarchive() {
    let activityId = popupWithConfirmUnarchive.getExtraData()['activityId'];
    api.changeOrderActivity(activityId)
        .then(() => {
            popupWithConfirmUnarchive.close();
            location.reload();
        })
        .catch(err => {
            console.error('Ошибка при разархивации:', err);
        });
}


new Tooltip();
new AppMenu();
// enableValidation(formConfig);
popupWithFormMarkActivity.setEventListeners();
popupWithConfirmArchive.setEventListeners();
popupWithConfirmUnarchive.setEventListeners();
popupWithFormAddActivity.setEventListeners();
popupWithConfirmDelete.setEventListeners();

// addNewActivityBtn.addEventListener('click', () => {
//     const action = button.dataset.action;
//     const activityId = button.dataset.activityId;
//     popupWithFormAddActivity.setExtraData({ activityId });
//     popupWithFormAddActivity.open();
//     setupDeadlineTypeListener();
// });

// deleteProtocolBtn.addEventListener('click', () => {
//     popupWithConfirmDelete.open();
// });

actionButtons.forEach(button => {
    button.addEventListener('click', () => {
        const action = button.dataset.action;
        const activityId = button.dataset.activityId;
        if (action === 'mark') {
            popupWithFormMarkActivity.setExtraData({ activityId });
            popupWithFormMarkActivity.open();
        } else if (action === 'archive') {
            popupWithConfirmArchive.setExtraData({ activityId });
            popupWithConfirmArchive.open();
        } else if (action === 'unarchive') {
            popupWithConfirmUnarchive.setExtraData({ activityId });
            popupWithConfirmUnarchive.open();
        }
    });
});

// depButtons.forEach(btn => {
//     btn.addEventListener('click', () => {
//         const id = btn.dataset.value;
//         const isSelected = btn.dataset.selected === 'true';
//         if (isSelected) {
//             btn.dataset.selected = 'false';
//             btn.setAttribute('aria-pressed', 'false');
//         } else {
//             btn.dataset.selected = 'true';
//             btn.setAttribute('aria-pressed', 'true');
//         }
//     });
// });


api.getMyProfile()
    .then((userData) => {
        newUserInfo.setUserInfo(userData);
    })
    .catch(err => {
        console.log(`Ошибка: ${err}`);
    })
    .finally(() => renderLoading(true));
