import * as config from './config/config.js';
import * as constant from './utils/constants.js';
import Api from './api/Api.js';
import UserInfo from './components/UserInfo.js';
import Tooltip from '../js/components/Tooltip.js';
import AppMenu from '../js/components/AppMenu.js';
import Chart from '../js/components/Chart.js'
import Plan from '../js/components/Plan.js'

const planId = document.querySelector('.card').id;

// создание объекта api
const api = new Api({
    baseUrl: config.apiConfig.url,
    headers:{
        'X-CSRFToken': document.getElementsByName('csrfmiddlewaretoken')[0].value,
        'Content-Type': 'application/json',
        // authorization: constant.apiConfig.token,
    }
});

// создание объекта с данными пользователя
const newUserInfo = new UserInfo({
    name: '.header__username',
    job: '.header__user-proff',
});

const planInstance = new Plan('#plan__container', '#plan-template', '#quarterly-template');


function renderLoading() {
    constant.loadingScreen.classList.toggle('loader_disactive');
};

new Tooltip();
new AppMenu();


// промис (заполнение данных пользователя) и (функция загрузки ТПА с сервера)
Promise.all([api.getMyProfile(), api.getPlanWithChildren(planId)])
    .then(([userData, planData]) => {
        newUserInfo.setUserInfo(userData);
        planInstance.renderAnnualPlan(planData);
        new Chart(
            '#chart-annual',
            planData.total_proposals,
            planData.completed_proposals,
            planData.total_economy,
            planData.sum_economy,
            230
        )
        planData.quarterly_plans.forEach((plan, index) => {
            new Chart(
                `#chart-q${index+1}`,
                plan.planned_proposals,
                plan.completed_proposals,
                plan.planned_economy,
                plan.sum_economy,
                100
            );
        })
    })
    .catch(err => {
        console.log(err);
    })
    .finally(() => renderLoading());
