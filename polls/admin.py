from django.contrib import admin
from .models import Question , Choice 

admin.site.register(Question)
# Register your models here.
admin.site.register(Choice)  # Assuming Choice is also a model in your polls app