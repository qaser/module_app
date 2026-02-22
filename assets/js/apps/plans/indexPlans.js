import { getApi } from '../../getApi.js';
import { initUser } from '../..//userInfo.js';
import { renderLoading } from '../../loadingScreen.js';
import Table from '../../components/Table.js';

// создание объекта api
const api = getApi();

initUser()
  .catch((err) => {
    console.log(`Ошибка: ${err}`);
  })
  .finally(() => renderLoading(true));
