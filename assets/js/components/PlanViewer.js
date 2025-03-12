export default class AnnualPlan {
    constructor(element) {
      this.element = element;
      this.header = element.querySelector('.annual-plan__header');
      this.quarters = element.querySelector('.annual-plan__quarters');
      this.planId = element.id.split('-')[2];

      this.header.addEventListener('click', () => this.toggle());
    }

    toggle() {
      if (this.element.classList.contains('expanded')) {
        this.collapse();
      } else {
        this.expand();
      }
    }

    expand() {
      this.element.classList.add('expanded');
      this.loadQuarters();
    }

    collapse() {
      this.element.classList.remove('expanded');
    }

    async loadQuarters() {
      if (this.quarters.children.length > 0) return;

      const response = await fetch(`/api/annual-plans/${this.planId}/quarters/`);
      const data = await response.json();

      data.forEach(quarter => {
        const quarterElement = document.createElement('div');
        quarterElement.classList.add('quarter');
        quarterElement.innerHTML = `
          <div class="quarter__number">Q${quarter.quarter}</div>
          <div class="quarter__stats">
            <div class="quarter__proposals">${quarter.completed_proposals} / ${quarter.planned_proposals}</div>
            <div class="quarter__economy">${quarter.sum_economy}₽ / ${quarter.planned_economy}₽</div>
          </div>
        `;
        this.quarters.appendChild(quarterElement);
      });
    }
  }
