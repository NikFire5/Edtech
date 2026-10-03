from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

# Create your models here.
class Category(models.Model):
    title = models.CharField('Название', max_length=150, unique=True)
    slug = models.SlugField('Slug', max_length=150, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']

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
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

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