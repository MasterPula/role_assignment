from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_assignments, name='generate_assignments'),
    path('edit/<int:week_id>/', views.edit_week, name='edit_week')
]
