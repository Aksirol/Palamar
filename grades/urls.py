from django.urls import path
from . import views

urlpatterns = [
    path('', views.GradeListView.as_view(), name='grade_list'),
    path('add/', views.GradeCreateView.as_view(), name='grade_add'),
]