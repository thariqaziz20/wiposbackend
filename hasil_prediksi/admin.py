from django.contrib import admin
from .models import HasilPrediksi
# Register your models here.


@admin.register(HasilPrediksi)
class DataWiPosAdmin(admin.ModelAdmin):
    list_display =["username","date","time", "lokasi","persentase_model_Random_Forest","persentase_model_SVM"]
    list_filter = ['username',"lokasi"]