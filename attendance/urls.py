from django.urls import path
from . import views

urlpatterns = [
    path('mark/', views.AttendanceMarkView.as_view(), name='attendance_mark'),
    path('stats/', views.AttendanceStatsView.as_view(), name='attendance_stats'),
]