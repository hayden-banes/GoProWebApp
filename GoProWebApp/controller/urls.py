from django.urls import path

from . import views

app_name = "controller"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:timelapse_id>/", views.detail, name="detail"),
    path("gopro/start/<str:gopro_id>/", views.gopro_start, name="gopro_start"),
    path("gopro/stop/<str:gopro_id>/", views.gopro_stop, name="gopro_stop"),
    path("timelapse/start/<str:gopro_id>/", views.timelapse_start, name="timelapse_start"),
    path("timelapse/stop/<str:gopro_id>/", views.timelapse_stop, name="timelapse_stop"),
    path("connect/<str:gopro_id>/", views.connect, name="connect"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("connect/", views.ConnectView.as_view(), name="connectview")
]