from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from equipments.models import Equipment
from module_app.utils import compress_image
from users.models import ModuleUser


SERVICECOLOR = (
    ('blue', 'синий'),
    ('gray', 'серый'),
    ('red', 'красный'),
    ('violet', 'фиолетовый'),
    ('yellow', 'жёлтый'),
)

DRIVETYPE = (
    ('Пневматический', 'Пневматический'),
    ('Пневмогидравлический', 'Пневмогидравлический'),
    ('Ручной (ручка, рычаг, маховик)', 'Ручной (ручка, рычаг, маховик)'),
    ('Ручной с механическим редуктором', 'Ручной с механическим редуктором'),
    ('Электрический c механическим редуктором', 'Электрический c механическим редуктором'),
    ('Без привода', 'Без привода'),
)

VALVETYPE = (
    ('Задвижка клиновая', 'Задвижка клиновая'),
    ('Вентиль', 'Вентиль'),
    ('Кран шаровой', 'Кран шаровой'),
    ('Клапан запорный', 'Клапан запорный'),
    ('Клапан обратный', 'Клапан обратный'),
    ('Клапан предохранительный', 'Клапан предохранительный'),
    ('Клапан регулирующий', 'Клапан регулирующий'),
)

REMOTE = (
    ('Да', 'Да'),
    ('Нет', 'Нет'),
    ('Не требуется', 'Не требуется'),
)

FILETYPE = (('video', 'video'), ('image', 'image'))

DESIGNTYPE = (
    ('Надземное', 'Надземное'),
    ('Подземное', 'Подземное'),
    ('В колодце', 'В колодце'),
)


class Factory(models.Model):
    name = models.CharField(
        'наименование изготовителя',
        max_length=70,
        blank=False,
        null=False,
    )
    country = models.CharField(
        'страна',
        max_length=20,
        blank=False,
        null=False,
    )
    class Meta:
        ordering = ('name',)
        verbose_name = 'Изготовитель ТПА'
        verbose_name_plural = 'Изготовители ТПА'

    def __str__(self) -> str:
        return f'{self.name}, {self.country}'


class Valve(models.Model):
    equipment = models.ForeignKey(
        Equipment(),
        verbose_name='Место установки',
        related_name='equipment',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
    )
    title = models.CharField(
        'Наименование ТПА',
        max_length=50,
        blank=False,
        null=False,
    )
    diameter = models.PositiveIntegerField(
        'Ду, мм',
        blank=False,
        null=False,
    )
    pressure = models.PositiveIntegerField(
        'Ру, кгс/см2',
        blank=False,
        null=False,
    )
    valve_type = models.CharField(
        verbose_name='Тип ТПА',
        choices=VALVETYPE,
        max_length=50,
        blank=False,
        null=False
    )
    factory = models.ForeignKey(
        Factory,
        verbose_name='Изготовитель',
        on_delete=models.CASCADE
    )
    year_made = models.PositiveIntegerField(
        'Год изготовления',
        null=True,
        blank=True,
    )
    year_exploit = models.PositiveIntegerField(
        'Год ввода в эксплуатацию',
        null=True,
        blank=True,
    )
    tech_number =  models.CharField(
        'Технологический номер',
        max_length=50,
        null=False,
        blank=False,
    )
    factory_number = models.CharField(
        'Заводской номер',
        default='',
        max_length=50,
        null=True,
        blank=True,
    )
    inventory_number = models.CharField(
        'Инвентарный номер',
        default='',
        max_length=50,
        null=True,
        blank=True,
    )
    lifetime = models.PositiveIntegerField(
        'Срок службы',
        default=25,
        null=True,
        blank=True,
    )
    remote = models.CharField(
        'Дистанционное управление',
        choices=REMOTE,
        max_length=50
    )
    label = models.CharField(
        'Марка',
        max_length=50,
        null=True,
        blank=True,
    )
    material = models.CharField(
        'Материал корпуса',
        default='',
        max_length=50,
        blank=True,
    )
    design = models.CharField(
        'Исполнение',
        choices=DESIGNTYPE,
        max_length=50,
    )
    drive_type = models.CharField(
        'Тип привода',
        choices=DRIVETYPE,
        max_length=50,
        blank=True,
        null=True,
    )
    drive_factory = models.ForeignKey(
        Factory,
        verbose_name='Изготовитель привода',
        on_delete=models.CASCADE,
        related_name='factory',
        blank=True,
        null=True
    )
    drive_year_exploit = models.PositiveIntegerField(
        'Год ввода в эксплуатацию привода',
        blank=True,
        null=True
    )
    note = models.CharField(
        'Примечание',
        default='',
        max_length=500,
        blank=True,
    )
    removed = models.BooleanField(
        'Демонтирован',
        default=False
    )

    class Meta:
        ordering = ('diameter',)
        verbose_name = 'ТПА'
        verbose_name_plural = 'ТПА'

    def get_ks(self):
        """
        Возвращает корневой элемент второго уровня для текущего оборудования.
        """
        if self.equipment:
            # Получаем корень ветки
            root = self.equipment.get_root()
            # Получаем всех потомков корня
            descendants = root.get_descendants(include_self=True)
            # Фильтруем элементы второго уровня
            second_level = descendants.filter(level=1)
            if second_level.exists():
                return second_level.first()
        return None

    def __str__(self):
        return f'{self.valve_type} Ду{self.diameter} | №{self.tech_number}'


class ValveDocument(models.Model):
    doc = models.FileField(upload_to='tpa/docs')
    name = models.CharField(
        'Наименование документа',
        max_length=50,
        blank=False,
        null=False,
    )
    valve = models.ForeignKey(
        Valve,
        on_delete=models.CASCADE,
        related_name='valve_doc'
    )

    class Meta:
        verbose_name = 'Документация по ТПА'
        verbose_name_plural = 'Документация по ТПА'


class ValveImage(models.Model):
    image = models.ImageField(
        'Фото ТПА',
        upload_to='tpa/images',
        # default='tpa/image_not_upload.png',
        blank=True,
        null=True,
    )
    name = models.CharField(
        'Наименование фотографии',
        max_length=50,
        blank=True,
        null=True,
    )
    valve = models.ForeignKey(
        Valve,
        on_delete=models.CASCADE,
        related_name='images'
    )

    class Meta:
        verbose_name = 'Фотоматериалы по ТПА'
        verbose_name_plural = 'Фотоматериалы по ТПА'

    def save(self, *args, **kwargs):  # сжатие фото перед сохранением
        super(ValveImage, self).save(*args, **kwargs)
        if self.image:
            compress_image(self.image)


class ServiceType(models.Model):
    name = models.CharField(
        'Наименование ТО',
        max_length=50,
        blank=False,
        null=False
    )
    period = models.PositiveIntegerField(
        'Периодичность, мес.',
        blank=True,
        null=True
    )
    valve_type = models.CharField(
        'Тип ТПА',
        choices=VALVETYPE,
        max_length=50,
        blank=False,
        null=False
    )
    min_diameter = models.PositiveIntegerField(
        'Минимальный диаметр',
        blank=False,
        null=False,
        validators=[
            MaxValueValidator(1400),
            MinValueValidator(50),
        ]
    )
    max_diameter = models.PositiveIntegerField(
        'Максимальный диаметр',
        blank=False,
        null=False,
        validators=[
            MaxValueValidator(1400),
            MinValueValidator(50),
        ]
    )
    color = models.CharField(
        'Цвет ТО в шаблоне',
        choices=SERVICECOLOR,
        max_length=30,
        null=False,
        blank=False,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Вид ТО'
        verbose_name_plural = 'Вид ТО'

    def __str__(self):
        return self.name


# работы, привязанные к виду ТО
class Work(models.Model):
    description = models.CharField(
        'Описание работы',
        max_length=500,
        blank=False,
        null=False,
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE,
        verbose_name='Тип ТО'
    )
    planned = models.BooleanField(
        verbose_name='по регламенту',
        default=True
    )

    class Meta:
        ordering = ('service_type',)
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'

    def __str__(self):
        return f'{self.description[:25].capitalize()}'


# проведённые ремонты
class Service(models.Model):
    executor = models.ForeignKey(
        ModuleUser,
        on_delete=models.CASCADE,
        verbose_name='исполнитель',
        related_name='services'
    )
    prod_date = models.DateField(
        'Дата проведения',
        blank=False,
        null=False,
    )
    reg_date = models.DateField(
        'Дата регистрации',
        auto_now_add=True,
        blank=False,
        null=False,
    )
    service_type = models.ForeignKey(
        ServiceType,
        on_delete=models.CASCADE
    )
    valve = models.ForeignKey(
        Valve,
        on_delete=models.CASCADE,
        related_name='services'
    )
    works = models.ManyToManyField(
        Work,
        through='WorkService',
        through_fields=('service', 'work')
    )

    class Meta:
        ordering = ('service_type',)
        verbose_name = 'Проведенное ТО'
        verbose_name_plural = 'Проведенные ТО'

    def __str__(self):
        date = self.prod_date.strftime('%d.%m.%Y')
        return f'{date} | {self.service_type} | {self.valve}'

    @property
    def prod_month(self):
        return self.prod_date.month

    @property
    def prod_year(self):
        return self.prod_date.year


class WorkService(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
    )
    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE
    )
    done = models.BooleanField(
        'Выполнено',
        default=True
    )
    faults = models.CharField(
        'Замечания',
        max_length=500,
        default='Замечаний нет',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('service',)
        verbose_name = 'Проведенная работа'
        verbose_name_plural = 'Проведенные работы'

    def __str__(self):
        return f'{self.service}'


class WorkProof(models.Model):
    file = models.FileField(upload_to='tpa/work/proofs')
    file_type = models.CharField(
        'Тип файла',
        choices=FILETYPE,
        max_length=10
    )
    name = models.CharField(
        'Наименование документа',
        max_length=100,
        blank=False,
        null=False,
    )
    work = models.ForeignKey(
        WorkService,
        on_delete=models.CASCADE,
        related_name='work_proof'
    )

    class Meta:
        verbose_name = 'Фото/видеоматериалы по работам'
        verbose_name_plural = 'Фото/видеоматериалы по работам'
