from django import forms
from .models import Course


class CourseForm(forms.ModelForm):
    """
    Форма создания/редактирования курса со стилизацией Bootstrap.
    """
    class Meta:
        model = Course
        fields = ['title', 'category', 'price', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Навешиваем класс Bootstrap 'form-control' на все поля формы
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'