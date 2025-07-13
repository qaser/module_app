import * as config from '../js/config/config.js';
import * as constant from '../js/utils/constants.js';
import Api from '../js/api/Api.js';
import UserInfo from '../js/components/UserInfo.js';
import PipeItem from './components/PipeItem.js';
import Section from '../js/components/Section.js';
import PopupWithForm from './components/PopupWithForm.js';
import Tooltip from '../js/components/Tooltip.js';
import FormValidator from '../js/components/FormValidator.js';
import FileManager from './components/FileManager.js';
import HiddenElement from './components/HiddenElement.js';
import AppMenu from '../js/components/AppMenu.js';
import SinglePipeVisualizer from '../js/components/SinglePipeVisualizer.js'


const pipeId = document.querySelector('.card').id;
let haveFiles = 0;
const filesContainer = document.querySelector('.card__files'); // контейнер с файлами
const formValidators = {};

const testPipe = generateTestPipe()

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
    api.deletePipeFile(id)
        .then((res) => {
            if (res.status == 204) {
                elementDelete(fileId, filesContainer);
                haveFiles -= 1
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

function generateTestPipe(id = 1) {
  const pipe_units = [];
  const getRandomLength = () => +(10.5 + Math.random() * (12 - 10.5)).toFixed(2);
  const getRandomDefects = (length) => {
    const count = Math.random() < 0.02 ? Math.floor(Math.random() * 5) + 1 : 0; // 10% труб с дефектами
    return Array.from({ length: count }, () => ({
      position: +(Math.random() * length).toFixed(2)
    }));
  };

  // начальный стык
  pipe_units.push({ unit_type: 'kss', defects: Math.random() < 0.01 ? [{}] : [] });

  for (let i = 0; i < 3000; i++) {
    const length = getRandomLength();
    const defects = getRandomDefects(length);
    pipe_units.push({
      unit_type: 'tube',
      length: length,
      defects: defects
    });

    pipe_units.push({
      unit_type: 'kss',
      defects: Math.random() < 0.02 ? [{}] : []
    });
  }

  // Рассчитаем общую длину участка
  const totalLength = pipe_units
    .filter(u => u.unit_type === 'tube')
    .reduce((sum, tube) => sum + tube.length, 0);

  const start_km = +(Math.random() * 1000).toFixed(3);
  const end_km = +(start_km + totalLength / 1000).toFixed(3);

  return {
    id: id,
    pipeline: "Тестовый газопровод",
    start_point: start_km,
    end_point: end_km,
    diameter: 1420,
    departments: [{ id: 1, name: "Тестовое ЛПУМГ", start_point: start_km, end_point: end_km }],
    pipe_units: pipe_units,
    state: null,
    limit: null,
    exploit_year: 2020
  };
}


enableValidation(formFileConfig);
popupWithFormNewFile.setEventListeners();
new Tooltip();
new AppMenu();

Promise.all([api.getMyProfile(), api.getPipeItem(pipeId)])
    .then(([userData, pipe]) => {
        newUserInfo.setUserInfo(userData);
        pipeInstance.renderItem(pipe);
        const pipeVisualizer = new SinglePipeVisualizer(testPipe, "scheme");
        pipeVisualizer.render();
        if (pipe.files.length > 0) {
            haveFiles = pipe.files.length;
            cardWithFiles.show();
            fileInstance.renderItems(pipe.files);
        } else {
            cardWithFiles.hide();
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
    .finally(() => renderLoading());
