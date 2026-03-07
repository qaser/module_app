import * as config from './config/config.js';
import Api from './api/Api.js';

// создание объекта api
const api = new Api({
  baseUrl: config.apiConfig.url,
  headers: {
    'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
    // 'Content-Type': 'application/json',
    // authorization: constant.apiConfig.token,
  },
});

function getApi() {
  return api;
}

export { getApi };
