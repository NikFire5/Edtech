from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
    'я': 'ya',
    # казахские буквы
    'ә': 'a', 'ғ': 'g', 'қ': 'k', 'ң': 'n', 'ө': 'o', 'ұ': 'u', 'ү': 'u', 'һ': 'h', 'і': 'i',
}


def make_slug(text: str) -> str:
    """Транслитерирует кириллицу и делает slug, подходящий для <slug:slug> в urls.py."""
    text = ''.join(_TRANSLIT.get(ch, ch) for ch in text.lower())
    return slugify(text)


# Эти значения заняты служебными URL (/courses/create/, /courses/lessons/...), поэтому
# курс с таким slug был бы недоступен.
RESERVED_SLUGS = {'create', 'lessons', 'categories'}


def unique_slug(model, text: str, instance, fallback: str) -> str:
    """Собирает уникальный slug для model из текста (с транслитерацией и суффиксом -2, -3...)."""
    max_length = model._meta.get_field('slug').max_length
    base = (make_slug(text) or fallback)[:max_length - 8].strip('-') or fallback
    if base in RESERVED_SLUGS:
        base = f'{base}-{fallback}'
    slug, n = base, 2
    while model.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


# Create your models here.
class Category(models.Model):
    title = models.CharField('Название', max_length=150, unique=True)
    slug = models.SlugField('Slug', max_length=150, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Category, self.title, self, 'category')
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

class Course(models.Model):
    title = models.CharField('Название курса', max_length=255)
    slug = models.SlugField('Slug', max_length=255, unique=True)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена (₸)', max_digits=10, decimal_places=2, default=0.00)
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='courses', 
        verbose_name='Категория'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_courses',
        verbose_name='Преподаватель'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(Course, self.title, self, 'course')
        super().save(*args, **kwargs)

    def can_be_managed_by(self, user) -> bool:
        """Редактировать курс, его уроки и удалять его может автор-преподаватель или администратор."""
        if not user.is_authenticated:
            return False
        if user.is_admin():
            return True
        return self.instructor_id == user.pk and user.is_instructor()

    def get_absolute_url(self):
        if not self.slug:
            return reverse('courses:course_list')
        return reverse('courses:course_detail', kwargs={'slug': self.slug})

    def __str__(self) -> str:
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )
    title = models.CharField('Заголовок урока', max_length=255)
    content = models.TextField('Содержимое урока')
    order = models.PositiveBigIntegerField('Порядковый номер', default=1)

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order']

    def get_absolute_url(self):
        return reverse('courses:lesson_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.order}. {self.title}"

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Студент'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Курс'
    )
    enrolled_at = models.DateTimeField('Дата записи', auto_now_add=True)

    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        unique_together = ('student', 'course')

    def __str__(self) -> str:
        return f"{self.student.username} -> {self.course.title}"