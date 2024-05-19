from django.contrib import admin
from .models import ModelWithPickle
# Register your models here.


@admin.register(ModelWithPickle)
class ModelWithPickleAdmin(admin.ModelAdmin):
    list_display =["username","date","time","svm_model","rf_model"]
    list_filter = ['username']