# Register your models here.
from django.contrib import admin
from .models import Person, Week, Assignment

admin.site.register(Person)
admin.site.register(Week)
admin.site.register(Assignment)
