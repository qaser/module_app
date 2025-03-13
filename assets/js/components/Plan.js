export default class Plan {
    constructor(containerSelector, annualTemplateSelector, quarterlyTemplateSelector) {
        this.annualPlansContainer = document.querySelector(containerSelector);
        this.annualPlanTemplate = document.querySelector(annualTemplateSelector).content;
        this.quarterlyPlanTemplate = document.querySelector(quarterlyTemplateSelector).content;
        this.isAnyCardExpanded = false; // Флаг для отслеживания состояния карточек
    }

    ensureConnectorsContainer() {
        let connectorsContainer = document.getElementById('connectors-container');
        if (!connectorsContainer) {
            connectorsContainer = document.createElement('div');
            connectorsContainer.id = 'connectors-container';
            connectorsContainer.className = 'connectors-container';
            this.annualPlansContainer.appendChild(connectorsContainer);
        }
        return connectorsContainer;
    }

    getRelativeCoordinates(element, parentContainer) {
        const elementRect = element.getBoundingClientRect();
        const containerRect = parentContainer.getBoundingClientRect();

        return {
            top: elementRect.top - containerRect.top,
            left: elementRect.left - containerRect.left,
            bottom: elementRect.bottom - containerRect.top,
            right: elementRect.right - containerRect.left,
            width: elementRect.width,
            height: elementRect.height,
        };
    }

    createConnector(parentElement, childElement) {
        const connectorsContainer = this.ensureConnectorsContainer();
        const parentRibbon = parentElement.querySelector('.plan__ribbon');
        const childRibbon = childElement.querySelector('.plan__ribbon');

        if (!parentRibbon || !childRibbon) return;

        const parentCoords = this.getRelativeCoordinates(parentRibbon, connectorsContainer);
        const childCoords = this.getRelativeCoordinates(childRibbon, connectorsContainer);

        const startX = parentCoords.left + parentCoords.width / 2;
        const startY = parentCoords.bottom;
        const endX = childCoords.left;
        const endY = childCoords.top + childCoords.height / 2;

        const verticalConnector = document.createElement('div');
        verticalConnector.className = 'connector vertical-connector';
        verticalConnector.style.top = `${startY}px`;
        verticalConnector.style.left = `${startX}px`;
        verticalConnector.style.height = `${endY - startY}px`;

        const horizontalConnector = document.createElement('div');
        horizontalConnector.className = 'connector horizontal-connector';
        horizontalConnector.style.top = `${endY}px`;
        horizontalConnector.style.left = `${startX}px`;
        horizontalConnector.style.width = `${endX - startX}px`;

        connectorsContainer.appendChild(verticalConnector);
        connectorsContainer.appendChild(horizontalConnector);
    }

    updateConnectorsVisibility() {
        const connectorsContainer = document.getElementById('connectors-container');
        if (connectorsContainer) {
            if (this.isAnyCardExpanded) {
                connectorsContainer.classList.add('hidden');
            } else {
                setTimeout(() => {
                    connectorsContainer.classList.remove('hidden');
                }, 420);
            }
        }
    }

    renderAnnualPlan(plan, level = 0, parentElement = null) {
        const annualPlanNode = this.annualPlanTemplate.cloneNode(true);
        const annualPlanElement = annualPlanNode.querySelector('.plan__card');
        const quartersContainer = annualPlanElement.querySelector('.plan__quarters');

        annualPlanElement.style.marginLeft = `${level * 30}px`;
        annualPlanElement.style.width = `calc(100% - ${level * 30}px)`;
        annualPlanNode.querySelector('.plan__name').textContent = plan.equipment_name;
        annualPlanNode.querySelector('.plan__proposals').textContent = `${plan.completed_proposals} РП / ${plan.total_proposals} РП`;
        annualPlanNode.querySelector('.plan__economy').textContent = `${plan.sum_economy} тыс.руб. / ${plan.total_economy} тыс.руб.`;

        annualPlanElement.addEventListener('click', () => {
            if (quartersContainer.children.length === 0) {
                this.renderQuarterlyPlans(quartersContainer, plan.quarterly_plans);
            }
            annualPlanElement.classList.toggle('expanded');
            this.isAnyCardExpanded = document.querySelectorAll('.plan__card.expanded').length > 0;
            this.updateConnectorsVisibility();
        });

        this.annualPlansContainer.appendChild(annualPlanNode);

        if (parentElement) {
            this.createConnector(parentElement, annualPlanElement);
        }

        if (plan.children_plans && plan.children_plans.length > 0) {
            plan.children_plans.forEach(childPlan => {
                this.renderAnnualPlan(childPlan, level + 1, annualPlanElement);
            });
        }
    }

    renderQuarterlyPlans(container, quarterlyPlans) {
        quarterlyPlans.forEach(quarter => {
            const quarterlyPlanNode = this.quarterlyPlanTemplate.cloneNode(true);
            quarterlyPlanNode.querySelector('.quarter__number').textContent = `${quarter.quarter} кв.`;
            quarterlyPlanNode.querySelector('.quarter__proposals').textContent = `${quarter.completed_proposals} РП / ${quarter.planned_proposals} РП`;
            quarterlyPlanNode.querySelector('.quarter__economy').textContent = `${quarter.sum_economy} т.р. / ${quarter.planned_economy} т.р.`;
            container.appendChild(quarterlyPlanNode);
        });
    }
}
