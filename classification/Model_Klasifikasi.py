import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from .models import ModelWithPickle

def ModelKlasifikasi(username, data):
    try:
        name = username
        df = pd.DataFrame(data)
        X1 = df["mackonversi"]
        X2 = df["rssi"]
        y = df["lokasi"]
        X = np.column_stack((X1, X2))
        y = np.array(y)

        # SVM GridSearch Parameter
        x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)
        param_grid = {'C': [0.1, 1, 10, 100],
                      'gamma': [1, 0.1, 0.01, 0.001],
                      'kernel': ['rbf']}
        svc = SVC()
        grid_svc = GridSearchCV(svc, param_grid, refit=True, verbose=3)
        grid_svc.fit(x_train, y_train)

        # Random Forest GridSearch Parameter
        param_grid_rf = {
            'n_estimators': [10, 50, 100],
            'max_depth': [None, 10, 20, 30],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        rf = RandomForestClassifier()
        grid_rf = GridSearchCV(rf, param_grid_rf, cv=5, n_jobs=-1, verbose=2)
        grid_rf.fit(x_train, y_train)

        y_pred_svm = grid_svc.predict(x_test)
        y_pred_rf = grid_rf.predict(x_test)

        akurasi_SVM = round(accuracy_score(y_pred_svm, y_test) * 100, 2)
        akurasi_RF = round(accuracy_score(y_pred_rf, y_test) * 100, 2)

        # Mengonversi model menjadi bentuk biner sebelum menyimpannya
        svm_model_bytes = pickle.dumps(grid_svc.best_estimator_)
        rf_model_bytes = pickle.dumps(grid_rf.best_estimator_)

        # Simpan model dalam satu baris dengan komposisi kolom yang tepat
        model_instance, created = ModelWithPickle.objects.update_or_create(
            username=name,
            defaults={'svm_model': svm_model_bytes, 'rf_model': rf_model_bytes}
        )

        status = "Updated" if not created else "Created"
        print(f"{status} model for user '{name}' successfully.")
        return(akurasi_SVM, akurasi_RF, status)
    
    except Exception as e:
        print(f"Error: {e}")
        return None, None, f"Error: " + str(e)
