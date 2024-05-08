from django.urls import path

from . import views

app_name = "controller"
urlpatterns = [
    path("", views.index, name="index"),
    path("<int:timelapse_id>/", views.detail, name="detail"),
    path("start/<str:gopro_id>/", views.start, name="start"),
    path("stop/<str:gopro_id>/", views.stop, name="stop"),
    path("home/", views.HomeView.as_view(), name="home"),
    path("connect/", views.ConnectView.as_view(), name="connect")
]