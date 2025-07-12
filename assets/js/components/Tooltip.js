export default class Tooltip {
    constructor() {
        this.tooltipElement = document.createElement('div');
        this.tooltipElement.className = 'tooltip';
        this.tooltipElement.innerHTML = `
            <div class='tooltip-glass'>
                <div class='tooltip-content'></div>
            </div>
            <div class='tooltip-arrow'></div>
        `;
        document.body.appendChild(this.tooltipElement);
        this.currentElement = null;
        this.init();
    }

    init() {
        document.addEventListener('mouseover', (event) => {
            const target = event.target.closest('[data-tooltip]');
            if (target && target !== this.currentElement) {
                this.currentElement = target;
                this._showTooltip(target);
            }
        });
        document.addEventListener('mouseout', (event) => {
            const target = event.target.closest('[data-tooltip]');
            if (target && target === this.currentElement) {
                this.currentElement = null;
                this._hideTooltip();
            }
        });
        document.addEventListener('click', (event) => {
            const target = event.target.closest('[data-tooltip]');
            if (target && target === this.currentElement) {
                this.currentElement = null;
                this._hideTooltip();
            }
        });
    }

    _showTooltip(element) {
        const tooltipText = element.getAttribute('data-tooltip');
        // Заменяем \n на <br> для отображения переносов строк
        this.tooltipElement.querySelector('.tooltip-content').innerHTML = tooltipText.replaceAll('\n', '<br>');
        const rect = element.getBoundingClientRect();
        const tooltipRect = this.tooltipElement.getBoundingClientRect();
        const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;
        let left = rect.left + window.scrollX + rect.width / 2 - tooltipRect.width / 2;
        let top = rect.top + window.scrollY - tooltipRect.height - 12;
        if (left + tooltipRect.width > window.innerWidth - scrollbarWidth) {
            left = window.innerWidth - tooltipRect.width - scrollbarWidth - 10;
        }
        if (left < 0) {
            left = 10;
        }
        if (top < 0) {
            top = rect.bottom + window.scrollY + 12;
            this.tooltipElement.classList.add('tooltip-bottom');
        } else {
            this.tooltipElement.classList.remove('tooltip-bottom');
        }
        this.tooltipElement.style.left = `${left}px`;
        this.tooltipElement.style.top = `${top}px`;
        this.tooltipElement.classList.add('tooltip-visible');
    }

    _hideTooltip() {
        this.tooltipElement.classList.remove('tooltip-visible');
    }
}
