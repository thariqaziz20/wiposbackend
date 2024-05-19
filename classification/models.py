from django.db import models

# Create your models here.

class ModelWithPickle(models.Model):
    username = models.CharField(max_length=100)
    date     = models.DateField(auto_now=False, auto_now_add=True)
    time     = models.TimeField(auto_now=False, auto_now_add=True)
    svm_model = models.BinaryField()
    rf_model = models.BinaryField()
