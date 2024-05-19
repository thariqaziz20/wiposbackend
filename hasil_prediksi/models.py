from django.db import models

# Create your models here.

class HasilPrediksi(models.Model):
    username                            = models.CharField(max_length=20)
    date                                = models.DateField(auto_now=False, auto_now_add=True)
    time                                = models.TimeField(auto_now=False, auto_now_add=True)
    lokasi                              = models.CharField(max_length=50)
    persentase_model_Random_Forest      = models.CharField(max_length=50)
    persentase_model_SVM                = models.CharField(max_length=50)

