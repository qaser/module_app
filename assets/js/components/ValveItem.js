export default class ValveItem {
    constructor(data) {
        this._card = document.querySelector(data.card);
        this._title = this._card.querySelector('.main__title');
        this._values = this._card.querySelectorAll('.card__value');
        this._service_type = document.getElementById('service_type');
        this._service_date = document.getElementById('prod_date');
    }

    replaceToForm(formAttrs, factories) {
        this._values.forEach((value) => {
            const formElem = document.createElement(formAttrs[value.id]['tag']);
            const spanElem = document.createElement('span');
            // spanElem.setAttribute('class', 'form-popup__input-error');
            // spanElem.setAttribute('id', `${value.id}-error`);
            if (formAttrs[value.id]['tag'] == 'select') {
                if (value.id == 'factory' || value.id == 'drive_factory') {
                    factories.forEach((i)=> {
                        const option = document.createElement('option');
                        option.value = `${i["name"]}, ${i["country"]}`;
                        option.id = i.id
                        option.innerHTML = `${i["name"]}, ${i["country"]}`;
                        if (value.textContent == option.value) {
                            option.selected = true;
                        }
                        formElem.appendChild(option);
                    })
                } else {
                    formAttrs[value.id]['options'].forEach((i) => {
                        const option = document.createElement('option');
                        option.value = i;
                        option.innerHTML = i;
                        if (value.textContent == option.value) {
                            option.selected = true;
                        }
                        formElem.appendChild(option);
                    });
                }
            }
            for (const [name, val] of Object.entries(formAttrs[value.id]['tagAttrs'])) {
                formElem.setAttribute(name, val);
                formElem.setAttribute('form', 'valve-edit');
                formElem.setAttribute('value', value.textContent);
                formElem.setAttribute('id', value.id);
            };
            // value.parentElement.insertBefore(spanElem, value.nextSibling);
            value.replaceWith(formElem);
        });
    }

    replaceToTable() {
        const formInputs = this._card.querySelectorAll('.card__input')
        formInputs.forEach((input, id, _) => {
            // input.nextSibling.remove()
            input.replaceWith(this._values[id]);
        })
    }

    renderItem(valve) {
        const eq = valve.equipment;
        const type = valve.valve_type;
        const diam = valve.diameter;
        const pressure = valve.pressure;
        const num = valve.tech_number;
        this._title.textContent = `${eq} | ${type} Ду${diam}, Ру${pressure} | №${num}`;
        this._values.forEach((item) => {
            item.textContent = valve[item.id];
        });
        this._service_type.textContent = valve.latest_service.service_type;
        this._service_date.textContent = valve.latest_service.prod_date;
    }
}
