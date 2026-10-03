from django.urls import path
from .views import (
    CourseCreateView,
    CourseDeleteView,
    CourseDetailView,
    CourseEnrollView,
    CourseListView,
    CourseUpdateView,
    LessonDetailView,
)

app_name = 'courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('/', CourseDetailView.as_view(), name='course_detail'),
    path('/edit/', CourseUpdateView.as_view(), name='course_update'),
    path('/delete/', CourseDeleteView.as_view(), name='course_delete'),
    path('/enroll/', CourseEnrollView.as_view(), name='course_enroll'),
    path('lessons//', LessonDetailView.as_view(), name='lesson_detail'),
]