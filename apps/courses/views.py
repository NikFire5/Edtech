from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
)

from .forms import CourseForm
from .mixins import EnrollmentOrInstructorRequiredMixin, InstructorRequiredMixin
from .models import Category, Course, Enrollment, Lesson


class IndexView(TemplateView):
    """
    Главная страница (Landing page).
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_courses'] = Course.objects.select_related('category', 'instructor')[:6]
        return context


class CourseListView(ListView):
    """
    Страница каталога курсов со стандартным отображением и AJAX-фильтрацией.
    """
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        queryset = Course.objects.select_related('category', 'instructor')
        category_slug = self.request.GET.get('category')
        search_query = self.request.GET.get('q')

        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        return queryset

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            courses_data = [
                {
                    'id': course.id,
                    'title': course.title,
                    'slug': course.slug,
                    'category': course.category.title,
                    'instructor': course.instructor.username,
                    'price': str(course.price),
                    'detail_url': course.get_absolute_url()
                }
                for course in context['courses']
            ]
            return JsonResponse({'courses': courses_data})
        
        return super().render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class CourseDetailView(DetailView):
    """
    Детальная карточка курса.
    """
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        course = self.object

        is_enrolled = False
        if user.is_authenticated:
            is_enrolled = Enrollment.objects.filter(student=user, course=course).exists()

        context['is_enrolled'] = is_enrolled
        context['lessons'] = course.lessons.all()
        return context


class CourseCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, InstructorRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'


class CourseDeleteView(LoginRequiredMixin, InstructorRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('courses:course_list')


class LessonDetailView(LoginRequiredMixin, EnrollmentOrInstructorRequiredMixin, DetailView):
    """
    Закрытый просмотр материалов конкретного урока.
    """
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'


class CourseEnrollView(LoginRequiredMixin, View):
    """
    Эндпоинт для записи текущего студента на курс.
    """
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        Enrollment.objects.get_or_create(student=request.user, course=course)
        return redirect('courses:course_detail', slug=course.slug)