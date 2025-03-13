export default class Chart {
    constructor(selector, totalProposals, completedProposals, totalEconomy, sumEconomy, size = 120, strokeWidth = 10) {
      this.container = document.querySelector(selector);
      this.totalProposals = totalProposals;
      this.completedProposals = completedProposals;
      this.totalEconomy = totalEconomy;
      this.sumEconomy = sumEconomy;
      this.size = size; // Размер SVG
      this.strokeWidth = strokeWidth; // Толщина внешнего круга
      this.innerStrokeWidth = strokeWidth * 0.7; // Толщина внутреннего круга
      this.radius = (size - strokeWidth) / 2;
      this.innerRadius = this.radius - (strokeWidth * 1.2);
      this.circumference = 2 * Math.PI * this.radius;
      this.proposalsPercent = this.calculatePercentage(completedProposals, totalProposals);
      this.economyPercent = this.calculatePercentage(sumEconomy, totalEconomy);
      this.render();
    }

    // Метод для вычисления процента выполнения
    calculatePercentage(value, total) {
      return total > 0 ? Math.round((value / total) * 100) : 0;
    }

    // Метод для создания SVG-круга
    createCircle(cx, cy, radius, stroke, percent, color) {
      const offset = this.circumference * (1 - percent / 100);
      const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      circle.setAttribute("cx", cx);
      circle.setAttribute("cy", cy);
      circle.setAttribute("r", radius);
      circle.setAttribute("fill", "none");
      circle.setAttribute("stroke", color);
      circle.setAttribute("stroke-width", stroke);
      circle.setAttribute("stroke-dasharray", `${this.circumference} ${this.circumference}`);
      circle.setAttribute("stroke-dashoffset", offset);
      circle.setAttribute("transform", `rotate(-90 ${this.size / 2} ${this.size / 2})`);
      circle.setAttribute("stroke-linecap", "round");
      return circle;
    }

    // Метод для создания текста с подсказкой
    createText(x, y, content, color, tooltipText) {
      const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
      text.setAttribute("x", x);
      text.setAttribute("y", y);
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("font-size", this.size * 0.12); // Уменьшил размер шрифта
      text.setAttribute("font-weight", "bold");
      text.setAttribute("fill", color);
      text.style.cursor = "pointer";
      text.textContent = content;
      // Создаём подсказку
      text.addEventListener("mouseenter", (e) => this.showTooltip(e, tooltipText));
      text.addEventListener("mouseleave", () => this.hideTooltip());
      return text;
    }

    // Показ подсказки
    showTooltip(event, text) {
      let tooltip = document.getElementById("donut-tooltip");
      if (!tooltip) {
        tooltip = document.createElement("div");
        tooltip.id = "donut-tooltip";
        tooltip.style.position = "absolute";
        tooltip.style.background = "rgba(0, 0, 0, 0.75)";
        tooltip.style.color = "#fff";
        tooltip.style.padding = "5px 10px";
        tooltip.style.borderRadius = "5px";
        tooltip.style.fontSize = "12px";
        tooltip.style.whiteSpace = "nowrap";
        tooltip.style.pointerEvents = "none";
        tooltip.style.opacity = "0";
        tooltip.style.transition = "opacity 0.2s";
        document.body.appendChild(tooltip);
      }

      tooltip.textContent = text;
      tooltip.style.left = `${event.pageX + 10}px`;
      tooltip.style.top = `${event.pageY - 20}px`;
      tooltip.style.opacity = "1";
    }

    // Скрытие подсказки
    hideTooltip() {
      const tooltip = document.getElementById("donut-tooltip");
      if (tooltip) tooltip.style.opacity = "0";
    }

    render() {
      if (!this.container) {
        console.error("Ошибка: контейнер не найден!");
        return;
      }

      // Создаём SVG-элемент
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("width", this.size);
      svg.setAttribute("height", this.size);
      svg.setAttribute("viewBox", `0 0 ${this.size} ${this.size}`);
      const center = this.size / 2;
      const textOffset = this.size * 0.08; // Смещение текста для адаптивности
      // Фоновые круги
      const bgProposals = this.createCircle(center, center, this.radius, this.strokeWidth, 100, "#e0e0e0");
      const bgEconomy = this.createCircle(center, center, this.innerRadius, this.innerStrokeWidth, 100, "#f0f0f0");
      // Круги с данными
      const proposalsCircle = this.createCircle(center, center, this.radius, this.strokeWidth, this.proposalsPercent, "#256CB8");
      const economyCircle = this.createCircle(center, center, this.innerRadius, this.innerStrokeWidth, this.economyPercent, "#247837");
      // Текстовые значения в центре (адаптивно смещены)
      const proposalsText = this.createText(center, center - textOffset, `${this.proposalsPercent}%`, "#256CB8", "Процент выполнения плана РП");
      const economyText = this.createText(center, center + textOffset, `${this.economyPercent}%`, "#247837", "Процент выполнения плана эк. эфф.");
      // Добавляем элементы в SVG
      svg.appendChild(bgProposals);
      svg.appendChild(bgEconomy);
      svg.appendChild(proposalsCircle);
      svg.appendChild(economyCircle);
      svg.appendChild(proposalsText);
      svg.appendChild(economyText);
      // Очищаем контейнер и вставляем диаграмму
      this.container.innerHTML = "";
      this.container.appendChild(svg);
    }
}
