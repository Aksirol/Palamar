from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('export-pdf/', views.DownloadPDFReportView.as_view(), name='export_pdf'),
]