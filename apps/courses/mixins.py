from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from .models import Course, Enrollment, Lesson


class InstructorRequiredMixin(UserPassesTestMixin):
    """Создавать курсы и категории могут преподаватели и администраторы."""

    def test_func(self) -> bool:
        user = self.request.user
        return user.is_authenticated and user.is_instructor()


class CourseManagerRequiredMixin(UserPassesTestMixin):
    """
    Курс (и добавление к нему уроков) может менять только его автор или администратор.
    Курс ищется по параметру slug из URL.
    """

    def get_managed_course(self) -> Course:
        if not hasattr(self, '_managed_course'):
            self._managed_course = get_object_or_404(Course, slug=self.kwargs['slug'])
        return self._managed_course

    def test_func(self) -> bool:
        return self.get_managed_course().can_be_managed_by(self.request.user)


class LessonManagerRequiredMixin(UserPassesTestMixin):
    """Урок может менять и удалять автор его курса или администратор. Урок ищется по pk из URL."""

    def test_func(self) -> bool:
        lesson = get_object_or_404(Lesson.objects.select_related('course'), pk=self.kwargs['pk'])
        return lesson.course.can_be_managed_by(self.request.user)


class EnrollmentOrInstructorRequiredMixin(UserPassesTestMixin):
    """Читать урок могут записанные студенты, автор курса и администратор."""

    def test_func(self) -> bool:
        user = self.request.user
        if not user.is_authenticated:
            return False

        lesson = get_object_or_404(Lesson.objects.select_related('course'), pk=self.kwargs.get('pk'))
        course = lesson.course

        if course.can_be_managed_by(user):
            return True
        return Enrollment.objects.filter(student=user, course=course).exists()
