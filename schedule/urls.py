from django.urls import path
from . import views

urlpatterns = [
    path('', views.ScheduleListView.as_view(), name='schedule_list'),
    path('add/', views.ScheduleCreateView.as_view(), name='schedule_add'),
    path('<int:pk>/edit/', views.ScheduleUpdateView.as_view(), name='schedule_edit'),
    path('<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),
]