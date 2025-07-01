export default class PipelineContextMenu {
    constructor(options = {}) {
        this.options = {
            menuClass: 'pipeline-context-menu',
            menuItemClass: 'pipeline-context-menu-item',
            ...options
        };
        this.menu = null;
        this.currentTarget = null;
    }

    createMenu(items) {
        this.menu = document.createElement('div');
        this.menu.className = this.options.menuClass;

        items.forEach(item => {
            const menuItem = document.createElement('button');
            menuItem.className = this.options.menuItemClass;
            menuItem.textContent = item.text;
            menuItem.addEventListener('click', () => {
                item.action(this.currentTarget);
                this.close();
            });
            this.menu.appendChild(menuItem);
        });

        document.body.appendChild(this.menu);
        this.positionMenu();
        this.addOutsideClickListener();
    }

    positionMenu() {
        if (!this.currentTarget || !this.menu) return;

        const rect = this.currentTarget.getBoundingClientRect();
        this.menu.style.position = 'absolute';
        this.menu.style.left = `${rect.left + window.scrollX}px`;
        this.menu.style.top = `${rect.bottom + window.scrollY}px`;
    }

    addOutsideClickListener() {
        this.outsideClickListener = (e) => {
            if (!this.menu.contains(e.target)) {
                this.close();
            }
        };
        document.addEventListener('click', this.outsideClickListener);
    }

    open(target, items) {
        this.currentTarget = target;
        this.close(); // Close any existing menu
        this.createMenu(items);
    }

    close() {
        if (this.menu) {
            document.removeEventListener('click', this.outsideClickListener);
            this.menu.remove();
            this.menu = null;
        }
    }
}
