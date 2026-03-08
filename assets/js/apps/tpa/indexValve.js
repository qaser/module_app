import { getApi } from '../../getApi.js';
import { initUser } from '../..//userInfo.js';
import { renderLoading } from '../../loadingScreen.js';
import Table from '../../components/Table.js';
import FormFilter from '../../components/FormFilter.js';
import * as constant from '../../utils/constants.js';

const api = getApi();

// создание объекта таблицы со строками ссылками
const newTable = new Table({ table: '.table__body' });

newTable.init();

initUser()
  .then(() => {
    new FormFilter(
      api.getEquipmentChildren.bind(api),
      'filter_submit',
      'id_equipment',
      'equipment',
      'sidebar__form-input'
    );
    const targetField = document.querySelector('#id_equipment');
    targetField.setAttribute('data-tooltip', constant.tooltipFormField);
  })
  .catch((err) => {
    console.log(`Ошибка: ${err}`);
  })
  .finally(() => renderLoading(true));
