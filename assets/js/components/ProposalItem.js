export default class ProposalItem {
    constructor(data) {
        this._card = document.querySelector(data.card);
        this._title = this._card.querySelector('.main__title');
        this._values = this._card.querySelectorAll('.card__value');
        // this._service_type = document.getElementById('service_type');
        // this._service_date = document.getElementById('prod_date');
    }

    replaceToForm(formAttrs) {
        this._values.forEach((value) => {
            const formElem = document.createElement(formAttrs[value.id]['tag']);
            const spanElem = document.createElement('span');
            // spanElem.setAttribute('class', 'form-popup__input-error');
            // spanElem.setAttribute('id', `${value.id}-error`);
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

    renderItem(proposal) {
        const reg_num = proposal.reg_num;
        const reg_date = proposal.reg_date;
        this._title.textContent = `РП №${reg_num} от ${reg_date}г.`;
        this._values.forEach((item) => {
            if (item.id === 'authors') {
                const authors = proposal.authors.map(author => author.lastname_and_initials).join(', ');
                item.textContent = authors;
            } else {
                item.textContent = proposal[item.id];
            }
        });
    }
}
