from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import render

def handler404(request, exception, template_name='main/404.html'):
    """
    Custom 404 error handler.
    """
    return render(request, template_name, status=404)

def handler500(request, template_name='main/error.html'):
    """
    Custom 500 error handler.
    """
    return render(request, template_name, 
                 {'message': 'An internal server error occurred.', 'error': ''}, 
                 status=500)

urlpatterns = [
    path('', include("main.urls")),
    path('', include("account.urls")),
    path('admin/', admin.site.urls),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# This is only needed when using runserver in DEBUG mode.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
