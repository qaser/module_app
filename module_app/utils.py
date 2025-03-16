from PIL import Image
from django.apps import apps

_MAX_SIZE = 1000


def get_installed_apps():
    return [app_config.name for app_config in apps.get_app_configs()]


def create_choices(queryset):
    '''
    функция для генерации списка кортежей соотношений полей моделей
    используется в формах и фильтрах
    '''
    choices = [(value, value) for value in queryset]
    return choices


# сжатие загружаемых изображений
def compress_image(source_image):
    filepath = source_image.path
    width = source_image.width
    height = source_image.height
    max_size = max(width, height)  # определяем максимальный размер
    if max_size > _MAX_SIZE:
        image = Image.open(filepath)
        image = image.resize(
            (
                round(width / max_size * _MAX_SIZE),
                round(height / max_size * _MAX_SIZE)
            ),
            Image.ANTIALIAS
        )
        image.save(filepath)
