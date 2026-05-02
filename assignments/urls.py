from django.urls import path
from . import views

urlpatterns = [
    path('', views.AssignmentListView.as_view(), name='assignment_list'),
    path('add/', views.AssignmentCreateView.as_view(), name='assignment_add'),
    path('<int:pk>/', views.AssignmentDetailView.as_view(), name='assignment_detail'),
    path('submission/<int:pk>/grade/', views.GradeSubmissionView.as_view(), name='grade_submission'),
]