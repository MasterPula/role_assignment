from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('assigner.urls')),  # Includiamo le URL dell'app assigner
]
