import * as constant from '../../utils/constants.js';
import { getApi } from '../../getApi.js';
import { initUser } from '../..//userInfo.js';
import { renderLoading } from '../../loadingScreen.js';
import FormFilter from '../../components/FormFilter.js';

const api = getApi();

initUser()
  .then(() => {
    new FormFilter(
      api.getDepartmentChildren.bind(api),
      'filter_submit',
      'id_department',
      'department',
      'form__input'
    );
    const targetField = document.querySelector('#id_department');
    targetField.setAttribute('data-tooltip', constant.tooltipFormField);
  })
  .catch((err) => {
    console.log(`Ошибка: ${err}`);
  })
  .finally(() => renderLoading(true));
