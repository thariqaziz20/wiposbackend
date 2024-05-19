import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from background_service.models import BackgroundService
from background_service.serializers import BackgroundServiceSerializer
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta



def PredictLocation(username):
    print("berhasil")
    queryset = BackgroundService.objects.filter(username=username)
    serializer = BackgroundServiceSerializer(queryset, many=True)
    print("gagal1")

    last_data = queryset.last()
    print(last_data)

    if last_data:
        last_date = last_data.date
        last_time = last_data.time
        print(last_date)
        print(last_time)

        date = last_date
        time = last_time
        d=str(time)
        a = datetime.strptime(d, "%H:%M:%S.%f")
        b = timedelta(hours=0, minutes=15, seconds=0)
        c = a - b
        print(c)

        # Filter data berdasarkan rentang waktu
        queryset = BackgroundService.objects.filter(date=date, time__range=(c, time))
        # filter_backends = [DjangoFilterBackend]
        # filterset_fields = ['date', "time"]
        mac_konversi_data = BackgroundService.objects.values_list('mackonversi', flat=True)
        rssi_data = BackgroundService.objects.values_list('rssi', flat=True)

        merged_data = np.column_stack((mac_konversi_data, rssi_data))

        # Menampilkan data
        serialized_data = serializer.data
        return merged_data, serialized_data
    else:
        return None, None
        
    
    
    # try:
    #     queryset = BackgroundService.objects.filter(username=username)
    #     serializer = BackgroundServiceSerializer(queryset, many=True)

    #     last_data = queryset.last()
        
    #     if last_data:
    #         last_date = last_data.date
    #         last_time = last_data.time
    #         print(last_date)
    #         print(last_time)

    #     else:
    #         return None, None 
        
    #     date = last_date
    #     time = last_time
    #     d=str(time)
    #     a = datetime.strptime(d, "%H:%M:%S.%f")
    #     b = timedelta(hours=0, minutes=15, seconds=0)
    #     c = a - b
    #     print(c)

    #     # Filter data berdasarkan rentang waktu
    #     queryset = BackgroundService.objects.filter(date=date, time__range=(c, time))
    #     # filter_backends = [DjangoFilterBackend]
    #     # filterset_fields = ['date', "time"]
    #     mac_konversi_data = BackgroundService.objects.values_list('mackonversi', flat=True)
    #     rssi_data = BackgroundService.objects.values_list('rssi', flat=True)

    #     merged_data = np.column_stack((mac_konversi_data, rssi_data))

    #     # Menampilkan data
    #     serialized_data = serializer.data
    #     return(merged_data,serialized_data)
    
    # except ObjectDoesNotExist:
    #     # Handle the case where the username is not found in the BackgroundService database
    #     return None, None