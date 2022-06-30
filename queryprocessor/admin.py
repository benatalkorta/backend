from django.contrib import admin

from .models import QuestionModel, DenyAccessToFields

# Register your models here.


admin.site.register(QuestionModel)
