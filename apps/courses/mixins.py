from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from .models import Course, Enrollment

class EnrollmentOrInstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        user = self.request.user
        if not user.is_authenticated:
            return False

        lesson_id = self.kwargs.get('pk')
        from .models import Lesson
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        course = lesson.course

        is_istructor = course.instructor == user or user.is_superuser
        is_enrolled = Enrollment.objects.filter(student=user, course=course).exists()

        return is_istructor or is_enrolled

class InstructorRequiredMixin(UserPassesTestMixin):
    def test_func(self) -> bool:
        user = self.request.user
        return user.is_authenticated and user.is_intructor()