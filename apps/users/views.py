from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, RedirectView, UpdateView

from apps.courses.models import Course, Enrollment

from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')
    template_name = 'users/signup.html'


class CustomLoginView(LoginView):
    template_name = 'users/login.html'


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('index')


class MyProfileRedirectView(LoginRequiredMixin, RedirectView):
    """/users/profile/ -> страница профиля текущего пользователя."""
    def get_redirect_url(self, *args, **kwargs):
        return reverse('users:profile_detail', kwargs={'username': self.request.user.username})


class ProfileView(DetailView):
    """
    Профиль пользователя. Публично видны имя, роль, «о себе» и курсы преподавателя.
    Список курсов, на которые записан студент, видит только он сам и администратор.
    """
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object
        viewer = self.request.user

        is_own = viewer.is_authenticated and viewer.pk == profile_user.pk
        viewer_is_admin = viewer.is_authenticated and viewer.is_admin()

        context['is_own'] = is_own

        if profile_user.is_instructor():
            context['created_courses'] = (
                profile_user.created_courses.select_related('category', 'instructor')
            )
            context['students_count'] = Enrollment.objects.filter(
                course__instructor=profile_user
            ).count()

        if is_own or viewer_is_admin:
            context['enrolled_courses'] = (
                Course.objects.filter(enrollments__student=profile_user)
                .select_related('category', 'instructor')
            )
        return context


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'users/profile_form.html'
    success_message = 'Профиль обновлён.'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse('users:profile_detail', kwargs={'username': self.request.user.username})


class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('users:profile')
    success_message = 'Пароль изменён.'
