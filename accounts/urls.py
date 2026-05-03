# accounts/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import CustomLoginView, register_view, PendingStudentsView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', register_view, name='register'),

    # Новий маршрут для заявок
    path('pending-students/', PendingStudentsView.as_view(), name='pending_students'),
]