export default class FormFilter {
    constructor(apiMethod, formSelectorId, fieldId, fieldName, fieldClass, structureEnable) {
        this._getElementChildren = apiMethod  // Передаем экземпляр Api в FormFilter
        this._form = document.getElementById(formSelectorId);
        this._field = document.getElementById(fieldId);
        this._structureEnable = structureEnable
        this._fieldName = fieldName
        this._fieldClass = fieldClass
        this.init();
    }

    init() {
        this._field.addEventListener('change', this._handleElementChange.bind(this));
    }

    _handleElementChange(event) {
        const selectedElementId = event.target.value;
        if (selectedElementId) {
            this._fetchChildren(selectedElementId, event.target);
        }
    }

    _fetchChildren(parentId, targetSelect) {
        this._getElementChildren(parentId, this._structureEnable)
            .then(data => {
                if (data.length > 0) {
                    this._restructureFields(targetSelect, data);
                } else {
                    targetSelect.name = this._fieldName;
                    targetSelect.id = `id_${this._fieldName}`;
                    if (targetSelect.previousElementSibling.tagName === 'SELECT') {
                        targetSelect.previousElementSibling.name = '';
                        targetSelect.previousElementSibling.id = '';
                    }
                    while (targetSelect.nextElementSibling) {
                        targetSelect.nextElementSibling.remove();
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка при загрузке данных:', error);
            });
    }



    // нужно добавить проверку - если сразу выбран элемент бех потомков то удалять последующие поля
    _restructureFields(targetSelect, children) {
        // удаляем последующие и добавляем одно новое
        while (targetSelect.nextElementSibling) {
            targetSelect.nextElementSibling.remove();
        }
        if (targetSelect.previousElementSibling.tagName === 'SELECT') {
            targetSelect.previousElementSibling.name = '';
            targetSelect.previousElementSibling.id = '';
        }
        const newSelect = document.createElement('select');
        newSelect.name = '';
        newSelect.className = this._fieldClass;
        newSelect.id = '';
        targetSelect.name = this._fieldName;
        targetSelect.id = `id_${this._fieldName}`;
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.text = '---------';
        newSelect.appendChild(defaultOption);
        children.forEach(child => {
            const option = document.createElement('option');
            option.value = child.id;
            option.text = child.name;
            newSelect.appendChild(option);
        });
        newSelect.addEventListener('change', this._handleElementChange.bind(this));
        targetSelect.parentNode.insertBefore(newSelect, targetSelect.nextSibling);
    }
}
