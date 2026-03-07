import { getApi } from '../../getApi.js';
import { initUser } from '../..//userInfo.js';
import { renderLoading } from '../../loadingScreen.js';
import * as constant from '../../utils/constants.js';
import Chart from '../../components/Chart.js';
import Plan from '../../components/Plan.js';

const planId = document.querySelector('.card').id;

const api = getApi();

const planInstance = new Plan('#plan__container', '#plan-template', '#quarterly-template');

// промис (заполнение данных пользователя) и (функция загрузки ТПА с сервера)
Promise.all([initUser(), api.getPlanWithChildren(planId)])
  .then(([userData, planData]) => {
    planInstance.renderAnnualPlan(planData);
    new Chart(
      '#chart-annual',
      planData.total_proposals,
      planData.completed_proposals,
      planData.total_economy,
      planData.sum_economy,
      230
    );
    planData.quarterly_plans.forEach((plan, index) => {
      new Chart(
        `#chart-q${index + 1}`,
        plan.planned_proposals,
        plan.completed_proposals,
        plan.planned_economy,
        plan.sum_economy,
        100
      );
    });
  })
  .catch((err) => {
    console.log(err);
  })
  .finally(() => renderLoading(true));
