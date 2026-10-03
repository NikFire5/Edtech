from django.urls import path
from .views import (
    CategoryCreateView,
    CourseCreateView,
    CourseDeleteView,
    CourseDetailView,
    CourseEnrollView,
    CourseListView,
    CourseUpdateView,
    LessonCreateView,
    LessonDeleteView,
    LessonDetailView,
    LessonUpdateView,
)

app_name = 'courses'

# Статичные маршруты (create/, lessons/..., categories/...) стоят выше <slug:slug>/,
# иначе они были бы приняты за slug курса.
urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),

    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/<int:pk>/edit/', LessonUpdateView.as_view(), name='lesson_update'),
    path('lessons/<int:pk>/delete/', LessonDeleteView.as_view(), name='lesson_delete'),

    path('<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    path('<slug:slug>/edit/', CourseUpdateView.as_view(), name='course_update'),
    path('<slug:slug>/delete/', CourseDeleteView.as_view(), name='course_delete'),
    path('<slug:slug>/enroll/', CourseEnrollView.as_view(), name='course_enroll'),
    path('<slug:slug>/lessons/add/', LessonCreateView.as_view(), name='lesson_create'),
]
