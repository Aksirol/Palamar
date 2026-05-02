from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Правильна функція для головної сторінки
def home_view(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('education/', include('subjects.urls')),
    path('', home_view, name='home'),
    path('schedule/', include('schedule.urls')),
    path('grades/', include('grades.urls')),
    path('attendance/', include('attendance.urls')),
    path('assignments/', include('assignments.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)