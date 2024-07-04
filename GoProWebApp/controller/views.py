import asyncio

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from django.views.generic.edit import FormView

import threading
from threading import Thread, Event
from time import sleep

from .models import *
from .forms import ConnectForm

TEMP_DIR = 'controller/'
GOPRO_ID = 4933

# Create your views here.


def index(request):
    timelapse_list = Timelapse.objects.all()
    return render(request, "controller/index.html", {"timelapse_list": timelapse_list})


def detail(request, timelapse_id):
    timelapse = get_object_or_404(Timelapse, pk=timelapse_id)
    return render(request, "controller/detail.html", {"item": timelapse})


def gopro_start(request):
    gopro = get_object_or_404(GoPro, identifier=GOPRO_ID)
    gopro.start()
    return HttpResponse("Started")


def gopro_stop(request):
    gopro = get_object_or_404(GoPro, identifier=GOPRO_ID)
    gopro.stop()
    return HttpResponse("Stopped")


def timelapse_start(request):
    timelapse = get_object_or_404(
        Timelapse, gopro=GoPro.objects.get(identifier=GOPRO_ID))
    timelapse.start()
    print("Timelapse started")
    return redirect('controller:home')


def timelapse_stop(request):
    timelapse = get_object_or_404(
        Timelapse, gopro=GoPro.objects.get(identifier=GOPRO_ID))
    timelapse.stop()
    print("Timelapse stopped")
    return redirect('controller:home')


def connect(request):
    gopro = get_object_or_404(GoPro, identifier=GOPRO_ID)
    gopro.start()
    print("Connecting")
    return redirect('controller:home')


class HomeView(View):
    template_path = TEMP_DIR + 'home.html'

    def get(self, request):
        gopro = GoPro.objects.get(identifier=GOPRO_ID)
        status = gopro.get_status()
        timelapse = get_object_or_404(Timelapse, gopro=gopro)
        image_list = Image.objects.order_by("-date_time")[:20]

        timelapse_action = 'stop' if timelapse.task_signal else 'start'
        # image_list =
        return render(
					request, 
					self.template_path, 
					{
						"gopro": gopro, 
						"status": status, 
						"timelapse_action": timelapse_action,
            "image_list": image_list
					}
				)


class SettingsView(View):
    template_path = TEMP_DIR + "settings.html"

    def get(self, request):
        return render(request, self.template_path)


class AdminView(View):
    template_path = TEMP_DIR + "admin.html"

    def get(self, request):
        return render(request, self.template_path)

# Start/Stop
# class ConnectView(FormView):
#     template_name = "controller/connect.html"
#     form_class = ConnectForm

#     def form_valid(self, form):
#         identifier = form.cleaned_data['identifier']
#         gopro, created = GoPro.objects.get_or_create(identifier=identifier)
#         print(f"view alive? {gopro.is_alive()}")
#         if gopro.is_alive():
#             gopro.stop()
#             print(f"view alive after stopping? {gopro.is_alive()}")
#         else:
#             gopro.start()
#             print(f"view alive after starting? {gopro.is_alive()}")
#         return render(self.request, 'controller/detail.html', {'item': gopro})

    # def get(self, request):
    #     return render(request, self.template_name, {"form":self.form})

    # def post(self, request):
    #     form = ConnectForm(request.POST)
    #     print(form)
    #     if form.is_valid():
    #         gopro = GoPro.objects.get(identifier = form.cleaned_data["identifier"])
    #         t: Thread = GoProObj.get_keep_alive_thread(gopro.identifier)
    #         return HttpResponse(str(t.ident))

    #     return HttpResponse(form.errors)
