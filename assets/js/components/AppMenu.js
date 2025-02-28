export default class AppMenu {
    constructor() {
        this.mainMenuButton = document.getElementById('menu-apps');
        this.sidebarPanel = document.querySelector('.sidebar__panel');
        this.floatPanel = null;
        this.overlay = null;

        this.init();
    }

    init() {
        if (this.mainMenuButton) {
            this.mainMenuButton.addEventListener('click', (event) => {
                event.preventDefault();
                this.toggleFloatPanel();
            });
        }
    }

    toggleFloatPanel() {
        if (this.floatPanel) {
            this.removeFloatPanel();
        } else {
            this.createFloatPanel();
            this.createOverlay();
            setTimeout(() => this.animateFloatPanel(), 10); // Небольшая задержка для запуска анимации
        }
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.classList.add('sidebar__overlay');
        document.body.appendChild(this.overlay);

        setTimeout(() => {
            this.overlay.classList.add('sidebar__overlay_visible'); // Плавное затемнение
        }, 10);

        this.overlay.addEventListener('click', () => this.removeFloatPanel());
    }

    createFloatPanel() {
        this.floatPanel = document.createElement('div');
        this.floatPanel.classList.add('sidebar__float-panel', 'sidebar__float-panel_hidden');

        this.floatPanel.innerHTML = `
            <a href="/tpa/" class="sidebar__item module-color_tpa">
                <div class="sidebar__icon sidebar__icon_app"></div>
                <h3 class="sidebar__text">Техническое обслуживание ТПА</h3>
            </a>
            <a href="/leaks/" class="sidebar__item module-color_leaks">
                <div class="sidebar__icon sidebar__icon_app"></div>
                <h3 class="sidebar__text">Регистрация утечек газа</h3>
            </a>
            <a href="/rational/" class="sidebar__item module-color_rational">
                <div class="sidebar__icon sidebar__icon_app"></div>
                <h3 class="sidebar__text">Рационализаторская работа</h3>
            </a>
        `;

        // Добавляем обработчик клика на кнопки меню
        const links = this.floatPanel.querySelectorAll('.sidebar__item');
        links.forEach(link => {
            link.addEventListener('click', () => {
                this.removeFloatPanel(); // Закрываем меню и оверлей
            });
        });

        this.sidebarPanel.insertAdjacentElement('afterend', this.floatPanel);
    }

    animateFloatPanel() {
        if (this.floatPanel) {
            this.floatPanel.classList.remove('sidebar__float-panel_hidden');
            this.floatPanel.classList.add('sidebar__float-panel_visible');

            const items = this.floatPanel.querySelectorAll('.sidebar__item');
            items.forEach((item, index) => {
                item.style.opacity = '0';
                item.style.transform = 'translateX(20px)';
                setTimeout(() => {
                    item.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                    item.style.opacity = '1';
                    item.style.transform = 'translateX(0)';
                    // Удаляем inline стили после завершения анимации
                    setTimeout(() => {
                        item.style.transition = '';
                        item.style.transform = '';
                    }, 300); // Время анимации
                }, index * 100);
            });
        }
    }

    removeFloatPanel() {
        if (this.floatPanel) {
            this.floatPanel.classList.remove('sidebar__float-panel_visible');
            this.floatPanel.classList.add('sidebar__float-panel_hidden');
            setTimeout(() => {
                if (this.floatPanel) {
                    this.floatPanel.remove();
                    this.floatPanel = null;
                }
            }, 300); // Ждем завершения анимации перед удалением
        }
        if (this.overlay) {
            this.overlay.classList.remove('sidebar__overlay_visible');
            setTimeout(() => {
                if (this.overlay) {
                    this.overlay.remove();
                    this.overlay = null;
                }
            }, 300);
        }
    }
}
