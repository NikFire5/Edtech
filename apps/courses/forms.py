from django import forms

from .models import Category, Course, Lesson


class CategoryForm(forms.ModelForm):
    """Новая категория. Slug создаётся автоматически из названия."""

    class Meta:
        model = Category
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например, Data Science'}),
        }


class CourseForm(forms.ModelForm):
    """Форма создания и редактирования курса."""

    class Meta:
        model = Course
        fields = ['title', 'category', 'price', 'description']
        widgets = {
            'price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'description': forms.Textarea(attrs={'rows': 8}),
        }


class LessonForm(forms.ModelForm):
    """Форма добавления и редактирования урока. Курс подставляется во view."""

    class Meta:
        model = Lesson
        fields = ['title', 'order', 'content']
        widgets = {
            'order': forms.NumberInput(attrs={'min': 1}),
            'content': forms.Textarea(attrs={'rows': 14}),
        }
        help_texts = {
            'order': 'Уроки показываются по возрастанию номера.',
        }
