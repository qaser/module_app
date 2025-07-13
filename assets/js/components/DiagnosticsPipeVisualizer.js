export default class SinglePipeVisualizer {
  constructor(pipe, containerId) {
    this.pipe = pipe;
    this.container = document.getElementById(containerId);
    this.svgNS = "http://www.w3.org/2000/svg";
    this.svg = document.createElementNS(this.svgNS, "svg");
    this.svg.setAttribute("width", "100%");
    this.svg.setAttribute("height", "200px");
    this.svg.setAttribute("background-color", "white");
    this.container.innerHTML = "";
    this.container.style.position = "relative";
    this.container.appendChild(this.svg);

    this.zoomScale = 1;
    this.minZoom = 1;
    this.offsetX = 0;
    this.offsetY = 0;
    this.zoomSpeed = 0.2;

    this.tubeCount = (this.pipe.pipe_units || []).filter(u => u.unit_type === 'tube').length;
    this.maxZoom = Math.max(10, this.tubeCount * 0.4); // Пример: 1000 → 400, 100 → 40

    this.pipeOutlineElement = null;

    this.setupZoom();
    this.setupPan();
    this.createResetButton();
    this.initTooltips();

    // центрируем при первой отрисовке
    this.centeredInitially = false;
    this.render();
  }

  initTooltips() {
    this.tooltip = document.createElement('div');
    this.tooltip.className = 'pipeline-tooltip';
    document.body.appendChild(this.tooltip);

    this.container.addEventListener('mouseover', (e) => {
      const target = e.target.closest('[data-tooltip]');
      if (target) {
        const tooltipText = target.getAttribute('data-tooltip');
        this.showTooltip(e, tooltipText);
      }
    });

    this.container.addEventListener('mouseout', () => {
      this.hideTooltip();
    });

    this.container.addEventListener('mousemove', (e) => {
      if (this.tooltip.style.display === 'block') {
        this.tooltip.style.left = `${e.pageX + 10}px`;
        this.tooltip.style.top = `${e.pageY + 10}px`;
      }
    });
  }

  showTooltip(e, text) {
    this.tooltip.textContent = text;
    this.tooltip.style.display = 'block';
    this.tooltip.style.left = `${e.pageX + 10}px`;
    this.tooltip.style.top = `${e.pageY + 10}px`;
  }

  hideTooltip() {
    this.tooltip.style.display = 'none';
  }

  setupZoom() {
    this.container.addEventListener('wheel', (e) => {
      e.preventDefault();
      const direction = e.deltaY > 0 ? -1 : 1;
      const factor = 1 + (this.zoomSpeed * direction);

      const rect = this.svg.getBoundingClientRect();
      const cursorX = e.clientX - rect.left;
    //   const cursorY = e.clientY - rect.top;

    //   const svgViewWidth = this.container.clientWidth;
    //   const svgViewHeight = 100;

      const newZoom = Math.min(this.maxZoom, Math.max(this.minZoom, this.zoomScale * factor));

      const scaleRatio = newZoom / this.zoomScale;
      this.offsetX = (this.offsetX + cursorX) * scaleRatio - cursorX;
      this.zoomScale = newZoom;

      this.render();
    });
  }

  setupPan() {
    let isDragging = false;
    let startX, startY;

    this.container.addEventListener('mousedown', (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
      this.container.style.cursor = 'grabbing';
    });

    this.container.addEventListener('mouseup', () => {
      isDragging = false;
      this.container.style.cursor = 'grab';
    });

    this.container.addEventListener('mouseleave', () => {
      isDragging = false;
      this.container.style.cursor = 'grab';
    });

    this.container.addEventListener('mouseenter', () => {
      this.container.style.cursor = 'grab';
    });

    this.container.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const dx = e.clientX - startX;
      const dy = e.clientY - startY;
      this.offsetX -= dx;
      this.offsetY -= dy;
      startX = e.clientX;
      startY = e.clientY;
      this.render();
    });
  }

  createResetButton() {
    const button = document.createElement("button");
    button.textContent = "⟳";
    button.style.position = "absolute";
    button.style.top = "10px";
    button.style.right = "10px";
    button.style.zIndex = 10;
    button.style.padding = "6px 10px";
    button.style.fontSize = "16px";
    button.style.cursor = "pointer";
    button.addEventListener("click", () => {
        this.zoomScale = 1;
        this.offsetX = 0;
        this.offsetY = 0;
        this.centeredInitially = false;
        this.render();
    });
    this.container.appendChild(button);
    }

  render() {
    this.svg.innerHTML = "";

    const units = this.pipe.pipe_units || [];
    const totalPipeLength = (this.pipe.end_point - this.pipe.start_point) * 1000;
    const showAll = this.zoomScale >= Math.max(1, this.tubeCount * 0.01);
    const showDefectDetails = this.zoomScale >= Math.max(5, this.tubeCount * 0.1);

 const totalUnitsLength = units.reduce((sum, unit) => {
      return unit.unit_type !== 'kss' && unit.length ? sum + unit.length : sum;
    }, 0);

    const containerWidth = this.container.clientWidth || 1000;
    const containerHeight = 100;
    const desiredWidth = containerWidth * 0.8 * this.zoomScale;
    const pixelsPerMeter = desiredWidth / totalPipeLength;

    let currentX = desiredWidth + 10;
    const y = 30;
    const height = 40;

    if (!this.centeredInitially) {
      this.offsetX = (desiredWidth - containerWidth) / 2;
      this.centeredInitially = true;
    }

    units.forEach((unit) => {
      if (unit.unit_type === 'kss') {
        const hasDefects = unit.defects && unit.defects.length > 0;
        if (showAll || hasDefects) {
          const line = document.createElementNS(this.svgNS, "rect");
          line.setAttribute("x", currentX);
          line.setAttribute("y", y);
          line.setAttribute("width", 1);
          line.setAttribute("height", height);
          line.setAttribute("fill", hasDefects ? "red" : "#000");
          this.svg.appendChild(line);
        }
        return;
      }

      const scaledLength = unit.length * pixelsPerMeter;
      const nextX = currentX - scaledLength;
      const hasDefects = unit.defects && unit.defects.length > 0;

      if (showAll || hasDefects) {
        const rect = document.createElementNS(this.svgNS, "rect");
        rect.setAttribute("x", nextX);
        rect.setAttribute("y", y);
        rect.setAttribute("width", scaledLength);
        rect.setAttribute("height", height);
        rect.setAttribute("fill", hasDefects ? "#f44336" : (unit.unit_type === 'tube' ? '#ffffff' : '#2196F3'));
        rect.setAttribute("stroke", "black");

        // Добавляем подсказку для трубы
        if (unit.unit_type === 'tube') {
          const defectsInfo = hasDefects
            ? `Дефекты: ${unit.defects.map(d => `${d.defect_type} (${d.position} м)`).join(', ')}`
            : 'Дефекты: нет';
          rect.setAttribute('data-tooltip',
            `Труба №${unit.tube_num}\n` +
            `Диаметр: ${unit.diameter} мм\n` +
            defectsInfo
          );
        }

        this.svg.appendChild(rect);

        if (showDefectDetails && hasDefects) {
          unit.defects.forEach(def => {
            if (def.position != null) {
              const defectX = nextX + scaledLength - (def.position * pixelsPerMeter);
              const mark = document.createElementNS(this.svgNS, "circle");
              mark.setAttribute("cx", defectX);
              mark.setAttribute("cy", y + height / 2);
              mark.setAttribute("r", 2);
              mark.setAttribute("fill", "black");
              this.svg.appendChild(mark);
            }
          });
        }
      }

      currentX = nextX;
    });

    this.pipeOutlineElement = document.createElementNS(this.svgNS, "rect");
    this.pipeOutlineElement.setAttribute("y", y);
    this.pipeOutlineElement.setAttribute("height", height);
    this.pipeOutlineElement.setAttribute("fill", "none");
    this.pipeOutlineElement.setAttribute("stroke", "black");
    this.svg.appendChild(this.pipeOutlineElement);

    this.pipeOutlineElement.setAttribute("x", 0);
    this.pipeOutlineElement.setAttribute("width", desiredWidth);
    this.pipeOutlineElement.style.display = 'inline';

    this.svg.setAttribute("viewBox", `${this.offsetX} ${this.offsetY} ${containerWidth} ${containerHeight}`);
  }
}
