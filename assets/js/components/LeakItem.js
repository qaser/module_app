export default class LeakItem {
    constructor(data) {
        this._card = document.querySelector(data.card);
        this._title = this._card.querySelector('.main__title');
        this._values = this._card.querySelectorAll('.card__value');
        this._service_type = document.getElementById('service_type');
        this._service_date = document.getElementById('prod_date');
        this._doc_manual = document.getElementById('doc_manual');
        this._doc_passport = document.getElementById('doc_passport');
        this._doc_certificate = document.getElementById('doc_certificate');
        this._doc_logbook = document.getElementById('doc_logbook');
        this._docs_dict = {
            'Руководство по эксплуатации': this._doc_manual,
            'Паспорт': this._doc_passport,
            'Сертификат': this._doc_certificate,
            'Формуляр': this._doc_logbook,
        };
    }

    _fillDocs(files) {
        files.forEach((doc) => {
            var _docLink = this._docs_dict[doc.name].querySelector('.card__value_ext');
            _docLink.id = doc.id
            _docLink.href = doc.doc
            _docLink.textContent = 'открыть'
        })
    }

    replaceToForm(formAttrs) {
        this._values.forEach((value) => {
            const formElem = document.createElement(formAttrs[value.id]['tag']);
            if (formAttrs[value.id]['tag'] == 'select') {
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
            for (const [name, val] of Object.entries(formAttrs[value.id]['tagAttrs'])) {
                formElem.setAttribute(name, val);
                formElem.setAttribute('form', 'leak-edit');
                formElem.setAttribute('value', value.textContent);
                formElem.setAttribute('id', value.id);
            };
            value.replaceWith(formElem);
        });
    }

    // replaceToForm(formAttrs) {
    //     this._values.forEach((value) => {
    //         const formElem = document.createElement(formAttrs[value.id]['tag']);
    //         if (formAttrs[value.id]['tag'] == 'select') {
    //             if (value.id == 'factory' || value.id == 'drive_factory') {
    //                 factories.forEach((i)=> {
    //                     const option = document.createElement('option');
    //                     option.value = `${i["name"]}, ${i["country"]}`;
    //                     option.id = i.id
    //                     option.innerHTML = `${i["name"]}, ${i["country"]}`;
    //                     if (value.textContent == option.value) {
    //                         option.selected = true;
    //                     }
    //                     formElem.appendChild(option);
    //                 })
    //             } else {
    //                 formAttrs[value.id]['options'].forEach((i) => {
    //                     const option = document.createElement('option');
    //                     option.value = i;
    //                     option.innerHTML = i;
    //                     if (value.textContent == option.value) {
    //                         option.selected = true;
    //                     }
    //                     formElem.appendChild(option);
    //                 });
    //             }
    //         }
    //         for (const [name, val] of Object.entries(formAttrs[value.id]['tagAttrs'])) {
    //             formElem.setAttribute(name, val);
    //             formElem.setAttribute('form', 'leak-edit');
    //             formElem.setAttribute('value', value.textContent);
    //             formElem.setAttribute('id', value.id);
    //         };
    //         value.replaceWith(formElem);
    //     });
    // }

    replaceToTable() {
        const formInputs = this._card.querySelectorAll('.card__input')
        formInputs.forEach((input, id, _) => {
            input.replaceWith(this._values[id]);
        })
    }

    renderItem(leak) {
        // const dep = leak.department;
        // const loc = leak.location;
        // const type = leak.leak_type;
        // const diam = valve.diameter;
        // const num = valve.tech_number;
        // this._title.textContent = `${dep} | ${loc} | ${type} | Ду${diam} | №${num}`;
        this._values.forEach((item) => {
            item.textContent = leak[item.id];
        });
        // this._service_type.textContent = valve.latest_service.service_type;
        // this._service_date.textContent = valve.latest_service.prod_date;
        // this._fillDocs(valve.files)
    }
}
