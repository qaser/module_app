export default class SinglePipeVisualizer {
  constructor(tubes, containerId) {
    this.tubes = tubes;
    this.container = document.getElementById(containerId);

    this.zoomLevel = 1;
    this.initialZoomLevel = 1;
    this.offsetX = 0;
    this.offsetY = 0;
    this.dragging = false;
    this.startX = 0;
    this.startY = 0;

    this.TUBE_HEIGHT = 20;
    this.TUBE_GAP = 2; // увеличен для видимого белого зазора
    this.SCALE_FACTOR = 5;

    this.MIN_ZOOM = 0.1;
    this.MAX_ZOOM = 5;
  }

  render() {
    this.container.innerHTML = "";
    this.container.style.position = "relative";
    this.container.style.backgroundColor = "#fff";

    this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    this.svg.setAttribute("width", "100%");
    this.svg.setAttribute("height", "100%");
    this.svg.style.display = "block";
    this.svg.style.cursor = "grab";

    this.container.appendChild(this.svg);

    this.tubeGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
    this.svg.appendChild(this.tubeGroup);

    this.svg.addEventListener("wheel", (e) => this.onZoom(e));
    this.svg.addEventListener("mousedown", (e) => this.onMouseDown(e));
    this.svg.addEventListener("mousemove", (e) => this.onMouseMove(e));
    this.svg.addEventListener("mouseup", () => this.onMouseUp());
    this.svg.addEventListener("mouseleave", () => this.onMouseUp());

    this.drawTubes();
    this.fitToContainer();
    this.createResetButton();
  }

    drawTubes() {
        this.tubeGroup.innerHTML = "";

        const reversed = [...this.tubes].reverse(); // труба №1 — слева
        let x = 0;

        for (let tube of reversed) {
            const width = tube.tube_length * this.SCALE_FACTOR;

            const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("x", x);
            rect.setAttribute("y", 0);
            rect.setAttribute("width", width);
            rect.setAttribute("height", this.TUBE_HEIGHT);
            rect.setAttribute("fill", "#a5c8f5"); // светлая заливка
            rect.setAttribute("stroke", "black"); // чёрная обводка
            rect.setAttribute("stroke-width", 0.5);
            rect.setAttribute("data-id", tube.id);
            rect.setAttribute("data-tooltip",
            `Труба №${tube.tube_num}\nДиаметр: ${tube.diameter} мм\nТолщина: ${tube.thickness} мм\nДлина: ${tube.tube_length} м\nТип трубы: ${tube.tube_type}`);
            rect.style.cursor = "pointer";

            rect.addEventListener("mouseenter", () => {
            rect.setAttribute("fill", "#c4dbf8");
            });
            rect.addEventListener("mouseleave", () => {
            rect.setAttribute("fill", "#a5c8f5");
            });

            this.tubeGroup.appendChild(rect);
            x += width + this.TUBE_GAP; // белый зазор между трубами создаётся отступом
        }

        this.totalWidth = x;
    }


  fitToContainer() {
    const containerRect = this.container.getBoundingClientRect();
    const padding = 40;
    const availableWidth = containerRect.width - padding * 2;

    this.initialZoomLevel = availableWidth / this.totalWidth;
    this.initialZoomLevel = Math.min(this.initialZoomLevel, 1);
    this.zoomLevel = this.initialZoomLevel;

    this.offsetX = (containerRect.width - this.totalWidth * this.zoomLevel) / 2;
    this.offsetY = (containerRect.height - this.TUBE_HEIGHT) / 2;

    this.updateTransform();
  }

  updateTransform() {
    this.tubeGroup.setAttribute(
      "transform",
      `translate(${this.offsetX}, ${this.offsetY}) scale(${this.zoomLevel}, 1)`
    );
  }

  onZoom(event) {
    event.preventDefault();
    const rect = this.svg.getBoundingClientRect();
    const cursorX = event.clientX - rect.left;

    const zoomFactor = event.deltaY < 0 ? 1.1 : 0.9;
    const prevZoom = this.zoomLevel;
    const newZoom = Math.max(this.initialZoomLevel, Math.min(this.MAX_ZOOM, this.zoomLevel * zoomFactor));
    const zoomRatio = newZoom / prevZoom;

    this.offsetX = cursorX - (cursorX - this.offsetX) * zoomRatio;
    this.zoomLevel = newZoom;

    this.updateTransform();
  }

  onMouseDown(event) {
    this.dragging = true;
    this.startX = event.clientX;
    this.startY = event.clientY;
    this.svg.style.cursor = "grabbing";
  }

  onMouseMove(event) {
    if (!this.dragging) return;
    const dx = event.clientX - this.startX;
    const dy = event.clientY - this.startY;
    this.startX = event.clientX;
    this.startY = event.clientY;
    this.offsetX += dx;
    this.offsetY += dy;
    this.updateTransform();
  }

  onMouseUp() {
    this.dragging = false;
    this.svg.style.cursor = "grab";
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
      this.fitToContainer();
    });

    this.container.appendChild(button);
  }
}
