export default class PipelineVisualizer {
    constructor(containerId, contextMenu, popupPipeChange, popupNodeChange, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            pipelinePadding: 40,
            pipelineHeight: 8,
            pipelineMargin: 60,
            pipeColor: '#4a89dc',
            valveColor: '#e9573f',
            connectionColor: '#37bc9b',
            bridgeColor: '#967adc',
            hostColor: '#8cc152',
            emptyPipeColor: '#ffffff',
            emptyPipeStroke: '#c0c0c0',
            valveOpenColor: '#00FF00',
            valveClosedColor: '#FF0000',
            valveDefaultColor: '#808080',
            bridgePipeOpenColor: '#00FF00',
            bridgePipeClosedColor: '#808080',
            ...options
        };
        this.popupPipeChange = popupPipeChange;
        this.popupNodeChange = popupNodeChange;
        this.scale = 1.0;
        this.offsetX = 0;
        this.offsetY = 0;
        this.contextMenu = contextMenu;
        this.initZoom();
        this.createResetButton();
        this.initTooltips();
    }

    initTooltips() {
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'pipeline-tooltip';
        document.body.appendChild(this.tooltip);

        this.container.addEventListener('mouseover', (e) => {
            const target = e.target.closest('.pipe-element, .node-element');
            if (target && target.hasAttribute('data-tooltip')) {
                const tooltipText = target.getAttribute('data-tooltip');
                this.showTooltip(e, tooltipText);
            }
        });

        this.container.addEventListener('mouseout', (e) => {
            if (e.target.closest('.pipe-element, .node-element')) {
                this.hideTooltip();
            }
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

    render(pipelinesData) {
        this.pipelines = pipelinesData
        this.container.innerHTML = '';

        const screenWidth = window.innerWidth;
        const fixedWidth = 1500;

        if (screenWidth < fixedWidth) {
            this.container.style.width = `${fixedWidth}px`;
            this.container.style.overflowX = 'auto';
        } else {
            this.container.style.width = '100%';
        }

        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute('width', '100%');
        svg.setAttribute('height', this.calculateTotalHeight(pipelinesData));

        pipelinesData.forEach((pipeline, index) => {
            pipeline.totalLength = this.calculatePipelineLength(pipeline);
            const pipelineGroup = this.createPipelineGroup(pipeline, index, pipelinesData.length);
            svg.appendChild(pipelineGroup);
        });

        this.container.appendChild(svg);
        this.svg = svg
        this.applyTransform();
        this.createResetButton();
        this.addClickHandlers();
    }

    addClickHandlers() {
        this.container.addEventListener('click', (e) => {
            const target = e.target.closest('.pipe-element, .node-element');
            if (!target) {
                this.contextMenu.close();
                return;
            }
            e.preventDefault();
            e.stopPropagation();
            const isPipe = target.classList.contains('pipe-element');
            const id = target.getAttribute(isPipe ? 'pipe-id' : 'node-id');
            const type = isPipe ? 'pipe' : 'node';
            this.selectedElement = {
                type,
                id: parseInt(id),
            };

            if (this.tooltip) {
                this.hideTooltip();
            }

            const menuItems = [
                {
                    text: 'Сменить состояние',
                    action: () => {
                        if (type === 'pipe') {
                            this.popupPipeChange.open();
                        } else {
                            this.popupNodeChange.open();
                        }
                    }
                },
                {
                    text: 'Подробный обзор',
                    action: () => this.openDetailsPopup(type, id)
                }
            ];
            this.contextMenu.open(e, menuItems);
        });
    }

    getSelectedElement() {
        return this.selectedElement || null;
    }

    openDetailsPopup(type, id) {
        window.location.href = type + 's/' + id + '/'
    }

    calculatePipelineLength(pipeline) {
        if (!pipeline.pipes || pipeline.pipes.length === 0) return 0;
        const minPoint = Math.min(...pipeline.pipes.map(pipe => pipe.start_point));
        const maxPoint = Math.max(...pipeline.pipes.map(pipe => pipe.end_point));
        return maxPoint - minPoint;
    }

    calculateTotalHeight(pipelinesData) {
        return pipelinesData.length * (this.options.pipelineHeight + this.options.pipelineMargin) + this.options.pipelineMargin;
    }

    createPipelineGroup(pipeline, index, total) {
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");

        const yPos = (total - 1 - index) * (this.options.pipelineHeight + this.options.pipelineMargin) + this.options.pipelineMargin;

        const containerWidth = this.container.clientWidth;
        const availableWidth = containerWidth - 2 * this.options.pipelinePadding;
        const pipeWidth = availableWidth / (pipeline.pipes.length + 2); // +2 for empty pipes

        const [startEmptyPipe, startArrow] = this.createEmptyPipeElement(pipeline.pipes.length, yPos, pipeWidth);
        group.appendChild(startEmptyPipe);
        group.appendChild(startArrow);

        const startCity = pipeline.title.split(' - ')[0];
        const startLabel = this.createCityLabel(startCity,
            containerWidth - this.options.pipelinePadding - pipeWidth,
            yPos - 5,
            pipeWidth);
        group.appendChild(startLabel);

        pipeline.pipes.forEach((pipe, idx) => {
            const pipeElement = this.createPipeElement(pipeline.title, pipe, yPos, idx, pipeWidth);
            group.appendChild(pipeElement);
        });

        const [endEmptyPipe, endArrow] = this.createEmptyPipeElement(-1, yPos, pipeWidth);
        group.appendChild(endEmptyPipe);
        group.appendChild(endArrow);

        const endCity = pipeline.title.split(' - ')[1] || '';
        const endLabel = this.createCityLabel(endCity,
            this.options.pipelinePadding,
            yPos - 5,
            pipeWidth);
        group.appendChild(endLabel);

        pipeline.nodes.forEach(node => {
            const nodeElement = this.createNodeElement(pipeline.title, node, yPos, pipeline, pipeWidth);
            if (nodeElement) {
                group.appendChild(nodeElement);
            }
        });

        return group;
    }

    createEmptyPipeElement(index, yPos, pipeWidth) {
        const element = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        const x = this.container.clientWidth - this.options.pipelinePadding - (index + 2) * pipeWidth;

        element.setAttribute('x', x);
        element.setAttribute('y', yPos);
        element.setAttribute('width', pipeWidth);
        element.setAttribute('height', this.options.pipelineHeight);
        element.setAttribute('fill', this.options.emptyPipeColor);
        element.setAttribute('stroke', this.options.emptyPipeStroke);
        element.setAttribute('stroke-width', '0.5');
        element.classList.add('empty-pipe-element');

        const arrowGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        arrowGroup.setAttribute('transform', `translate(${x + pipeWidth/2}, ${yPos - 5})`);

        const arrowShape = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
        arrowShape.setAttribute("points", "0 0, -7 2.5, 0 5");
        arrowShape.setAttribute('transform', 'translate(0, 18)');
        arrowShape.setAttribute("fill", "gray");

        const arrowRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        arrowRect.setAttribute('x', '0');
        arrowRect.setAttribute('y', '20.5');
        arrowRect.setAttribute('width', '15');
        arrowRect.setAttribute('height', '0.5');
        arrowRect.setAttribute('fill', 'gray');

        arrowGroup.appendChild(arrowShape);
        arrowGroup.appendChild(arrowRect);

        return [element, arrowGroup];
    }

    createCityLabel(cityName, x, y, width) {
        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute('x', x + width/2);
        text.setAttribute('y', y);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '10px');
        text.setAttribute('fill', '#333');
        text.textContent = cityName;
        return text;
    }

    createPipeElement(pipeline_title, pipe, yPos, index, pipeWidth) {
    const svgNS = "http://www.w3.org/2000/svg";

    // Главный контейнер для всех элементов
    const mainGroup = document.createElementNS(svgNS, "g");
    mainGroup.classList.add('main-pipe-group');

    // Создаем группу для pipe (как у вас было)
    const group = document.createElementNS(svgNS, "g");
    group.classList.add('pipe-group');

    const x = this.container.clientWidth - this.options.pipelinePadding - (index + 2) * pipeWidth;
    const rect = document.createElementNS(svgNS, "rect");
        rect.setAttribute('x', x);
        rect.setAttribute('y', yPos);
        rect.setAttribute('width', pipeWidth);
        rect.setAttribute('height', this.options.pipelineHeight);
        rect.setAttribute('fill', pipe.state?.color || this.options.pipeColor);
        if (pipe.limit) {
            rect.setAttribute('stroke', '#8B0000');
        }
        rect.classList.add('pipe-element');
        rect.setAttribute('pipe-id', pipe.id);

        let departmentInfo = '';
        let separator = null;

        if (Array.isArray(pipe.departments)) {
            if (pipe.departments.length === 1) {
                departmentInfo = `Филиал: ${pipe.departments[0].name}`;
            } else {
                departmentInfo = pipe.departments.map(dep => {
                    return `Филиал: ${dep.name} от ${dep.start_point} до ${dep.end_point} км.`;
                }).join('\n');
                separator = document.createElementNS(svgNS, 'line');
                const centerX = x + pipeWidth / 2;
                separator.setAttribute('x1', centerX);
                separator.setAttribute('x2', centerX);
                separator.setAttribute('y1', yPos - 30);
                separator.setAttribute('y2', yPos + this.options.pipelineHeight + 30);
                separator.setAttribute('stroke', 'red');
                separator.setAttribute('stroke-width', '1');
                separator.setAttribute('stroke-dasharray', '4,2');
                separator.classList.add('pipe-separator-line');
            }
        }

        if (pipe.state) {
            rect.setAttribute('data-tooltip',
                `${departmentInfo}\n` +
                `Газопровод: ${pipeline_title}\n` +
                `Участок: ${pipe.start_point.toFixed(1)} - ${pipe.end_point.toFixed(1)} км.\n` +
                `Диаметр: ${pipe.diameter} мм\n` +
                `Состояние: ${pipe.state.state_type_display} c ${pipe.state.start_date}г.\n` +
                `Ограничение: ${pipe.limit ? pipe.limit.pressure_limit.toFixed(1) + ' кгс/см²' : 'Нет'}`
            );
        }

        group.appendChild(rect);
        if (separator) {
            group.appendChild(separator);
        }
        if (pipe.limit) {
            // Создаем фон для текста (прямоугольник)
            const textBg = document.createElementNS(svgNS, "rect");
            textBg.setAttribute('x', x + pipeWidth / 2 - 20); // Центрируем и добавляем отступы
            textBg.setAttribute('y', yPos - 25); // Позиционируем выше pipe
            textBg.setAttribute('width', 40); // Ширина фона
            textBg.setAttribute('height', 20); // Высота фона
            textBg.setAttribute('rx', 3); // Закругленные углы
            textBg.setAttribute('fill', '#8B0000'); // Темно-красный цвет
            textBg.setAttribute('class', 'limit-text-bg');

            // Создаем текст
            const text = document.createElementNS(svgNS, "text");
            text.setAttribute('x', x + pipeWidth / 2); // Центрируем по ширине pipe
            text.setAttribute('y', yPos - 10); // Размещаем над pipe
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', '12px');
            text.setAttribute('fill', 'white'); // Белый текст
            text.setAttribute('font-weight', 'bold');
            text.setAttribute('class', 'pipe-limit-text');
            text.textContent = pipe.limit.pressure_limit;

            // Добавляем элементы в правильном порядке (сначала фон, потом текст)
            mainGroup.appendChild(textBg);
            mainGroup.appendChild(text);
        }
        mainGroup.appendChild(group);
        return mainGroup; // Возвращаем основной контейнер
    }

    createNodeElement(pipeline_title, node, yPos, pipeline, pipeWidth) {
        const containerWidth = this.container.clientWidth;
        const availableWidth = containerWidth - 2 * this.options.pipelinePadding;
        const pipes = pipeline.pipes;
        let x = null;
        const offsetMultiplier = 0.75;
        if (node.node_type === 'bridge') {
            const pipe = pipes.find(p => node.location_point >= p.start_point && node.location_point <= p.end_point);
            if (!pipe) return null;
            const pipeIndex = pipes.indexOf(pipe);
            const localPercent = (node.location_point - pipe.start_point) / (pipe.end_point - pipe.start_point);
            const innerOffset = offsetMultiplier + localPercent * (1 - 2 * offsetMultiplier);
            // Adjust pipeIndex by +1 because of the empty pipe at start
            const pipeStartX = containerWidth - this.options.pipelinePadding - (pipeIndex + 2) * pipeWidth;
            x = pipeStartX + innerOffset * pipeWidth;
        } else if (node.node_type === 'valve' || node.node_type === 'host') {
            const boundaryPipe = pipes.find((p, idx) => {
                const isStart = Math.abs(node.location_point - p.start_point) < 0.001;
                const isEnd = Math.abs(node.location_point - p.end_point) < 0.001;
                return isStart || isEnd;
            });
            if (!boundaryPipe) return null;
            const pipeIndex = pipes.indexOf(boundaryPipe);
            const isEnd = Math.abs(node.location_point - boundaryPipe.end_point) < 0.001;
            const offset = isEnd ? 1 : 0;
            x = containerWidth - this.options.pipelinePadding - (pipeIndex + offset + 1) * pipeWidth;
        }
        if (x === null) return null;
        const y = yPos + this.options.pipelineHeight / 2;
        const size = this.options.pipelineHeight * 4;
        let element;
        switch(node.node_type) {
            case 'valve':
                element = this.createValveElement(node, x, y, size);
                break;
            case 'host':
                element = this.createHostElement(node, x, y, size);
                break;
            case 'bridge':
                element = this.createBridgeElement(node, x, y, size);
                break;
            default:
                return null;
        }
        element.setAttribute('node-id', node.id);
        element.classList.add('node-element');
        element.setAttribute('data-tooltip',
            `Филиал: ${node.department.name}\n` +
            `Газопровод: ${pipeline_title}\n` +
            `${node.node_type_display}: ${node.location_point.toFixed(2)} км.\n` +
            `Состояние: ${node.state ? node.state.state_display : 'Неизвестно'}`);
        return element;
    }

    createValveIcon(valveStateColor = '#00FF00', size = 'medium', orientation = 'horizontal') {
        const sizes = {
            large: 1.0,
            medium: 0.6,
            small: 0.4
        };
        const scale = sizes[size] || 0.6;
        const rotation = orientation === 'vertical' ? 90 : 0;
        const namespace = "http://www.w3.org/2000/svg";
        const svg = document.createElementNS(namespace, 'svg');
        svg.setAttribute('xmlns', namespace);
        svg.setAttribute('width', 20 * scale);
        svg.setAttribute('height', 20 * scale);
        svg.setAttribute('viewBox', '138 192 6 6');
        svg.setAttribute('transform', `scale(${scale}) rotate(${rotation})`);
        svg.innerHTML = `
            <g>
            <!-- Левая закрашиваемая часть -->
            <path
                d="m 141.11221,194.74054 -1.26917,0.73276 -1.26917,0.73276 v -1.46552 -1.46551 l 1.26917,0.73276 z"
                class="valve-fill"
                style="fill:${valveStateColor};stroke:#000000;stroke-width:0.1;stroke-linecap:round;" />

            <!-- Правая закрашиваемая часть -->
            <path
                d="m 141.11221,194.74054 1.26917,0.73276 1.26917,0.73276 v -1.46552 -1.46551 l -1.26917,0.73276 z"
                class="valve-fill"
                style="fill:${valveStateColor};stroke:#000000;stroke-width:0.1;stroke-linecap:round;" />

            <!-- Верхняя белая маска -->
            <path
                d="m 141.11221,194.70326 -1.27263,-0.74424 -1.27263,-0.74423 h 2.54526 2.54525 l -1.27263,0.74423 z"
                class="valve-mask"
                style="fill:#F8F8F8;stroke:none;" />

            <!-- Нижняя белая маска -->
            <path
                d="m 141.11221,194.77303 -1.27263,0.74171 -1.27263,0.74171 h 2.54526 2.54525 l -1.27263,-0.74171 z"
                class="valve-mask"
                style="fill:#F8F8F8;stroke:none;" />
            </g>
        `;

        return svg;
    }

    createValveElement(node, x, y, size) {
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        const scale = size / 20;
        group.setAttribute('transform', `translate(${x - 10 * scale}, ${y - 10 * scale}) scale(${scale})`);
        const getValveColor = () => {
            if (!node.state) return this.options.valveDefaultColor;

            return node.state.state_type === 'open'
                ? this.options.valveOpenColor
                : this.options.valveClosedColor;
        };
        const leftVerticalPipe = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        leftVerticalPipe.setAttribute('x', '-3');
        leftVerticalPipe.setAttribute('y', '-2');
        leftVerticalPipe.setAttribute('width', '0.75');
        leftVerticalPipe.setAttribute('height', '10');
        leftVerticalPipe.setAttribute('fill', this.options.pipeColor);

        const rightVerticalPipe = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rightVerticalPipe.setAttribute('x', '23');
        rightVerticalPipe.setAttribute('y', '-12');
        rightVerticalPipe.setAttribute('width', '0.75');
        rightVerticalPipe.setAttribute('height', '20');
        rightVerticalPipe.setAttribute('fill', this.options.pipeColor);

        const horizontalPipe = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        horizontalPipe.setAttribute('x', '-2');
        horizontalPipe.setAttribute('y', '-24');
        horizontalPipe.setAttribute('width', '0.75');
        horizontalPipe.setAttribute('height', '27');
        horizontalPipe.setAttribute('transform', 'rotate(90)');
        horizontalPipe.setAttribute('fill', this.options.pipeColor);

        const mainValveColor = getValveColor();
        const mainValveIcon = this.createValveIcon(mainValveColor, 'large', 'horizontal');
        mainValveIcon.setAttribute('transform', `translate(0, 1)`);

        const bypassLeft = this.createValveIcon(this.options.valveDefaultColor, 'small', 'vertical');
        bypassLeft.setAttribute('transform', 'scale(0.8) rotate(90) translate(0, -0.5)');

        const bypassRight = this.createValveIcon(this.options.valveDefaultColor, 'small', 'vertical');
        bypassRight.setAttribute('transform', 'scale(0.8) rotate(90) translate(0, -33)');

        const bypassBleed = this.createValveIcon(this.options.valveDefaultColor, 'small', 'vertical');
        bypassBleed.setAttribute('transform', 'scale(0.8) rotate(90) translate(-12, -33)');

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute('x', 10);
        text.setAttribute('y', 23);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '7px');
        text.setAttribute('fill', '#333');
        text.textContent = node.location_point.toFixed(1);

        group.appendChild(leftVerticalPipe);
        group.appendChild(rightVerticalPipe);
        group.appendChild(horizontalPipe);
        group.appendChild(mainValveIcon);
        group.appendChild(bypassLeft);
        group.appendChild(bypassRight);
        group.appendChild(bypassBleed);
        group.appendChild(text);

        return group;
    }

    createHostElement(node, x, y, size) {
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
        const scale = size / 20;
        group.setAttribute('transform', `translate(${x - 10 * scale}, ${y - 10 * scale}) scale(${scale})`);
        const getValveColor = () => {
            if (!node.state) return this.options.valveDefaultColor;

            return node.state.state_type === 'open'
                ? this.options.valveOpenColor
                : this.options.valveClosedColor;
        };
        const perimetrHost = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        perimetrHost.setAttribute('x', '-20');
        perimetrHost.setAttribute('y', '-5');
        perimetrHost.setAttribute('width', '60');
        perimetrHost.setAttribute('height', '30');
        perimetrHost.setAttribute('fill', 'none');
        perimetrHost.setAttribute('stroke', 'gray');
        perimetrHost.setAttribute('stroke-dasharray', '1,2');
        const mainValveColor = getValveColor();
        const mainValveIcon = this.createValveIcon(mainValveColor, 'large', 'horizontal');
        mainValveIcon.setAttribute('transform', 'scale(1) translate(0, 1)');

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute('x', 10);
        text.setAttribute('y', 23);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('font-size', '7px');
        text.setAttribute('fill', '#333');
        text.textContent = node.location_point;

        group.appendChild(mainValveIcon);
        group.appendChild(perimetrHost);
        group.appendChild(text);

        return group;
    }

    createBridgeElement(node, x, y, size) {
        const group = document.createElementNS("http://www.w3.org/2000/svg", "g");

        const scale = size / 20;
        group.setAttribute('transform', `translate(${x - 10 * scale}, ${y - 10 * scale}) scale(${scale})`);
        const isValveOpen = node.state?.state_type === 'open';
        const bridgePipeColor = isValveOpen
            ? this.options.bridgePipeOpenColor
            : this.options.bridgePipeClosedColor;
        const getValveColor = () => {
            if (!node.state) return this.options.valveDefaultColor;

            return node.state.state_type === 'open'
                ? this.options.valveOpenColor
                : this.options.valveClosedColor;
        };
        const bridgePipe = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        bridgePipe.setAttribute('x', '9');
        bridgePipe.setAttribute('y', '-30');
        bridgePipe.setAttribute('width', '2.5');
        bridgePipe.setAttribute('height', '38');
        bridgePipe.setAttribute('fill', bridgePipeColor);
        bridgePipe.classList.add('main-bridge-pipe');

        const topHorizontalPipe = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        topHorizontalPipe.setAttribute('x', '10');
        topHorizontalPipe.setAttribute('y', '-3');
        topHorizontalPipe.setAttribute('width', '7');
        topHorizontalPipe.setAttribute('height', '0.75');
        topHorizontalPipe.setAttribute('fill', this.options.pipeColor);

        const bottomHorizontalPipe = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        bottomHorizontalPipe.setAttribute('x', '10');
        bottomHorizontalPipe.setAttribute('y', '-18');
        bottomHorizontalPipe.setAttribute('width', '7');
        bottomHorizontalPipe.setAttribute('height', '0.75');
        bottomHorizontalPipe.setAttribute('fill', this.options.pipeColor);

        const verticalPipe = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        verticalPipe.setAttribute('x', '17');
        verticalPipe.setAttribute('y', '-18');
        verticalPipe.setAttribute('width', '0.75');
        verticalPipe.setAttribute('height', '15.7');
        verticalPipe.setAttribute('fill', this.options.pipeColor);
        const mainValveColor = getValveColor();
        const mainValveIcon = this.createValveIcon(mainValveColor, 'large', 'vertical');
        mainValveIcon.setAttribute('transform', 'scale(0.6) rotate(90) translate(-27, -26)');

        const bypassValve = this.createValveIcon(this.options.valveDefaultColor, 'small', 'vertical');
        bypassValve.setAttribute('transform', 'scale(0.8) rotate(90) translate(-17, -25.2)');

        group.appendChild(bridgePipe);
        group.appendChild(topHorizontalPipe);
        group.appendChild(bottomHorizontalPipe);
        group.appendChild(verticalPipe);
        group.appendChild(mainValveIcon);
        group.appendChild(bypassValve);

        return group;
    }

    initZoom() {
        let isDragging = false;
        let startX, startY;

        this.container.addEventListener('wheel', (e) => {
            e.preventDefault();
            const rect = this.container.getBoundingClientRect();
            // Координаты указателя относительно контейнера
            const pointerX = e.clientX - rect.left;
            const pointerY = e.clientY - rect.top;
            const oldScale = this.scale;
            const delta = e.deltaY > 0 ? -0.2 : 0.2;
            this.scale = Math.min(Math.max(0.5, this.scale + delta), 3.0);
            // Коррекция offsetX и offsetY, чтобы масштабирование было относительно указателя мыши
            this.offsetX -= (pointerX / oldScale - pointerX / this.scale);
            this.offsetY -= (pointerY / oldScale - pointerY / this.scale);
            this.applyTransform();
        });

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

            this.offsetX += dx;
            this.offsetY += dy;

            startX = e.clientX;
            startY = e.clientY;

            this.applyTransform();
        });
    }

    applyTransform() {
        const svg = this.container.querySelector('svg');
        if (svg) {
            svg.style.transform = `scale(${this.scale}) translate(${this.offsetX}px, ${this.offsetY}px)`;
            svg.style.transformOrigin = '0 0';
        }
    }

    createResetButton() {
        const button = document.createElement('button');
        button.textContent = '⟳';
        button.style.position = 'absolute';
        button.style.top = '10px';
        button.style.right = '10px';
        button.style.zIndex = 1000;
        button.addEventListener('click', () => {
            this.scale = 1.0;
            this.offsetX = 0;
            this.offsetY = 0;
            this.applyTransform();
        });
        this.container.style.position = 'relative';
        this.container.appendChild(button);
    }
}
