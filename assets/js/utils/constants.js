// кнопки формы редактирования ТПА
export const btnEdit = document.querySelector('.card__button_edit');
export const btnDone = document.querySelector('.card__button_done');
export const btnCancel = document.querySelector('.card__button_cancel');


// экран загрузки
export const loadingScreen = document.querySelector('.loader');

// шаблон для загрузки картинки
export const uploadImageTemplate = `
    <div class="image_upload">
        <div class="card__image card__image_upload" data-tooltip="Добавить фотографию">
            <input type="file" id="imageUpload" class=" card__image_upload-input" accept="image/*">
            <label for="imageUpload" class=" card__image_upload-label"></label>
        </div>
    </div>
`;

export const tooltipFormField = 'Можно выбирать последовательно'

export const BYTES_IN_MB = 1048576;

// атрибуты преобразования формы данных об утечке
export const formAttrs = {
    'id': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'disabled': '',
      }
    },
    'direction': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'disabled': '',
      }
    },
    'station': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'disabled': '',
      }
    },
    'department': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'disabled': '',
      }
    },
    'equipment': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'disabled': '',
      }
    },
    'title': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'minlength': 3,
            'maxlength': 50,
            'required': '',
        }
    },
    'diameter': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'min': 1,
            'max': 1400,
            'required': '',
        }
    },
    'pressure': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'required': '',
        }
    },
    'valve_type': {
        'tag': 'select',
        'options': [
            'Задвижка клиновая',
            'Вентиль',
            'Кран шаровой',
            'Клапан запорный',
            'Клапан обратный',
            'Клапан предохранительный',
            'Клапан регулирующий',
        ],
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
            'required': '',
        }
    },
    'factory': {
        'tag': 'select',
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
    'year_made': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'min': 1950,
            'max': 3000,
        }
    },
    'year_exploit': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'min': 1950,
            'max': 3000,
        }
    },
    'tech_number': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'minlength': 1,
            'maxlength': 10,
            'required': '',
        }
    },
    'factory_number': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'minlength': 1,
            'maxlength': 20,
        }
    },
    'inventory_number': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'minlength': 1,
            'maxlength': 20,
        }

    },
    'lifetime': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'min': 1,
        }
    },
    'remote': {
        'tag': 'select',
        'options': [
            'Да',
            'Нет',
            'Не требуется',
        ],
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
    'label': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 50,
        }
    },
    'material': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 50,
        }
    },
    'design': {
        'tag': 'select',
        'options': [
            'Надземное',
            'Подземное',
            'В колодце',
        ],
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
    'drive_type': {
        'tag': 'select',
        'options': [
            'Пневматический',
            'Пневмогидравлический',
            'Ручной (ручка, рычаг, маховик)',
            'Ручной с механическим редуктором',
            'Электрический c механическим редуктором',
            'Без привода'
        ],
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
    'drive_factory': {
        'tag': 'select',
        'tagAttrs': {
            'class': 'card__value card__input',
        }
    },
    'drive_year_exploit': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'min': 1950,
            'max': 3000,
        }
    },
    'description': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 500,
            'rows': 1
        }
    },
    'place': {
        'tag': 'select',
        'options': [
            'КЦ',
            'ЛЧ',
        ],
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
    'is_valve': {
        'tag': 'select',
        'options': [
            'Да',
            'Нет',
        ],
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
    'specified_location': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 100,
            'rows': 1
        }
    },
    'type_leak': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 100,
            'rows': 1
        }
    },
    'volume': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'min': 1950,
            'max': 3000,
            'step': 0.00001
        }
    },
    'volume_dinamic': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'min': 1950,
            'max': 3000,
            'step': 0.00001
        }
    },
    'gas_losses': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'number',
            'min': 1950,
            'max': 3000,
            'step': 0.00001
        }
    },
    'reason': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 100,
            'rows': 1
        }
    },
    'detection_date': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'date',
        }
    },
    'planned_date': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'date',
        }
    },
    'fact_date': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'date',
        }
    },
    'method': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 100,
            'rows': 1
        }
    },
    'detector': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 100,
            'rows': 1
        }
    },
    'executor': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'disabled': '',
      }
    },
    'plan_work': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 500,
            'rows': 1
        }
    },
    'doc_name': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 100,
            'rows': 1
        }
    },
    'protocol': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 100,
            'rows': 1
        }
    },
    'is_done': {
        'tag': 'select',
        'options': [
            'Да',
            'Нет',
        ],
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
    'note': {
        'tag': 'textarea',
        'tagAttrs': {
            'class': 'card__value card__input',
            'type': 'text',
            'maxlength': 500,
            'rows': 1
        }
    },
    'is_draft': {
        'tag': 'select',
        'options': [
            'Да',
            'Нет',
        ],
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
    'valve': {
        'tag': 'input',
        'tagAttrs': {
            'class': 'card__value card__input',
            'required': '',
        }
    },
}
