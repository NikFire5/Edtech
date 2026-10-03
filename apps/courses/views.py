from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.text import Truncator
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView
)

from .forms import CategoryForm, CourseForm, LessonForm
from .mixins import (
    CourseManagerRequiredMixin,
    EnrollmentOrInstructorRequiredMixin,
    InstructorRequiredMixin,
    LessonManagerRequiredMixin,
)
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
                    'description': Truncator(course.description).words(22),
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

        can_manage = course.can_be_managed_by(user)

        context['is_enrolled'] = is_enrolled
        context['can_manage'] = can_manage
        context['can_read'] = is_enrolled or can_manage
        context['lessons'] = course.lessons.all()
        return context


class CourseCreateView(LoginRequiredMixin, InstructorRequiredMixin, SuccessMessageMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_message = 'Курс создан. Теперь добавьте к нему уроки.'

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, CourseManagerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_message = 'Изменения сохранены.'


class CourseDeleteView(LoginRequiredMixin, CourseManagerRequiredMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('courses:course_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Курс удалён.')
        return response


class CategoryCreateView(LoginRequiredMixin, InstructorRequiredMixin, CreateView):
    """
    Создание категории. Работает и как обычная страница, и как AJAX-эндпоинт
    для диалога «Новая категория» на странице курса (отвечает JSON).
    """
    model = Category
    form_class = CategoryForm
    template_name = 'courses/category_form.html'

    def is_ajax(self):
        return self.request.headers.get('x-requested-with') == 'XMLHttpRequest'

    def get_safe_next(self):
        """Адрес возврата из ?next=, только если он ведёт на этот же сайт."""
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={self.request.get_host()},
            require_https=self.request.is_secure(),
        ):
            return next_url
        return ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next_url'] = self.get_safe_next() or reverse('courses:course_create')
        return context

    def get_success_url(self):
        return self.get_safe_next() or reverse('courses:course_create')

    def form_valid(self, form):
        self.object = form.save()
        if self.is_ajax():
            return JsonResponse(
                {'id': self.object.pk, 'title': self.object.title, 'slug': self.object.slug},
                status=201,
            )
        messages.success(self.request, f'Категория «{self.object.title}» создана.')
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if self.is_ajax():
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({'errors': errors}, status=400)
        return super().form_invalid(form)


class LessonCreateView(LoginRequiredMixin, CourseManagerRequiredMixin, CreateView):
    """
    Добавление урока к курсу. Доступно автору курса и администратору.
    """
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'

    def get_initial(self):
        initial = super().get_initial()
        last_order = self.get_managed_course().lessons.aggregate(Max('order'))['order__max'] or 0
        initial['order'] = last_order + 1
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.get_managed_course()
        return context

    def form_valid(self, form):
        form.instance.course = self.get_managed_course()
        response = super().form_valid(form)
        messages.success(self.request, 'Урок добавлен.')
        return response

    def get_success_url(self):
        if 'add_another' in self.request.POST:
            return reverse('courses:lesson_create', kwargs={'slug': self.object.course.slug})
        return self.object.course.get_absolute_url()


class LessonUpdateView(LoginRequiredMixin, LessonManagerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_form.html'
    success_message = 'Урок сохранён.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context


class LessonDeleteView(LoginRequiredMixin, LessonManagerRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'courses/lesson_confirm_delete.html'

    def get_success_url(self):
        return self.object.course.get_absolute_url()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Урок удалён.')
        return response


class LessonDetailView(LoginRequiredMixin, EnrollmentOrInstructorRequiredMixin, DetailView):
    """
    Закрытый просмотр материалов конкретного урока.
    """
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    context_object_name = 'lesson'

    def get_queryset(self):
        return Lesson.objects.select_related('course')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        siblings = Lesson.objects.filter(course=lesson.course)
        context['prev_lesson'] = siblings.filter(order__lt=lesson.order).order_by('-order').first()
        context['next_lesson'] = siblings.filter(order__gt=lesson.order).order_by('order').first()
        context['can_manage'] = lesson.course.can_be_managed_by(self.request.user)
        return context


class CourseEnrollView(LoginRequiredMixin, View):
    """
    Эндпоинт для записи текущего студента на курс.
    """
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)

        if course.can_be_managed_by(request.user):
            messages.info(request, 'Вы управляете этим курсом, записываться на него не нужно.')
            return redirect('courses:course_detail', slug=course.slug)

        _, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        if created:
            messages.success(request, 'Вы записаны на курс. Уроки теперь доступны.')
        return redirect('courses:course_detail', slug=course.slug)
