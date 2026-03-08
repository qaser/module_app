import { getApi } from '../../getApi.js';
import { initUser } from '../..//userInfo.js';
import { renderLoading } from '../../loadingScreen.js';
import Table from '../../components/Table.js';
// import SinglePipeVisualizer from '../js/components/SinglePipeVisualizer.js'

// const pipeId = document.querySelector('.content').id;

const api = getApi();

// создание объекта таблицы со строками ссылками
const newTable = new Table({ table: '.table__body' });

newTable.init();

initUser()
  .catch((err) => {
    console.log(err);
  })
  .finally(() => renderLoading(true));
