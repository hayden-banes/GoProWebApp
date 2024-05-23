from django.urls import path

from . import views

app_name = "controller"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:timelapse_id>/", views.detail, name="detail"),
    path("gopro/start/<str:gopro_id>/", views.gopro_start, name="gopro_start"),
    path("gopro/stop/<str:gopro_id>/", views.gopro_stop, name="gopro_stop"),
    # path("connect/", views.ConnectView.as_view(), name="connectview"),
    path("timelapse/start/", views.timelapse_start, name="timelapse_start"),
    path("timelapse/stop/", views.timelapse_stop, name="timelapse_stop"),
    path("connect/", views.connect, name="connect"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("settings/", views.SettingsView.as_view(), name="settings"),
    path("admin/", views.AdminView.as_view(), name="admin")
]