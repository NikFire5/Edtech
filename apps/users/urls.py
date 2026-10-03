from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordChangeView,
    MyProfileRedirectView,
    ProfileUpdateView,
    ProfileView,
    SignUpView,
)

app_name = 'users'

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', MyProfileRedirectView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('password/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('u/<str:username>/', ProfileView.as_view(), name='profile_detail'),
]
