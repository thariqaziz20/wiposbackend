from django.urls import path
from . import views



urlpatterns = [
    path('', views.DataWiPosListCreateView.as_view(), name="post_home"),
    # path('create/', views.createDataWiPos),
    path('<str:pk>/', views.PostRetrieveUpdateDeleteView.as_view(), name="post_detail"),
]
