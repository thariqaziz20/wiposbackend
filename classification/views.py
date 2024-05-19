from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from data_wipos.serializers import DataWiPosSerializer
from data_wipos.models import DataWiPos
from rest_framework.response import Response
from rest_framework import status
import pandas as pd 
import numpy as np
import pickle
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, accuracy_score
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from .Model_Klasifikasi import ModelKlasifikasi
from .models import ModelWithPickle
from .serializers import ModelWithPickleSerializer
from collections import Counter
from .Predict_Location import PredictLocation
from hasil_prediksi.models import HasilPrediksi
from hasil_prediksi.serializers import HasilPrediksiSerializer



class FittingModel(generics.ListAPIView):
    queryset = DataWiPos.objects.all()
    serializer_class = DataWiPosSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        if self.check_different_values(data):
            
            return Response(data=data, status=status.HTTP_200_OK)

        data_name = data[0] if data else None
        username = data_name.get('username') if data_name else None

        hasil = ModelKlasifikasi(username, data)
        response = {
            "Status" : hasil[2],
            "Hasil Model Klasifikasi SVM": hasil[0],
            "Hasil Model Klasifikasi RF": hasil[1]
        }
        return Response(data=response, status=status.HTTP_200_OK)

    # Fungsi untuk memeriksa apakah ada nilai yang berbeda dalam data kolom pertama
    def check_different_values(self, data):
        # Jika tidak ada data, tidak ada nilai yang berbeda
        if not data:
            return False

        # Ambil nilai dari kolom pertama
        first_column_values = [item['username'] for item in data]

        # Jika ada nilai yang berbeda dalam data kolom pertama, return True
        if len(set(first_column_values)) > 1:
            return True

        return False




class PredictModel(generics.ListAPIView):
    queryset = ModelWithPickle.objects.all()
    serializer_class = ModelWithPickleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['username']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        if self.check_different_values(data):
            
            return Response(data=data, status=status.HTTP_200_OK)

        data_name = data[0] if data else None
        username = data_name.get('username') if data_name else None

        # // Mengambil model dari database
        data_name = data[0] if data else None
        username = data_name.get('username') if data_name else None
        model_with_pickle_instance = ModelWithPickle.objects.get(username=username)
        svm_model = pickle.loads(model_with_pickle_instance.svm_model)
        rf_model = pickle.loads(model_with_pickle_instance.rf_model)

        def make_predictions(svm_model, rf_model, input_data):
            svm_prediction = svm_model.predict(input_data)
            rf_prediction = rf_model.predict(input_data)
            
            return svm_prediction, rf_prediction
        
        input_data, background_data = PredictLocation(username)
        if input_data is None or background_data is None:
            # Construct failure response
            failure_response = {
                "message": "Failed to retrieve input data or background data for the given username."
            }
            return Response(data=failure_response, status=status.HTTP_400_BAD_REQUEST)

        # Make prediction
        svm_prediction, rf_prediction = make_predictions(svm_model, rf_model, input_data)
        # Hitung kemunculan setiap string dalam array untuk kedua model
        counts_SVM = Counter(svm_prediction)
        counts_RF = Counter(rf_prediction)

        # Hitung total kemunculan untuk setiap model
        total_SVM = sum(counts_SVM.values())
        total_RF = sum(counts_RF.values())

        # Hitung dan cetak persentase setiap elemen untuk model SVM
        persentase_SVM = {}
        for nilai, jumlah in counts_SVM.items():
            persentase = (jumlah / total_SVM) * 100
            persentase_SVM[nilai] = "{:.2f} %".format(persentase)

        # Hitung dan cetak persentase setiap elemen untuk model RF
        persentase_RF = {}
        for nilai, jumlah in counts_RF.items():
            persentase = (jumlah / total_RF) * 100
            persentase_RF[nilai] = "{:.2f} %".format(persentase)

        # Dapatkan hasil prediksi dengan persentase terbesar
        max_svm_prediction = max(counts_SVM, key=counts_SVM.get)
        max_rf_prediction = max(counts_RF, key=counts_RF.get)
        # Hitung persentase untuk hasil prediksi terbesar
        persentase_max_svm_prediction = "{:.2f} %".format((counts_SVM[max_svm_prediction] / total_SVM) * 100) if total_SVM != 0 else 0
        persentase_max_rf_prediction = "{:.2f} %".format((counts_RF[max_rf_prediction] / total_RF) * 100) if total_RF != 0 else 0

        def insert_hasil_prediksi_to_database(username, lokasi, persentase_model_RF, persentase_model_SVM):
            # Buat instance serializer dengan data yang ingin dimasukkan
            data = {
                'username': username,
                'lokasi': lokasi,
                'persentase_model_Random_Forest': persentase_model_RF,
                'persentase_model_SVM': persentase_model_SVM
            }
            serializer = HasilPrediksiSerializer(data=data)

            # Periksa apakah data valid
            if serializer.is_valid():
                # Simpan data ke dalam database
                serializer.save()
                print("Data berhasil dimasukkan ke dalam database.")
            else:
                # Jika data tidak valid, cetak pesan kesalahan
                print("Gagal memasukkan data ke dalam database. Kesalahan:", serializer.errors)

        insert_hasil_prediksi_to_database(username, max_svm_prediction, persentase_max_rf_prediction, persentase_max_svm_prediction)

        # Buat respons
        response = {
            "Username": username,
            "SVM Percentage": persentase_SVM,
            "Max SVM Prediction": {"Value": max_svm_prediction, "Percentage": persentase_max_svm_prediction},
            "RF Percentage": persentase_RF,
            "Max RF Prediction": {"Value": max_rf_prediction, "Percentage": persentase_max_rf_prediction},
            # "Background Data": background_data
        }
        return Response(data=response, status=status.HTTP_200_OK)
    
    def check_different_values(self, data):
        # Jika tidak ada data, tidak ada nilai yang berbeda
        if not data:
            return False

        # Ambil nilai dari kolom pertama
        first_column_values = [item['username'] for item in data]

        # Jika ada nilai yang berbeda dalam data kolom pertama, return True
        if len(set(first_column_values)) > 1:
            return True

        return False
    

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #     serializer = self.get_serializer(queryset, many=True)
    #     data = serializer.data
    #     # queryset = self.filter_queryset(self.get_queryset())
    #     # serializer = self.get_serializer(queryset, many=True)
    #     # data = serializer.data

    #     if self.check_different_values(data):
            
    #         return Response(data=data, status=status.HTTP_200_OK)
        
        # # // Mengambil model dari database
        # data_name = data[0] if data else None
        # username = data_name.get('username') if data_name else None
        # model_with_pickle_instance = ModelWithPickle.objects.get(username=username)
        # svm_model = pickle.loads(model_with_pickle_instance.svm_model)
        # rf_model = pickle.loads(model_with_pickle_instance.rf_model)

        
        # def make_predictions(svm_model, rf_model, input_data):
        #     svm_prediction = svm_model.predict(input_data)
        #     rf_prediction = rf_model.predict(input_data)
            
        #     return svm_prediction, rf_prediction
        
        # data_background_service, background_data = PredictLocation(username)

        # # Make predictions
        # svm_prediction, rf_prediction = make_predictions(svm_model, rf_model, data_background_service)

    #     # Hitung kemunculan setiap string dalam array untuk kedua model
    #     counts_SVM = Counter(svm_prediction)
    #     counts_RF = Counter(rf_prediction)

    #     # Hitung total kemunculan untuk setiap model
    #     total_SVM = sum(counts_SVM.values())
    #     total_RF = sum(counts_RF.values())

    #     # Hitung dan cetak persentase setiap elemen untuk model SVM
    #     persentase_SVM = {}
    #     for nilai, jumlah in counts_SVM.items():
    #         persentase = (jumlah / total_SVM) * 100
    #         persentase_SVM[nilai] = "{:.2f} %".format(persentase)

    #     # Hitung dan cetak persentase setiap elemen untuk model RF
    #     persentase_RF = {}
    #     for nilai, jumlah in counts_RF.items():
    #         persentase = (jumlah / total_RF) * 100
    #         persentase_RF[nilai] = "{:.2f} %".format(persentase)

    #     # Dapatkan hasil prediksi dengan persentase terbesar
    #     max_svm_prediction = max(counts_SVM, key=counts_SVM.get)
    #     max_rf_prediction = max(counts_RF, key=counts_RF.get)
    #     # Hitung persentase untuk hasil prediksi terbesar
    #     persentase_max_svm_prediction = "{:.2f} %".format((counts_SVM[max_svm_prediction] / total_SVM) * 100) if total_SVM != 0 else 0
    #     persentase_max_rf_prediction = "{:.2f} %".format((counts_RF[max_rf_prediction] / total_RF) * 100) if total_RF != 0 else 0

    #     def insert_hasil_prediksi_to_database(username, lokasi, persentase_model_RF, persentase_model_SVM):
    #         # Buat instance serializer dengan data yang ingin dimasukkan
    #         data = {
    #             'username': username,
    #             'lokasi': lokasi,
    #             'persentase_model_Random_Forest': persentase_model_RF,
    #             'persentase_model_SVM': persentase_model_SVM
    #         }
    #         serializer = HasilPrediksiSerializer(data=data)

    #         # Periksa apakah data valid
    #         if serializer.is_valid():
    #             # Simpan data ke dalam database
    #             serializer.save()
    #             print("Data berhasil dimasukkan ke dalam database.")
    #         else:
    #             # Jika data tidak valid, cetak pesan kesalahan
    #             print("Gagal memasukkan data ke dalam database. Kesalahan:", serializer.errors)

    #     insert_hasil_prediksi_to_database(username, max_svm_prediction, persentase_max_rf_prediction, persentase_max_svm_prediction)

    #     # Buat respons
    #     response = {
    #         "Username": username,
    #         "SVM Percentage": persentase_SVM,
    #         "Max SVM Prediction": {"Value": max_svm_prediction, "Percentage": persentase_max_svm_prediction},
    #         "RF Percentage": persentase_RF,
    #         "Max RF Prediction": {"Value": max_rf_prediction, "Percentage": persentase_max_rf_prediction},
    #         # "Background Data": background_data
    #     }
    #     return Response(data=data, status=status.HTTP_200_OK)
    
    # def check_different_values(self, data):
    #     # Jika tidak ada data, tidak ada nilai yang berbeda
    #     if not data:
    #         return False

    #     # Ambil nilai dari kolom pertama
    #     first_column_values = [item['username'] for item in data]

    #     # Jika ada nilai yang berbeda dalam data kolom pertama, return True
    #     if len(set(first_column_values)) > 1:
    #         return True

    #     return False

    
