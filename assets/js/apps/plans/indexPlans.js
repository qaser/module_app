import { getApi } from '../../getApi.js';
import { initUser } from '../..//userInfo.js';
import { renderLoading } from '../../loadingScreen.js';
import ChartWidget from '../../components/ChartWidget.js';

const planId = document.getElementById('rational').getAttribute('plan_id');
console.log(planId);

// создание объекта api
const api = getApi();

Promise.all([initUser(), api.getPlanWithChildren(planId)])
  .then(([userData, planData]) => {
    // Создаем виджет для годового плана
    const annualWidget = new ChartWidget('#chart-annual', planData, 'annual');

    // Создаем виджет для квартального плана
    const quarterWidget = new ChartWidget('#chart-q', planData, 'quarter');
  })
  .catch((err) => {
    console.log(err);
  })
  .finally(() => renderLoading(true));
