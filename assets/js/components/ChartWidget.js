export default class ChartWidget {
  constructor(containerSelector, planData, type = 'annual') {
    this.container = document.querySelector(containerSelector);
    if (!this.container) {
      console.error('Контейнер не найден:', containerSelector);
      return;
    }

    this.planData = planData;
    this.type = type; // 'annual' или 'quarter'
    this.currentQuarter = this.getCurrentQuarter();

    this.render();
  }

  // Определение текущего квартала
  getCurrentQuarter() {
    const month = new Date().getMonth() + 1; // 1-12
    if (month >= 1 && month <= 3) return 1;
    if (month >= 4 && month <= 6) return 2;
    if (month >= 7 && month <= 9) return 3;
    return 4;
  }

  // Получение данных для отображения
  getDisplayData() {
    if (this.type === 'annual') {
      return {
        title: `Годовой план ${this.planData.year}`,
        totalProposals: this.planData.total_proposals,
        completedProposals: this.planData.completed_proposals || 0,
        totalEconomy: parseFloat(this.planData.total_economy) || 0,
        sumEconomy: parseFloat(this.planData.sum_economy) || 0,
        size: 140,
        strokeWidth: 12,
      };
    } else {
      const quarterData = this.planData.quarterly_plans?.find(
        (q) => q.quarter === this.currentQuarter
      );

      if (!quarterData) {
        return null;
      }

      return {
        title: `${this.getQuarterName(this.currentQuarter)} квартал ${this.planData.year}`,
        totalProposals: quarterData.planned_proposals,
        completedProposals: quarterData.completed_proposals || 0,
        totalEconomy: parseFloat(quarterData.planned_economy) || 0,
        sumEconomy: parseFloat(quarterData.sum_economy) || 0,
        size: 120,
        strokeWidth: 10,
      };
    }
  }

  // Расчет процента выполнения
  calculatePercentage(value, total) {
    return total > 0 ? Math.round((value / total) * 100) : 0;
  }

  // Создание SVG круговой диаграммы
  createDonutChart(data) {
    const { completedProposals, totalProposals, sumEconomy, totalEconomy, size, strokeWidth } =
      data;

    const proposalsPercent = this.calculatePercentage(completedProposals, totalProposals);
    const economyPercent = this.calculatePercentage(sumEconomy, totalEconomy);

    const radius = (size - strokeWidth) / 2;
    const innerRadius = radius - strokeWidth * 1.2;
    const circumference = 2 * Math.PI * radius;
    const center = size / 2;
    const textOffset = size * 0.08;

    // Создаем SVG
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', size);
    svg.setAttribute('height', size);
    svg.setAttribute('viewBox', `0 0 ${size} ${size}`);

    // Вспомогательная функция для создания круга
    const createCircle = (radius, strokeWidth, percent, color) => {
      const offset = circumference * (1 - percent / 100);
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('cx', center);
      circle.setAttribute('cy', center);
      circle.setAttribute('r', radius);
      circle.setAttribute('fill', 'none');
      circle.setAttribute('stroke', color);
      circle.setAttribute('stroke-width', strokeWidth);
      circle.setAttribute('stroke-dasharray', `${circumference} ${circumference}`);
      circle.setAttribute('stroke-dashoffset', offset);
      circle.setAttribute('transform', `rotate(-90 ${center} ${center})`);
      circle.setAttribute('stroke-linecap', 'round');
      return circle;
    };

    // Фоновые круги
    const bgProposals = createCircle(radius, strokeWidth, 100, '#e0e0e0');
    const bgEconomy = createCircle(innerRadius, strokeWidth * 0.7, 100, '#f0f0f0');

    // Круги с данными
    const proposalsCircle = createCircle(radius, strokeWidth, proposalsPercent, '#256CB8');
    const economyCircle = createCircle(innerRadius, strokeWidth * 0.7, economyPercent, '#247837');

    // Создание текста
    const createText = (yOffset, content, color, tooltipText) => {
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', center);
      text.setAttribute('y', yOffset);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('font-size', size * 0.12);
      text.setAttribute('font-weight', 'bold');
      text.setAttribute('fill', color);
      text.style.cursor = 'pointer';
      text.textContent = content;

      // Подсказка
      text.addEventListener('mouseenter', (e) => this.showTooltip(e, tooltipText));
      text.addEventListener('mouseleave', () => this.hideTooltip());

      return text;
    };

    const proposalsText = createText(
      center - textOffset,
      `${proposalsPercent}%`,
      '#256CB8',
      'Процент выполнения плана РП'
    );
    const economyText = createText(
      center + textOffset,
      `${economyPercent}%`,
      '#247837',
      'Процент выполнения плана эк. эфф.'
    );

    // Собираем SVG
    svg.appendChild(bgProposals);
    svg.appendChild(bgEconomy);
    svg.appendChild(proposalsCircle);
    svg.appendChild(economyCircle);
    svg.appendChild(proposalsText);
    svg.appendChild(economyText);

    return svg;
  }

  // Показ подсказки
  showTooltip(event, text) {
    let tooltip = document.getElementById('chart-tooltip');
    if (!tooltip) {
      tooltip = document.createElement('div');
      tooltip.id = 'chart-tooltip';
      tooltip.style.position = 'absolute';
      tooltip.style.background = 'rgba(0, 0, 0, 0.75)';
      tooltip.style.color = '#fff';
      tooltip.style.padding = '5px 10px';
      tooltip.style.borderRadius = '5px';
      tooltip.style.fontSize = '12px';
      tooltip.style.whiteSpace = 'nowrap';
      tooltip.style.pointerEvents = 'none';
      tooltip.style.opacity = '0';
      tooltip.style.transition = 'opacity 0.2s';
      tooltip.style.zIndex = '1000';
      document.body.appendChild(tooltip);
    }

    tooltip.textContent = text;
    tooltip.style.left = `${event.pageX + 10}px`;
    tooltip.style.top = `${event.pageY - 20}px`;
    tooltip.style.opacity = '1';
  }

  // Скрытие подсказки
  hideTooltip() {
    const tooltip = document.getElementById('chart-tooltip');
    if (tooltip) tooltip.style.opacity = '0';
  }

  // Создание контейнера для диаграммы с заголовком
  createChartContainer(title, chart) {
    const container = document.createElement('div');
    container.className = 'chart__item';

    // Заголовок
    const titleElement = document.createElement('div');
    titleElement.className = 'chart__title';
    titleElement.textContent = title;

    container.appendChild(titleElement);
    container.appendChild(chart);

    return container;
  }

  render() {
    const data = this.getDisplayData();

    if (!data) {
      // Показываем заглушку если нет данных
      const placeholder = document.createElement('div');
      placeholder.className = 'chart__item';
      placeholder.style.display = 'flex';
      placeholder.style.alignItems = 'center';
      placeholder.style.justifyContent = 'center';
      placeholder.style.minHeight = '150px';
      placeholder.style.background = '#f5f5f5';
      placeholder.style.borderRadius = '8px';
      placeholder.style.color = '#999';
      placeholder.style.fontSize = '14px';
      placeholder.style.padding = '20px';
      placeholder.textContent = 'Нет данных по текущему кварталу';

      this.container.appendChild(placeholder);
      return;
    }

    // Создаем диаграмму
    const chart = this.createDonutChart(data);

    // Создаем контейнер с заголовком
    const chartContainer = this.createChartContainer(data.title, chart);

    // Очищаем и добавляем в основной контейнер
    this.container.innerHTML = '';
    this.container.appendChild(chartContainer);
  }

  // Получение названия квартала
  getQuarterName(quarter) {
    const quarters = {
      1: 'I',
      2: 'II',
      3: 'III',
      4: 'IV',
    };
    return quarters[quarter] || quarter;
  }
}
